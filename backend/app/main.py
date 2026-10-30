from __future__ import annotations

import base64
import io
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .agents.profiler import profile_resume
from .agents.state import AgentState
from .config import integration_status, settings
from .integrations.errors import IntegrationError, IntegrationNotConfigured
from .integrations.embeddings import get_embedding_provider
from .integrations.groq_client import get_groq_client
from .integrations.freehire import fetch_csv_jobs, load_configured_freehire
from .integrations.myscheme import fetch_myscheme
from .learning import default_model_path, load_runtime_ranker
from .recommendation import build_feed, explain_item
from .runtime import create_store
from .schemas import ConnectCreate, ImpressionBatchCreate, IngestJobsCreate, InteractionCreate, ShareCreate, StartupApply, StartupCreate, UserUpdate


app = FastAPI(
    title="Bharat Career Twin API",
    version="0.1.0",
    description="A transparent, steerable career network with LangGraph/Groq/Supabase integrations and local fallbacks.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = create_store()


def current_user_id(
    x_demo_user: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
    user_id: str | None = Query(default=None),
) -> str:
    """Resolve a Supabase Auth user in production or a seeded demo user locally."""

    if settings.store_backend == "supabase":
        token = authorization.removeprefix("Bearer ").strip() if authorization else ""
        if not token or token == "undefined":
            raise HTTPException(status_code=401, detail={"code": "auth_required", "message": "Bearer Supabase access token required."})
        try:
            return store.resolve_auth_user(token)
        except IntegrationError as exc:
            raise HTTPException(status_code=401, detail={"code": "invalid_token", "message": str(exc)}) from exc

    candidate = x_demo_user or user_id or ""
    if not candidate and authorization:
        token = authorization.removeprefix("Bearer ").strip()
        if token and token != "undefined":
            candidate = token
    candidate = candidate or "demo_fresher"
    try:
        store.get_user(candidate)
    except KeyError as exc:
        raise HTTPException(status_code=401, detail={"code": "unknown_demo_user", "message": "Use demo_fresher, demo_govt, or demo_founder."}) from exc
    return candidate


def api_error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": message, "code": code})


def require_admin(
    user_id: str = Depends(current_user_id),
    admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
) -> str:
    if settings.admin_token and admin_token != settings.admin_token:
        raise HTTPException(status_code=403, detail={"code": "admin_required", "message": "Valid X-Admin-Token required."})
    return user_id


def _auth_payload(response: Any) -> dict[str, Any]:
    user = getattr(response, "user", None)
    session = getattr(response, "session", None)
    if isinstance(response, dict):
        user = response.get("user", user)
        session = response.get("session", session)
    def plain(value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool, list, dict)):
            if isinstance(value, list):
                return [plain(item) for item in value]
            if isinstance(value, dict):
                return {key: plain(item) for key, item in value.items()}
            return value
        if hasattr(value, "model_dump"):
            return value.model_dump()
        if hasattr(value, "__dict__"):
            return {key: plain(item) for key, item in vars(value).items() if not key.startswith("_")}
        return str(value)
    return {"user": plain(user), "session": plain(session)}


def _extract_pdf_text(content: bytes) -> tuple[str, str]:
    """Extract text when PyMuPDF is available, otherwise use a safe fallback."""

    try:
        try:
            import pymupdf  # type: ignore

            document = pymupdf.open(stream=content, filetype="pdf")
        except ImportError:
            import fitz  # type: ignore

            document = fitz.open(stream=content, filetype="pdf")
        return "\n".join(str(page.get_text()) for page in document).strip(), "pymupdf"
    except Exception:
        # A scanned/image PDF or a minimal environment should not crash the
        # onboarding flow. The profiler will return the editable manual state.
        decoded = content.decode("utf-8", errors="ignore")
        decoded = re.sub(r"[^\x09\x0a\x0d\x20-\x7e]", " ", decoded)
        return re.sub(r"\s+", " ", decoded).strip(), "local-fallback"


def _item_detail(item: dict[str, Any]) -> dict[str, Any]:
    detail = dict(item)
    if "fresh_hours" in detail:
        detail["posted_ago"] = _posted_ago(detail["fresh_hours"])
    if detail.get("type") == "scheme":
        detail["eligibility_score"] = _eligibility_score(detail)
    return detail


def _posted_ago(hours: float | int | None) -> str:
    value = float(hours or 0)
    if value < 1:
        return "just now"
    if value < 24:
        return f"{int(value)}h ago"
    return f"{int(value / 24)}d ago"


def _eligibility_score(scheme: dict[str, Any], user: dict[str, Any] | None = None) -> int:
    eligibility = scheme.get("eligibility") or {}
    if not eligibility:
        return 0
    values = [bool(value) for value in eligibility.values()]
    return round(sum(values) / len(values) * 100)


@app.get("/health", tags=["system"])
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "bharat-career-twin", "mode": settings.store_backend, "integrations": integration_status(), "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/users/me", tags=["auth"])
def get_me(user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    return {"user": store.get_user(user_id), "memory": store.get_memory(user_id)}


@app.patch("/api/users/me", tags=["auth"])
def update_me(payload: UserUpdate, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    updates = payload.model_dump(exclude_none=True)
    return {"user": store.save_user(user_id, **updates), "memory": store.get_memory(user_id)}


@app.post("/api/auth/signup", tags=["auth"])
def signup(payload: dict[str, Any]) -> dict[str, Any]:
    email = str(payload.get("email") or "").strip()
    if not email:
        raise HTTPException(status_code=422, detail={"code": "email_required", "message": "email is required"})
    if settings.store_backend == "supabase":
        password = str(payload.get("password") or "")
        if len(password) < 8:
            raise HTTPException(status_code=422, detail={"code": "password_required", "message": "password must be at least 8 characters"})
        response = store.client.auth.sign_up({"email": email, "password": password, "options": {"data": {"full_name": payload.get("full_name") or "New builder"}}})
        return _auth_payload(response)
    return {"user": {"id": f"local-{secrets.token_hex(5)}", "email": email, "full_name": payload.get("full_name") or "New builder"}, "session": {"access_token": "local-demo-token", "provider": "supabase-placeholder"}}


@app.post("/api/auth/login", tags=["auth"])
def login(payload: dict[str, Any]) -> dict[str, Any]:
    email = str(payload.get("email") or "").strip()
    if settings.store_backend == "supabase":
        password = str(payload.get("password") or "")
        if not password:
            raise HTTPException(status_code=422, detail={"code": "password_required", "message": "password is required"})
        response = store.client.auth.sign_in_with_password({"email": email, "password": password})
        return _auth_payload(response)
    demo = next((user for user in (store.get_user("demo_fresher"), store.get_user("demo_govt"), store.get_user("demo_founder")) if user["email"] == email), None)
    if not demo:
        raise HTTPException(status_code=401, detail={"code": "local_demo_only", "message": "Use one of the seeded demo emails in local mode."})
    return {"user": demo, "session": {"access_token": demo["id"], "provider": "local-demo"}}


@app.post("/api/resume/parse", tags=["resume"])
async def parse_resume(file: UploadFile = File(...), user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail={"code": "resume_too_large", "message": "Resume must be 5MB or smaller."})
    raw_text, parser = _extract_pdf_text(content)
    state = AgentState(user_id=user_id, user=store.get_user(user_id))
    profile_resume(state, raw_text=raw_text)
    resume_json = state.resume_json or {}
    embedding = None
    provider = get_embedding_provider()
    if provider.available:
        try:
            embedding = provider.embed_text(" ".join([*(resume_json.get("skills") or []), *(resume_json.get("interests") or [])]))
        except Exception:
            embedding = None
    store.save_user(user_id, resume_json=resume_json, ats_score=resume_json.get("ats_score", 68), skills=resume_json.get("skills", []), interest_embedding=embedding)
    return {
        "resume_json": resume_json,
        "ats_score": resume_json.get("ats_score", 68),
        "strengths": resume_json.get("strengths", []),
        "gaps": resume_json.get("gaps", []),
        "suggestions": resume_json.get("suggestions", []),
        "interest_embedding": embedding,
        "parser": parser,
        "agent_trace": state.agent_trace,
        "manual_review_required": not bool(raw_text),
    }


@app.get("/api/resume/analysis", tags=["resume"])
def resume_analysis(user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    user = store.get_user(user_id)
    return {"resume_json": user.get("resume_json"), "ats_score": user.get("ats_score", 68), "strengths": (user.get("resume_json") or {}).get("strengths", []), "gaps": (user.get("resume_json") or {}).get("gaps", [])}


@app.post("/api/resume/improve", tags=["resume"])
def improve_resume(job_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"code": "job_not_found", "message": "Job not found"})
    user = store.get_user(user_id)
    skills = ", ".join(user.get("skills", [])[:4]) or "product building"
    cover_letter = None
    groq = get_groq_client()
    if groq:
        try:
            generated = groq.json_completion(
                "You are a concise career coach. Return JSON with one cover_letter string. Ground it only in the supplied user skills and job details; do not invent employers, metrics, or credentials.",
                f"Candidate: {user.get('full_name', 'builder')}\nCity: {user.get('city', 'India')}\nSkills: {skills}\nJob: {job['title']} at {job['company']}\nDescription: {job.get('description', '')}",
                temperature=0.2,
                max_tokens=500,
            )
            cover_letter = generated.get("cover_letter")
        except Exception:
            cover_letter = None
    cover_letter = cover_letter or f"Hi team — I’m {user.get('full_name', 'a builder')}, a {skills} practitioner from {user.get('city', 'India')}. I’m excited about {job['title']} at {job['company']} because the role connects practical craft with useful outcomes. I’d love to share how I can contribute and keep growing into the next version of the work."
    return {"job_id": job_id, "cover_letter": cover_letter, "grounded_in": {"skills": user.get("skills", []), "company": job["company"], "title": job["title"]}}


@app.get("/api/feed", tags=["feed"])
def feed(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=50),
    type: str = Query(default="all"),
    steer: str | None = Query(default=None),
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    result = build_feed(store, user_id, offset=offset, limit=limit, item_type=type, steer=steer)
    result["items"] = [_item_detail(item) for item in result["items"]]
    return result


@app.post("/api/interactions", tags=["feed"])
def interaction(payload: InteractionCreate, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    return {"interaction": store.add_interaction(user_id, **payload.model_dump()), "memory_updated": payload.action in {"like", "save", "hide", "apply"}}


@app.post("/api/impressions", tags=["feed"])
def impressions(payload: ImpressionBatchCreate, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    rows = store.add_impressions(user_id, [item.model_dump() for item in payload.impressions])
    return {"recorded": len(rows), "impressions": rows}


@app.get("/api/model/status", tags=["model"])
def model_status(user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    model = load_runtime_ranker()
    if not model:
        return {"available": False, "backend": "hybrid-rules", "model_version": "rules-v1", "model_path": str(default_model_path()), "metrics": {}}
    return {
        "available": True,
        "backend": "learned-logistic+guardrails",
        "model_version": model.model_version,
        "model_path": str(default_model_path()),
        "trained_examples": model.trained_examples,
        "metrics": model.metrics or {},
        "features": list(model.feature_names),
    }


@app.get("/api/jobs/recent", tags=["jobs"])
def recent_jobs(days: int = Query(default=1, ge=1, le=30), user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    threshold = days * 24
    jobs = [job for job in store.list_jobs() if job["fresh_hours"] <= threshold]
    return {"jobs": [_item_detail(job) for job in jobs], "days": days}


@app.get("/api/jobs/sources", tags=["jobs"])
def job_sources(user_id: str = Depends(current_user_id)) -> dict[str, int]:
    return store.source_counts()


@app.get("/api/jobs/{job_id}", tags=["jobs"])
def job_detail(job_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"code": "job_not_found", "message": "Job not found"})
    try:
        explanation = explain_item(store, user_id, job_id, "job")
    except KeyError:
        explanation = {"breakdown": {}, "why": [], "gap_info": {}}
    return {"job": _item_detail(job), **explanation}


@app.post("/api/sync/freehire", tags=["admin"])
def sync_freehire(user_id: str = Depends(require_admin)) -> dict[str, Any]:
    if settings.store_backend == "sqlite" and not settings.freehire_json_url and not settings.freehire_database_url and not settings.freehire_api_url:
        return {"inserted": 0, "updated": 0, "source": "freehire", "mode": "local-demo", "message": "Set FREEHIRE_JSON_URL, FREEHIRE_DATABASE_URL, or use the public API to sync external jobs."}
    try:
        postings = load_configured_freehire()
        inserted, updated = store.upsert_freehire_jobs(postings)
        return {"inserted": inserted, "updated": updated, "source": "freehire", "mode": settings.store_backend, "fetched": len(postings)}
    except IntegrationError as exc:
        raise HTTPException(status_code=502, detail={"code": "freehire_sync_failed", "message": str(exc)}) from exc


@app.post("/api/ingest/jobs", tags=["admin"])
def ingest_jobs(payload: IngestJobsCreate, user_id: str = Depends(require_admin)) -> dict[str, Any]:
    try:
        postings = fetch_csv_jobs(payload.csv_url)
        inserted, updated = store.upsert_kaggle_jobs(postings)
        return {"inserted": inserted, "updated": updated, "source": "kaggle_india", "fetched": len(postings), "mode": settings.store_backend}
    except (IntegrationError, OSError) as exc:
        raise HTTPException(status_code=502, detail={"code": "jobs_ingest_failed", "message": str(exc)}) from exc


@app.post("/api/ingest/schemes", tags=["admin"])
def ingest_schemes(user_id: str = Depends(require_admin)) -> dict[str, Any]:
    try:
        schemes = fetch_myscheme()
        inserted, updated = store.upsert_schemes(schemes)
        return {"inserted": inserted, "updated": updated, "source": "myscheme", "fetched": len(schemes), "mode": settings.store_backend}
    except IntegrationError as exc:
        raise HTTPException(status_code=502, detail={"code": "scheme_ingest_failed", "message": str(exc)}) from exc


@app.get("/api/schemes", tags=["schemes"])
def schemes(eligible_only: bool = Query(default=False), user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    items = store.list_schemes()
    if eligible_only:
        items = [item for item in items if _eligibility_score(item) >= 75]
    return {"schemes": [{**item, "eligibility_score": _eligibility_score(item)} for item in items]}


@app.get("/api/schemes/{scheme_id}", tags=["schemes"])
def scheme_detail(scheme_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    scheme = store.get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail={"code": "scheme_not_found", "message": "Scheme not found"})
    return {"scheme": {**scheme, "eligibility_score": _eligibility_score(scheme)}, "explanation": "Eligibility is a guide; verify the official application requirements before submitting."}


@app.get("/api/peers/nearby", tags=["social"])
def nearby_peers(skill: str | None = None, city: str | None = None, radius: float = Query(default=20, ge=1, le=100), limit: int = Query(default=20, ge=1, le=50), user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    normalized_skill = (skill or "").lower()
    normalized_city = (city or "").lower()
    try:
        peer_pool = store.list_peers(user_id)
    except TypeError:
        peer_pool = store.list_peers()
    items = [peer for peer in peer_pool if peer["distance_km"] <= radius and (not normalized_skill or normalized_skill in " ".join(peer["skills"] + peer["interests"]).lower()) and (not normalized_city or normalized_city in peer["city"].lower())]
    return {"peers": items[:limit], "radius": radius, "city": city, "skill": skill}


@app.get("/api/peers/referral-path", tags=["social"])
def referral_path(job_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"code": "job_not_found", "message": "Job not found"})
    company = job["company"]
    path = None
    if hasattr(store, "find_referral_path"):
        try:
            path = store.find_referral_path(user_id, job)
        except Exception:
            path = None
    if path:
        pass
    elif company == "TCS":
        path = [{"user_id": user_id, "name": "You", "relation": "self"}, {"user_id": "p1", "name": "Priya Sharma", "relation": "mutual · 1 hop"}, {"user_id": "tcs-hiring", "name": "Aman · TCS hiring", "relation": "company · 2 hops"}]
    else:
        path = [{"user_id": user_id, "name": "You", "relation": "self"}, {"user_id": "p3", "name": "Rohit Gupta", "relation": "mutual · 1 hop"}, {"user_id": "company-hiring", "name": f"Hiring team · {company}", "relation": "company · 2 hops"}]
    hinglish = f"Hi {path[1]['name'].split()[0]} — Sudipta here. {company} ka role explore kar raha hoon. Would you be open to a quick referral if the profile feels relevant?"
    english = f"Hi {path[1]['name'].split()[0]} — I’m exploring the {job['title']} role at {company}. Would you be open to a quick referral if the profile feels relevant?"
    request_id = store.add_referral_request(user_id, path[1]["user_id"], job_id, hinglish, english)
    return {"job_id": job_id, "path": path, "draft_hinglish": hinglish, "draft_english": english, "request_id": request_id}


@app.post("/api/peers/connect", tags=["social"])
def connect_peer(payload: ConnectCreate, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    peer = store.get_peer(payload.peer_id)
    if not peer:
        raise HTTPException(status_code=404, detail={"code": "peer_not_found", "message": "Peer not found"})
    store.set_memory(user_id, f"connect:{payload.peer_id}", {"message": payload.message, "created_at": datetime.now(timezone.utc).isoformat()})
    return {"status": "sent", "peer": peer, "message": payload.message}


@app.get("/api/graph/ego", tags=["social"])
def ego_graph(user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    peers = store.list_peers()
    nodes = [{"id": user_id, "label": "You", "type": "user"}] + [{"id": peer["id"], "label": peer["name"], "type": "peer", "color": peer["color"]} for peer in peers]
    edges = [{"source": user_id, "target": peer["id"], "weight": peer["mutual_count"]} for peer in peers]
    return {"nodes": nodes, "edges": edges}


@app.post("/api/startups", tags=["startups"])
def create_startup(payload: StartupCreate, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    startup = store.create_startup(user_id, payload.title, payload.description, payload.category, payload.skills_needed, payload.location_city)
    return {"startup": startup}


@app.get("/api/startups", tags=["startups"])
def startups(my_match: bool = Query(default=True), category: str | None = None, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    items = store.list_startups()
    if category:
        items = [item for item in items if item["category"].lower() == category.lower()]
    return {"startups": items, "my_match": my_match}


@app.get("/api/startups/{startup_id}", tags=["startups"])
def startup_detail(startup_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    startup = store.get_startup(startup_id)
    if not startup:
        raise HTTPException(status_code=404, detail={"code": "startup_not_found", "message": "Startup idea not found"})
    return {"startup": startup, "applicants": []}


@app.post("/api/startups/{startup_id}/apply", tags=["startups"])
def apply_startup(startup_id: str, payload: StartupApply, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    if not store.get_startup(startup_id):
        raise HTTPException(status_code=404, detail={"code": "startup_not_found", "message": "Startup idea not found"})
    return {"application": store.add_startup_application(startup_id, user_id, payload.message, payload.skill_offer)}


@app.get("/api/startups/{startup_id}/applicants", tags=["startups"])
def startup_applicants(startup_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    if not store.get_startup(startup_id):
        raise HTTPException(status_code=404, detail={"code": "startup_not_found", "message": "Startup idea not found"})
    return {"applicants": []}


@app.get("/api/recent", tags=["feed"])
def recent(user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    jobs = [item for item in store.list_jobs() if item["fresh_hours"] <= 24]
    schemes = [item for item in store.list_schemes() if item["id"] in {"s1", "s4", "s6"}]
    startups = store.list_startups()[:3]
    return {"jobs": [_item_detail(item) for item in jobs], "schemes": schemes, "startups": startups}


@app.get("/api/notifications", tags=["notifications"])
def notifications(unread_only: bool = Query(default=True), user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    items = store.list_notifications(user_id, unread_only=unread_only)
    return {"notifications": items, "unread_count": len([item for item in store.list_notifications(user_id, unread_only=True)])}


@app.post("/api/notifications/{notification_id}/read", tags=["notifications"])
def mark_notification_read(notification_id: int, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    store.mark_notification_read(notification_id)
    return {"id": notification_id, "read": True}


@app.post("/api/share/qr", tags=["share"])
def share_qr(payload: ShareCreate, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    share_link = f"https://bharatcareertwin.local/{payload.item_type}/{payload.item_id}"
    return {"qr_url": share_link, "share_link": share_link, "item_type": payload.item_type, "item_id": payload.item_id, "format": "client-generated-qr"}


@app.get("/api/stats", tags=["admin"])
def stats(user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    counts = store.source_counts()
    model = load_runtime_ranker()
    impressions = store.list_impressions(limit=100000) if hasattr(store, "list_impressions") else []
    interactions = store.list_interactions(user_id, limit=100000)
    positive = sum(1 for row in interactions if row.get("action") in {"view", "like", "save", "apply", "share"})
    return {
        "users": 3,
        "jobs_by_source": counts,
        "impressions": len(impressions),
        "interactions": len(interactions),
        "ctr": round(positive / max(1, len(impressions)), 4),
        "popular_skills": ["React", "Python", "SQL", "Docker"],
        "model": {
            "available": bool(model),
            "backend": "learned-logistic+guardrails" if model else "hybrid-rules",
            "model_version": model.model_version if model else "rules-v1",
            "metrics": model.metrics if model else {},
        },
    }


@app.exception_handler(KeyError)
async def key_error_handler(request: Any, exc: KeyError) -> JSONResponse:
    return api_error(404, "not_found", f"Resource not found: {exc.args[0] if exc.args else 'unknown'}")
