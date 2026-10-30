from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from ..config import settings
from .embeddings import get_embedding_provider
from .errors import IntegrationNotConfigured, IntegrationResponseError


def _data(response: Any) -> list[dict[str, Any]]:
    value = getattr(response, "data", response)
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return datetime.now(timezone.utc)


def _fresh_hours(value: Any) -> float:
    return max(0.0, (datetime.now(timezone.utc) - _parse_dt(value)).total_seconds() / 3600)


def _uuid_or_deterministic(value: Any, namespace: str) -> str:
    try:
        return str(UUID(str(value)))
    except (TypeError, ValueError, AttributeError):
        return str(uuid5(NAMESPACE_URL, f"{namespace}:{value}"))


class SupabaseStore:
    """Supabase/Postgres repository implementing the local Store contract."""

    def __init__(self) -> None:
        if not settings.supabase_url or not settings.supabase_key:
            raise IntegrationNotConfigured("Set SUPABASE_URL and SUPABASE_SECRET_KEY/SUPABASE_SERVICE_ROLE_KEY.")
        try:
            from supabase import create_client
        except ImportError as exc:  # pragma: no cover - depends on real install
            raise IntegrationNotConfigured("Install the supabase package for the real store backend.") from exc
        self.client = create_client(settings.supabase_url, settings.supabase_key)
        self.last_vector_error: str | None = None

    def _rows(self, table: str, *, user_id: str | None = None, order: str | None = None) -> list[dict[str, Any]]:
        query = self.client.table(table).select("*")
        if user_id:
            query = query.eq("user_id", user_id)
        if order:
            query = query.order(order, desc=True)
        return _data(query.execute())

    def _one(self, table: str, record_id: str) -> dict[str, Any] | None:
        rows = _data(self.client.table(table).select("*").eq("id", record_id).limit(1).execute())
        return rows[0] if rows else None

    def resolve_auth_user(self, token: str) -> str:
        try:
            response = self.client.auth.get_user(token)
            auth_user = getattr(response, "user", None)
            if auth_user is None and isinstance(response, dict):
                auth_user = response.get("user")
            user_id = getattr(auth_user, "id", None) or (auth_user or {}).get("id")
            if not user_id:
                raise IntegrationResponseError("Supabase Auth did not return a user id.")
            if isinstance(auth_user, dict):
                email = auth_user.get("email")
                metadata = auth_user.get("user_metadata", {}) or {}
            else:
                email = getattr(auth_user, "email", None)
                metadata = getattr(auth_user, "user_metadata", {}) or {}
        except Exception as exc:
            raise IntegrationResponseError(f"Supabase Auth verification failed: {exc}") from exc
        try:
            self.get_user(str(user_id))
        except KeyError:
            self.client.table("users").insert({"id": str(user_id), "email": email, "full_name": metadata.get("full_name") or email or "Builder"}).execute()
        return str(user_id)

    def get_user(self, user_id: str) -> dict[str, Any]:
        row = self._one("users", user_id)
        if not row:
            raise KeyError(user_id)
        interests = _data(self.client.table("user_interests").select("tag,weight").eq("user_id", user_id).execute())
        hates = _data(self.client.table("user_hates").select("tag,weight").eq("user_id", user_id).execute())
        return {
            "id": row.get("id"),
            "email": row.get("email"),
            "full_name": row.get("full_name") or "Builder",
            "city": row.get("city"),
            "state": row.get("state"),
            "experience_level": row.get("experience_level"),
            "skills": row.get("skills") or [],
            "interests": [item.get("tag") for item in interests if item.get("tag")],
            "hates": [item.get("tag") for item in hates if item.get("tag")],
            "education": row.get("education"),
            "resume_json": row.get("resume_json"),
            "ats_score": row.get("ats_score", 68),
            "lat": row.get("lat"),
            "lng": row.get("lng"),
        }

    def _replace_tags(self, table: str, user_id: str, values: list[str]) -> None:
        self.client.table(table).delete().eq("user_id", user_id).execute()
        if values:
            self.client.table(table).insert([{"user_id": user_id, "tag": value, "weight": 1} for value in dict.fromkeys(values)]).execute()

    def save_user(self, user_id: str, **updates: Any) -> dict[str, Any]:
        fields: dict[str, Any] = {}
        for key in ("full_name", "city", "state", "experience_level", "education", "ats_score", "resume_json", "skills", "interest_embedding", "hate_embedding"):
            if key in updates:
                fields[key] = updates[key]
        if fields:
            self.client.table("users").update(fields).eq("id", user_id).execute()
        if "interests" in updates:
            self._replace_tags("user_interests", user_id, updates["interests"])
        if "hates" in updates:
            self._replace_tags("user_hates", user_id, updates["hates"])
        return self.get_user(user_id)

    @staticmethod
    def _job(row: dict[str, Any]) -> dict[str, Any]:
        return {**row, "location": row.get("location_city") or row.get("location") or "Remote", "salary": row.get("salary_text") or row.get("salary") or "Not listed", "likes": row.get("likes_count", 0), "saves": row.get("saves_count", 0), "fresh_hours": _fresh_hours(row.get("posted_at")), "type": "job"}

    @staticmethod
    def _scheme(row: dict[str, Any]) -> dict[str, Any]:
        return {**row, "name": row.get("scheme_name") or row.get("name"), "benefit": row.get("benefits") or row.get("benefit"), "eligibility": row.get("eligibility_json") or row.get("eligibility") or {}, "type": "scheme"}

    @staticmethod
    def _peer(row: dict[str, Any], distance_km: float = 0) -> dict[str, Any]:
        return {"id": row.get("id"), "name": row.get("full_name") or "Builder", "city": row.get("city") or "India", "distance_km": distance_km, "role": row.get("experience_level") or "Builder", "skills": row.get("skills") or [], "interests": [], "mutual_count": 0, "color": "#5076a8", "type": "peer"}

    @staticmethod
    def _distance_km(left: dict[str, Any], right: dict[str, Any]) -> float:
        if left.get("lat") is None or left.get("lng") is None or right.get("lat") is None or right.get("lng") is None:
            return 0.0
        lat1, lon1, lat2, lon2 = map(float, (left["lat"], left["lng"], right["lat"], right["lng"]))
        radius = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        return radius * 2 * math.asin(math.sqrt(a))

    @staticmethod
    def _startup(row: dict[str, Any]) -> dict[str, Any]:
        return {**row, "owner": row.get("owner_id") or "Builder", "title": row.get("title"), "description": row.get("description"), "category": row.get("category"), "skills": row.get("skills_needed") or [], "match_score": row.get("match_score", 0.5), "likes": row.get("likes_count", 0), "type": "startup"}

    def list_jobs(self) -> list[dict[str, Any]]:
        return [self._job(row) for row in self._rows("jobs", order="posted_at")]

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        row = self._one("jobs", job_id)
        return self._job(row) if row else None

    def list_schemes(self) -> list[dict[str, Any]]:
        return [self._scheme(row) for row in self._rows("schemes", order="posted_at")]

    def get_scheme(self, scheme_id: str) -> dict[str, Any] | None:
        row = self._one("schemes", scheme_id)
        return self._scheme(row) if row else None

    def list_peers(self, user_id: str | None = None) -> list[dict[str, Any]]:
        query = self.client.table("users").select("*")
        if user_id:
            query = query.neq("id", user_id)
        rows = _data(query.execute())
        origin = self.get_user(user_id) if user_id else {}
        return [self._peer(row, self._distance_km(origin, row)) for row in rows]

    def get_peer(self, peer_id: str) -> dict[str, Any] | None:
        row = self._one("users", peer_id)
        return self._peer(row) if row else None

    def find_referral_path(self, user_id: str, job: dict[str, Any], max_depth: int = 3) -> list[dict[str, Any]] | None:
        """Bounded BFS over Supabase social_edges to a job-company employee."""

        company = str(job.get("company") or "").strip().lower()
        if not company:
            return None
        edge_rows = _data(self.client.table("social_edges").select("source_user_id,target_user_id").execute())
        adjacency: dict[str, list[str]] = {}
        for edge in edge_rows:
            source = str(edge.get("source_user_id"))
            target = str(edge.get("target_user_id"))
            adjacency.setdefault(source, []).append(target)
        employment_rows = _data(self.client.table("user_employment").select("user_id,company").execute())
        target_ids = {str(row.get("user_id")) for row in employment_rows if str(row.get("company") or "").strip().lower() == company}
        if not target_ids:
            return None
        queue: list[tuple[str, list[str]]] = [(user_id, [user_id])]
        visited = {user_id}
        found: list[str] | None = None
        while queue:
            current, path = queue.pop(0)
            if current in target_ids and current != user_id:
                found = path
                break
            if len(path) - 1 >= max_depth:
                continue
            for neighbor in adjacency.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, [*path, neighbor]))
        if not found:
            return None
        user_rows = _data(self.client.table("users").select("id,full_name").in_("id", found).execute())
        names = {str(row.get("id")): row.get("full_name") or "Builder" for row in user_rows}
        result: list[dict[str, Any]] = []
        for index, node_id in enumerate(found):
            if index == 0:
                relation = "self"
            elif index == len(found) - 1:
                relation = f"company · {index} hops"
            else:
                relation = f"mutual · {index} hops"
            result.append({"user_id": node_id, "name": names.get(node_id, "Hiring team"), "relation": relation})
        return result

    def list_startups(self) -> list[dict[str, Any]]:
        rows = _data(self.client.table("startups").select("*").order("created_at", desc=True).execute())
        return [self._startup(row) for row in rows]

    def get_startup(self, startup_id: str) -> dict[str, Any] | None:
        row = self._one("startups", startup_id)
        return self._startup(row) if row else None

    def _rpc_rows(self, function: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        return _data(self.client.rpc(function, params).execute())

    def candidate_pool(self, user_id: str, query_embedding: list[float] | None = None, limit: int = 200) -> dict[str, list[dict[str, Any]]]:
        if not query_embedding:
            return {"jobs": self.list_jobs(), "schemes": self.list_schemes(), "peers": self.list_peers(user_id), "startups": self.list_startups()}
        try:
            jobs = [self._job(row) for row in self._rpc_rows("match_jobs", {"query_embedding": query_embedding, "match_count": min(100, limit)})]
            schemes = [self._scheme(row) for row in self._rpc_rows("match_schemes", {"query_embedding": query_embedding, "match_count": min(50, limit)})]
            startups = [self._startup(row) for row in self._rpc_rows("match_startups", {"query_embedding": query_embedding, "match_count": min(20, limit)})]
            peers = [self._peer(row) for row in self._rpc_rows("match_users", {"query_embedding": query_embedding, "match_count": min(30, limit), "exclude_user_id": user_id})]
            return {"jobs": jobs, "schemes": schemes, "peers": peers, "startups": startups}
        except Exception as exc:
            self.last_vector_error = str(exc)
            return {"jobs": self.list_jobs(), "schemes": self.list_schemes(), "peers": self.list_peers(user_id), "startups": self.list_startups()}

    def create_startup(self, owner: str, title: str, description: str, category: str, skills: list[str], location_city: str, match_score: float = .78) -> dict[str, Any]:
        payload = {"owner_id": owner, "title": title, "description": description, "category": category, "skills_needed": skills, "location_city": location_city, "likes_count": 0}
        response = _data(self.client.table("startups").insert(payload).execute())
        return self._startup(response[0]) if response else {}

    def add_startup_application(self, startup_id: str, applicant: str, message: str, skills: list[str]) -> dict[str, Any]:
        response = _data(self.client.table("startup_applications").insert({"startup_id": startup_id, "applicant_id": applicant, "message": message, "skill_offer": skills}).execute())
        return response[0] if response else {"startup_id": startup_id, "applicant_id": applicant, "status": "received"}

    def list_interactions(self, user_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        query = self.client.table("interactions").select("*")
        if user_id:
            query = query.eq("user_id", user_id)
        return _data(query.order("created_at", desc=True).limit(limit).execute())

    def add_impressions(self, user_id: str, impressions: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for impression in impressions:
            item_id = str(impression.get("item_id") or "")
            rank_position = int(impression.get("rank_position") or 0)
            if not item_id or rank_position < 1:
                continue
            rows.append({
                "impression_id": str(impression.get("impression_id") or f"imp-{uuid4().hex}"),
                "user_id": user_id,
                "item_id": item_id,
                "item_type": str(impression.get("item_type") or "job"),
                "rank_position": rank_position,
                "candidate_source": str(impression.get("candidate_source") or "feed"),
                "model_version": str(impression.get("model_version") or "rules-v1"),
                "surface": str(impression.get("surface") or "feed"),
                "context": impression.get("context") or {},
            })
        if rows:
            self.client.table("impressions").upsert(rows, on_conflict="impression_id").execute()
        return rows

    def list_impressions(self, user_id: str | None = None, limit: int = 1000) -> list[dict[str, Any]]:
        query = self.client.table("impressions").select("*")
        if user_id:
            query = query.eq("user_id", user_id)
        return _data(query.order("created_at", desc=True).limit(limit).execute())

    def add_interaction(self, user_id: str, item_id: str, item_type: str, action: str, dwell_ms: int = 0, reason: str | None = None) -> dict[str, Any]:
        payload = {"user_id": user_id, "item_id": item_id, "item_type": item_type, "action": action, "dwell_ms": dwell_ms, "reason": reason}
        self.client.table("interactions").insert(payload).execute()
        if item_type == "job" and action in {"like", "save"}:
            field = "likes_count" if action == "like" else "saves_count"
            current = self.get_job(item_id)
            if current:
                self.client.table("jobs").update({field: int(current.get("likes", 0) if field == "likes_count" else current.get("saves", 0)) + 1}).eq("id", item_id).execute()
        if action == "hide" and reason:
            self.client.table("user_hates").upsert({"user_id": user_id, "tag": reason, "weight": 1}, on_conflict="user_id,tag").execute()
        return payload

    def get_memory(self, user_id: str) -> dict[str, Any]:
        rows = _data(self.client.table("agent_memory").select("memory_key,memory_value").eq("user_id", user_id).execute())
        return {row["memory_key"]: row.get("memory_value") for row in rows if row.get("memory_key")}

    def set_memory(self, user_id: str, key: str, value: Any) -> None:
        self.client.table("agent_memory").upsert({"user_id": user_id, "memory_key": key, "memory_value": value}, on_conflict="user_id,memory_key").execute()

    def add_referral_request(self, user_id: str, target_id: str | None, job_id: str | None, hinglish: str, english: str) -> int | str:
        payload = {"requester_id": user_id, "target_user_id": target_id, "job_id": job_id, "draft_hinglish": hinglish, "draft_english": english}
        response = _data(self.client.table("referral_requests").insert(payload).execute())
        return response[0].get("id", "") if response else ""

    def list_notifications(self, user_id: str, unread_only: bool = False) -> list[dict[str, Any]]:
        query = self.client.table("notifications").select("*").eq("user_id", user_id)
        if unread_only:
            query = query.is_("read_at", "null")
        return _data(query.order("created_at", desc=True).execute())

    def mark_notification_read(self, notification_id: int) -> None:
        self.client.table("notifications").update({"read_at": datetime.now(timezone.utc).isoformat()}).eq("id", notification_id).execute()

    def _embedding(self, text: str) -> list[float] | None:
        provider = get_embedding_provider()
        try:
            return provider.embed_text(text)
        except Exception:
            return None

    def upsert_freehire_jobs(self, postings: Iterable[dict[str, Any]]) -> tuple[int, int]:
        rows: list[dict[str, Any]] = []
        inserted = 0
        updated = 0
        for posting in postings:
            freehire_id = str(posting.get("freehire_id") or posting.get("id") or "").strip()
            if not freehire_id:
                continue
            existing = _data(self.client.table("jobs").select("id").eq("freehire_id", freehire_id).limit(1).execute())
            if existing:
                updated += 1
            else:
                inserted += 1
            row = {
                "freehire_id": freehire_id,
                "title": posting.get("title") or "Untitled role",
                "company": posting.get("company") or "Unknown company",
                "location_city": posting.get("location_city") or posting.get("location") or "Remote",
                "location_state": posting.get("location_state") or "",
                "skills": posting.get("skills") or [],
                "description": posting.get("description") or "",
                "salary_text": posting.get("salary") or "Not listed",
                "source": "freehire",
                "source_url": posting.get("source_url") or posting.get("url"),
                "board": posting.get("board"),
                "provider": posting.get("provider") or "freehire",
                "posted_at": posting.get("posted_at") or datetime.now(timezone.utc).isoformat(),
            }
            vector = self._embedding(" ".join([row["title"], row["company"], row["description"], *row["skills"]]))
            if vector:
                row["embedding"] = vector
            rows.append(row)
        if rows:
            self.client.table("jobs").upsert(rows, on_conflict="freehire_id").execute()
        return inserted, updated

    def upsert_kaggle_jobs(self, postings: Iterable[dict[str, Any]]) -> tuple[int, int]:
        rows: list[dict[str, Any]] = []
        for posting in postings:
            row = {
                "id": _uuid_or_deterministic(posting.get("freehire_id") or posting.get("title"), "kaggle-job"),
                "title": posting.get("title") or "Untitled role",
                "company": posting.get("company") or "Unknown company",
                "location_city": posting.get("location") or "India",
                "location_state": posting.get("location_state") or "",
                "skills": posting.get("skills") or [],
                "description": posting.get("description") or "",
                "salary_text": posting.get("salary") or "Not listed",
                "source": "kaggle_india",
                "source_url": posting.get("url"),
                "provider": "kaggle_india",
                "posted_at": posting.get("posted_at") or datetime.now(timezone.utc).isoformat(),
            }
            vector = self._embedding(" ".join([row["title"], row["company"], row["description"], *row["skills"]]))
            if vector:
                row["embedding"] = vector
            rows.append(row)
        if rows:
            self.client.table("jobs").upsert(rows, on_conflict="id").execute()
        return len(rows), 0

    def upsert_schemes(self, schemes: Iterable[dict[str, Any]]) -> tuple[int, int]:
        rows: list[dict[str, Any]] = []
        for scheme in schemes:
            row = {
                "id": _uuid_or_deterministic(scheme.get("id"), "myscheme"),
                "scheme_name": scheme.get("name") or "Government scheme",
                "ministry": scheme.get("ministry"),
                "category": scheme.get("category"),
                "benefits": scheme.get("benefit"),
                "eligibility_json": scheme.get("eligibility") or {},
                "application_url": scheme.get("application_url"),
                "state": scheme.get("state") or "India",
                "posted_at": scheme.get("posted_at") or datetime.now(timezone.utc).isoformat(),
            }
            vector = self._embedding(" ".join([row["scheme_name"], row["ministry"] or "", row["benefits"] or ""]))
            if vector:
                row["embedding"] = vector
            rows.append(row)
        if rows:
            self.client.table("schemes").upsert(rows, on_conflict="id").execute()
        return len(rows), 0

    def source_counts(self) -> dict[str, int]:
        rows = _data(self.client.table("jobs").select("source").execute())
        counts: dict[str, int] = {}
        for row in rows:
            source = row.get("source") or "unknown"
            counts[source] = counts.get(source, 0) + 1
        counts["total"] = sum(counts.values())
        return counts
