from __future__ import annotations

import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now(hours_ago: float = 0) -> str:
    return (utc_now() - timedelta(hours=hours_ago)).isoformat()


def json_load(value: str | None, default: Any) -> Any:
    if value is None:
        return default
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return default


def json_dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class Store:
    """Small SQLite persistence layer used by the local demo.

    The tables mirror the Supabase schema in ``supabase/migrations/01_schema.sql``
    closely enough that the API and agent pipeline can be exercised without
    external credentials. The same repositories can later be swapped for
    Supabase adapters without changing the agent contracts.
    """

    def __init__(self, db_path: str | Path | None = None):
        default_path = Path(__file__).resolve().parents[2] / "data" / "bharat_twin.db"
        configured_path = db_path or os.getenv("BCT_DB_PATH") or default_path
        self.db_path = Path(configured_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def _initialize(self) -> None:
        with self._lock, self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE,
                    full_name TEXT NOT NULL,
                    city TEXT,
                    state TEXT,
                    experience_level TEXT,
                    skills_json TEXT NOT NULL DEFAULT '[]',
                    interests_json TEXT NOT NULL DEFAULT '[]',
                    hates_json TEXT NOT NULL DEFAULT '[]',
                    education TEXT,
                    resume_json TEXT,
                    ats_score INTEGER NOT NULL DEFAULT 68,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    freehire_id TEXT UNIQUE,
                    title TEXT NOT NULL,
                    company TEXT,
                    location_city TEXT,
                    location_state TEXT,
                    skills_json TEXT NOT NULL DEFAULT '[]',
                    description TEXT,
                    salary TEXT,
                    source TEXT NOT NULL DEFAULT 'kaggle_india',
                    source_url TEXT,
                    board TEXT,
                    provider TEXT,
                    posted_at TEXT NOT NULL,
                    likes_count INTEGER NOT NULL DEFAULT 0,
                    saves_count INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS schemes (
                    id TEXT PRIMARY KEY,
                    scheme_name TEXT NOT NULL,
                    ministry TEXT,
                    category TEXT,
                    benefits TEXT,
                    eligibility_json TEXT NOT NULL DEFAULT '{}',
                    application_url TEXT,
                    state TEXT,
                    posted_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS peers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    city TEXT,
                    distance_km REAL NOT NULL DEFAULT 0,
                    role TEXT,
                    skills_json TEXT NOT NULL DEFAULT '[]',
                    interests_json TEXT NOT NULL DEFAULT '[]',
                    mutual_count INTEGER NOT NULL DEFAULT 0,
                    color TEXT
                );

                CREATE TABLE IF NOT EXISTS startups (
                    id TEXT PRIMARY KEY,
                    owner TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT,
                    skills_json TEXT NOT NULL DEFAULT '[]',
                    location_city TEXT,
                    match_score REAL NOT NULL DEFAULT 0.5,
                    likes_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS social_edges (
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    PRIMARY KEY (source_id, target_id)
                );

                CREATE TABLE IF NOT EXISTS user_employment (
                    user_id TEXT NOT NULL,
                    company TEXT NOT NULL,
                    PRIMARY KEY (user_id, company)
                );

                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    action TEXT NOT NULL,
                    dwell_ms INTEGER NOT NULL DEFAULT 0,
                    reason TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS impressions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    impression_id TEXT NOT NULL UNIQUE,
                    user_id TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    rank_position INTEGER NOT NULL,
                    candidate_source TEXT NOT NULL DEFAULT 'feed',
                    model_version TEXT NOT NULL DEFAULT 'rules-v1',
                    surface TEXT NOT NULL DEFAULT 'feed',
                    context_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS agent_memory (
                    user_id TEXT NOT NULL,
                    memory_key TEXT NOT NULL,
                    memory_value_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (user_id, memory_key)
                );

                CREATE TABLE IF NOT EXISTS referral_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    target_id TEXT,
                    job_id TEXT,
                    draft_hinglish TEXT,
                    draft_english TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    read_at TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS jobs_source_idx ON jobs(source);
                CREATE INDEX IF NOT EXISTS jobs_posted_idx ON jobs(posted_at DESC);
                CREATE INDEX IF NOT EXISTS interactions_user_idx ON interactions(user_id, created_at DESC);
                 CREATE INDEX IF NOT EXISTS impressions_user_idx ON impressions(user_id, created_at DESC);
                """
            )
            self._seed_if_empty(connection)

    def _seed_if_empty(self, connection: sqlite3.Connection) -> None:
        if connection.execute("SELECT 1 FROM users LIMIT 1").fetchone():
            return

        now = iso_now()
        users = [
            ("demo_fresher", "fresher@bharat.twin", "Sudipta Samanta", "Nagpur", "Maharashtra", "early-career", ["React", "JavaScript", "Python", "TypeScript"], ["React", "AI/ML", "Product"], ["Sales", "Night shift"], "B.Tech CSE", 82),
            ("demo_govt", "schemes@bharat.twin", "Ananya Kulkarni", "Pune", "Maharashtra", "student", ["Python", "Data", "SQL"], ["Data", "Learning", "Govt schemes"], ["Long commute"], "B.Sc Statistics", 76),
            ("demo_founder", "founder@bharat.twin", "Rohit Gupta", "Nagpur", "Maharashtra", "founder", ["Product", "Growth", "React"], ["Startup", "Product", "Community"], ["BPO"], "BBA", 79),
        ]
        connection.executemany(
            """INSERT INTO users
            (id,email,full_name,city,state,experience_level,skills_json,interests_json,hates_json,education,ats_score,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            [(uid, email, name, city, state, level, json_dump(skills), json_dump(interests), json_dump(hates), education, ats, now) for uid, email, name, city, state, level, skills, interests, hates, education, ats in users],
        )

        jobs = [
            ("j1", "fh-tcs-react", "Frontend Developer · React + TS", "TCS", "Nagpur", "Maharashtra", ["React", "TypeScript", "Tailwind"], "Build customer-facing products with a team that ships in small, useful steps.", "₹8–14 LPA", "freehire", "https://freehire.me/jobs/fh-tcs-react", "greenhouse", "freehire", 2, 124, 42),
            ("j2", "fh-infosys-node", "Backend Engineer · Node + Postgres", "Infosys", "Pune", "Maharashtra", ["Node.js", "Postgres", "Docker"], "Own reliable APIs and data workflows for teams across India.", "₹12–18 LPA", "kaggle_india", "https://example.com/jobs/infosys-node", "naukri", "kaggle", 18, 89, 31),
            ("j3", "fh-google-rag", "Data Scientist · LLM + RAG", "Google", "Bengaluru", "Karnataka", ["Python", "LLM", "RAG"], "Explore useful language systems that move from research to real people.", "₹22–35 LPA", "freehire", "https://freehire.me/jobs/fh-google-rag", "lever", "freehire", 5, 210, 98),
            ("j4", None, "Product Intern · 0 → 1", "Zerodha", "Mumbai", "Maharashtra", ["Figma", "SQL", "Analytics"], "Learn the craft of product thinking with a team that values clarity.", "₹45k stipend", "kaggle_india", "https://example.com/jobs/zerodha-product", "naukri", "kaggle", 36, 67, 22),
            ("j5", "fh-amazon-devops", "DevOps Engineer · K8s + CI/CD", "Amazon", "Hyderabad", "Telangana", ["Kubernetes", "Docker", "AWS"], "Help the next million releases become safer, faster and more boring.", "₹16–24 LPA", "freehire", "https://freehire.me/jobs/fh-amazon-devops", "amazon", "freehire", 9, 143, 55),
            ("j6", "fh-sarvam-ai", "AI Engineer · Multilingual", "Sarvam AI", "Remote · India", "Remote", ["ML", "Hindi NLP", "Transformers"], "Build language products that understand the texture of Bharat.", "₹18–30 LPA", "freehire", "https://freehire.me/jobs/fh-sarvam-ai", "manual", "freehire", 1, 301, 112),
            ("j7", None, "MERN Developer · Nagpur onsite", "Persistent", "Nagpur", "Maharashtra", ["React", "Node.js", "MongoDB"], "Join a local team shipping modern web experiences for global users.", "₹10–16 LPA", "kaggle_india", "https://example.com/jobs/persistent-mern", "naukri", "kaggle", 3, 98, 34),
            ("j8", None, "Data Analyst · SQL + PowerBI", "Wipro", "Pune", "Maharashtra", ["SQL", "PowerBI", "Excel"], "Turn a noisy business question into a clear decision.", "₹6–9 LPA", "kaggle_india", "https://example.com/jobs/wipro-analyst", "naukri", "kaggle", 28, 54, 18),
            ("j9", "fh-razorpay-design", "Product Designer · Research-led", "Razorpay", "Bengaluru", "Karnataka", ["Figma", "Research", "Product"], "Make complex financial moments feel human and trustworthy.", "₹14–21 LPA", "freehire", "https://freehire.me/jobs/fh-razorpay-design", "greenhouse", "freehire", 7, 72, 29),
        ]
        connection.executemany(
            """INSERT INTO jobs
            (id,freehire_id,title,company,location_city,location_state,skills_json,description,salary,source,source_url,board,provider,posted_at,likes_count,saves_count)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            [(jid, fid, title, company, city, state, json_dump(skills), description, salary, source, url, board, provider, iso_now(hours), likes, saves) for jid, fid, title, company, city, state, skills, description, salary, source, url, board, provider, hours, likes, saves in jobs],
        )

        schemes = [
            ("s1", "PM Internship Scheme", "Ministry of Corporate Affairs", "Students", "12 months + ₹5,000 / month", {"age": True, "state": True, "education": False}, "India", 3),
            ("s2", "NCS Young Professionals", "MSDE · National Career Service", "Jobs", "Skill stipend + placement support", {"age": True, "state": True, "education": True}, "India", 24),
            ("s3", "Startup India Seed Fund", "DPIIT · Startup India", "Startup", "Up to ₹50L grant for validation", {"age": False, "state": True, "education": True}, "India", 48),
            ("s4", "SWAYAM · NPTEL scholarships", "Ministry of Education", "Learning", "Free courses + recognised certificates", {"age": True, "state": True, "education": True}, "India", 6),
            ("s5", "PMKVY 4.0", "Skill India Digital", "Learning", "Industry-aligned upskilling support", {"age": True, "state": True, "education": True}, "India", 10),
            ("s6", "Maharashtra Apprenticeship Drive", "MSSDS · Maharashtra", "Jobs", "Paid apprenticeship + mentor support", {"age": True, "state": True, "education": False}, "Maharashtra", 14),
        ]
        connection.executemany(
            """INSERT INTO schemes
            (id,scheme_name,ministry,category,benefits,eligibility_json,state,posted_at)
            VALUES (?,?,?,?,?,?,?,?)""",
            [(sid, name, ministry, category, benefits, json_dump(eligibility), state, iso_now(hours)) for sid, name, ministry, category, benefits, eligibility, state, hours in schemes],
        )

        peers = [
            ("p1", "Priya Sharma", "Nagpur", 4.2, "SDE @ TCS", ["React", "Node.js"], ["AI/ML", "Product"], 3, "#156b48"),
            ("p2", "Aman Verma", "Pune", 12.8, "Data Analyst @ Infosys", ["Python", "SQL"], ["Data"], 1, "#5076a8"),
            ("p3", "Rohit Gupta", "Nagpur", 2.1, "Founder @ BharatBuild", ["Product", "Growth"], ["Startup"], 5, "#b86e78"),
            ("p4", "Sneha Das", "Remote", 7.4, "ML Intern @ Sarvam", ["Transformers", "Hindi NLP"], ["AI/ML"], 2, "#a278b8"),
            ("p5", "Arjun Mehta", "Hyderabad", 18.3, "DevOps @ Amazon", ["K8s", "Docker"], ["Cloud"], 0, "#9b710d"),
            ("p6", "Kavya Iyer", "Mumbai", 9.1, "Design @ Zerodha", ["Figma", "Research"], ["Design"], 2, "#d46d3b"),
        ]
        connection.executemany(
            """INSERT INTO peers
            (id,name,city,distance_km,role,skills_json,interests_json,mutual_count,color)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            [(pid, name, city, distance, role, json_dump(skills), json_dump(interests), mutuals, color) for pid, name, city, distance, role, skills, interests, mutuals, color in peers],
        )

        startups = [
            ("st1", "You", "Bharat Tutor · AI for Tier-3", "Voice-first tutor for Hindi and Marathi that works on low bandwidth. Need one LLM builder and a calm frontend thinker.", "EdTech", ["React", "LLM", "Hindi"], "Nagpur", .91, 42),
            ("st2", "Rohit G.", "Kisan Mandi Connect", "Farmers to buyers with real mandi prices, lightweight logistics and a UPI-first checkout.", "AgriTech", ["Node", "Maps", "UPI"], "Nagpur", .76, 28),
            ("st3", "Sneha D.", "Health Saathi · ASHA helper", "An offline-friendly assistant for ASHA workers: schedule, transcribe, translate and keep moving.", "Health", ["ML", "React Native"], "Pune", .82, 35),
            ("st4", "Kavya I.", "Namma Skill Circles", "Small, local skill circles that make it easier to learn in public and find collaborators nearby.", "Community", ["Product", "Research", "React"], "Nagpur", .86, 19),
        ]
        connection.executemany(
            """INSERT INTO startups
            (id,owner,title,description,category,skills_json,location_city,match_score,likes_count,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            [(sid, owner, title, description, category, json_dump(skills), city, match, likes, iso_now(index * 6)) for index, (sid, owner, title, description, category, skills, city, match, likes) in enumerate(startups)],
        )

        edges = [("demo_fresher", "p1"), ("p1", "tcs"), ("demo_fresher", "p3"), ("p3", "bharatbuild"), ("p1", "demo_fresher"), ("p3", "demo_fresher")]
        connection.executemany("INSERT OR IGNORE INTO social_edges(source_id,target_id) VALUES (?,?)", edges)
        connection.executemany("INSERT OR IGNORE INTO user_employment(user_id,company) VALUES (?,?)", [("p1", "TCS"), ("p2", "Infosys"), ("p5", "Amazon")])
        connection.executemany(
            "INSERT INTO notifications(user_id,title,body,created_at) VALUES (?,?,?,?)",
            [("demo_fresher", "3 fresh signals", "Three new roles scored above 90% near your network.", iso_now(2)), ("demo_fresher", "PM Internship fit", "You are a strong eligibility match for a government internship.", iso_now(5))],
        )

    def get_user(self, user_id: str) -> dict[str, Any]:
        with self._lock, self._connect() as connection:
            row = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            raise KeyError(user_id)
        return self._user(row)

    def save_user(self, user_id: str, **updates: Any) -> dict[str, Any]:
        allowed = {"full_name", "city", "state", "experience_level", "education", "ats_score", "resume_json"}
        fields = [(key, json_dump(value) if key == "resume_json" else value) for key, value in updates.items() if key in allowed]
        for key in ("skills", "interests", "hates"):
            if key in updates:
                fields.append((f"{key}_json", json_dump(updates[key])))
        if fields:
            set_clause = ", ".join(f"{key} = ?" for key, _ in fields)
            values = [value for _, value in fields] + [user_id]
            with self._lock, self._connect() as connection:
                connection.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
        return self.get_user(user_id)

    def list_jobs(self) -> list[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute("SELECT * FROM jobs ORDER BY posted_at DESC").fetchall()
        return [self._job(row) for row in rows]

    def candidate_pool(self, user_id: str, query_embedding: list[float] | None = None, limit: int = 200) -> dict[str, list[dict[str, Any]]]:
        """Return the local candidate boundary used by the Matcher agent.

        SQLite has no pgvector extension in the zero-credential mode, so the
        agent receives the complete seeded pool and applies its lexical recall.
        SupabaseStore overrides this with pgvector RPC calls.
        """

        return {"jobs": self.list_jobs(), "schemes": self.list_schemes(), "peers": self.list_peers(), "startups": self.list_startups()}

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self._lock, self._connect() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return self._job(row) if row else None

    def list_schemes(self) -> list[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute("SELECT * FROM schemes ORDER BY posted_at DESC").fetchall()
        return [self._scheme(row) for row in rows]

    def get_scheme(self, scheme_id: str) -> dict[str, Any] | None:
        with self._lock, self._connect() as connection:
            row = connection.execute("SELECT * FROM schemes WHERE id = ?", (scheme_id,)).fetchone()
        return self._scheme(row) if row else None

    def list_peers(self, user_id: str | None = None) -> list[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute("SELECT * FROM peers ORDER BY distance_km ASC").fetchall()
        return [self._peer(row) for row in rows]

    def get_peer(self, peer_id: str) -> dict[str, Any] | None:
        with self._lock, self._connect() as connection:
            row = connection.execute("SELECT * FROM peers WHERE id = ?", (peer_id,)).fetchone()
        return self._peer(row) if row else None

    def list_startups(self) -> list[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute("SELECT * FROM startups ORDER BY created_at DESC").fetchall()
        return [self._startup(row) for row in rows]

    def get_startup(self, startup_id: str) -> dict[str, Any] | None:
        with self._lock, self._connect() as connection:
            row = connection.execute("SELECT * FROM startups WHERE id = ?", (startup_id,)).fetchone()
        return self._startup(row) if row else None

    def create_startup(self, owner: str, title: str, description: str, category: str, skills: list[str], location_city: str, match_score: float = .78) -> dict[str, Any]:
        startup_id = f"startup-{int(utc_now().timestamp() * 1000)}"
        with self._lock, self._connect() as connection:
            connection.execute(
                """INSERT INTO startups
                (id,owner,title,description,category,skills_json,location_city,match_score,likes_count,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (startup_id, owner, title, description, category, json_dump(skills), location_city, match_score, 0, iso_now()),
            )
        return self.get_startup(startup_id) or {}

    def add_startup_application(self, startup_id: str, applicant: str, message: str, skills: list[str]) -> dict[str, Any]:
        self.set_memory(applicant, f"startup_application:{startup_id}", {"message": message, "skills": skills, "created_at": iso_now()})
        return {"startup_id": startup_id, "applicant_id": applicant, "message": message, "skill_offer": skills, "status": "received"}

    def list_interactions(self, user_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        query = "SELECT * FROM interactions"
        params: list[Any] = []
        if user_id:
            query += " WHERE user_id = ?"
            params.append(user_id)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._lock, self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def add_impressions(self, user_id: str, impressions: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        created: list[dict[str, Any]] = []
        with self._lock, self._connect() as connection:
            for impression in impressions:
                row = {
                    "impression_id": str(impression.get("impression_id") or f"imp-{uuid.uuid4().hex}"),
                    "user_id": user_id,
                    "item_id": str(impression.get("item_id") or ""),
                    "item_type": str(impression.get("item_type") or "job"),
                    "rank_position": int(impression.get("rank_position") or 0),
                    "candidate_source": str(impression.get("candidate_source") or "feed"),
                    "model_version": str(impression.get("model_version") or "rules-v1"),
                    "surface": str(impression.get("surface") or "feed"),
                    "context_json": json_dump(impression.get("context") or {}),
                    "created_at": str(impression.get("created_at") or iso_now()),
                }
                if not row["item_id"] or row["rank_position"] < 1:
                    continue
                connection.execute(
                    """INSERT OR IGNORE INTO impressions
                    (impression_id,user_id,item_id,item_type,rank_position,candidate_source,model_version,surface,context_json,created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (row["impression_id"], row["user_id"], row["item_id"], row["item_type"], row["rank_position"], row["candidate_source"], row["model_version"], row["surface"], row["context_json"], row["created_at"]),
                )
                created.append({**row, "context": impression.get("context") or {}})
        return created

    def list_impressions(self, user_id: str | None = None, limit: int = 1000) -> list[dict[str, Any]]:
        query = "SELECT * FROM impressions"
        params: list[Any] = []
        if user_id:
            query += " WHERE user_id = ?"
            params.append(user_id)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._lock, self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [
            {**dict(row), "context": json_load(row["context_json"], {})}
            for row in rows
        ]

    def add_interaction(self, user_id: str, item_id: str, item_type: str, action: str, dwell_ms: int = 0, reason: str | None = None) -> dict[str, Any]:
        with self._lock, self._connect() as connection:
            connection.execute(
                "INSERT INTO interactions(user_id,item_id,item_type,action,dwell_ms,reason,created_at) VALUES (?,?,?,?,?,?,?)",
                (user_id, item_id, item_type, action, dwell_ms, reason, iso_now()),
            )
            if item_type == "job":
                field = "likes_count" if action == "like" else "saves_count" if action == "save" else None
                if field:
                    connection.execute(f"UPDATE jobs SET {field} = {field} + 1 WHERE id = ?", (item_id,))
            if action == "hide" and reason:
                user = connection.execute("SELECT hates_json FROM users WHERE id = ?", (user_id,)).fetchone()
                if user:
                    hates = json_load(user["hates_json"], [])
                    if reason not in hates:
                        connection.execute("UPDATE users SET hates_json = ? WHERE id = ?", (json_dump([*hates, reason]), user_id))
        return {"user_id": user_id, "item_id": item_id, "item_type": item_type, "action": action, "dwell_ms": dwell_ms, "reason": reason}

    def get_memory(self, user_id: str) -> dict[str, Any]:
        with self._lock, self._connect() as connection:
            rows = connection.execute("SELECT memory_key,memory_value_json FROM agent_memory WHERE user_id = ?", (user_id,)).fetchall()
        return {row["memory_key"]: json_load(row["memory_value_json"], None) for row in rows}

    def set_memory(self, user_id: str, key: str, value: Any) -> None:
        with self._lock, self._connect() as connection:
            connection.execute(
                """INSERT INTO agent_memory(user_id,memory_key,memory_value_json,updated_at)
                VALUES (?,?,?,?)
                ON CONFLICT(user_id,memory_key) DO UPDATE SET memory_value_json=excluded.memory_value_json, updated_at=excluded.updated_at""",
                (user_id, key, json_dump(value), iso_now()),
            )

    def add_referral_request(self, user_id: str, target_id: str | None, job_id: str | None, hinglish: str, english: str) -> int:
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO referral_requests(user_id,target_id,job_id,draft_hinglish,draft_english,created_at) VALUES (?,?,?,?,?,?)",
                (user_id, target_id, job_id, hinglish, english, iso_now()),
            )
            return int(cursor.lastrowid or 0)

    def list_notifications(self, user_id: str, unread_only: bool = False) -> list[dict[str, Any]]:
        query = "SELECT * FROM notifications WHERE user_id = ?"
        params: list[Any] = [user_id]
        if unread_only:
            query += " AND read_at IS NULL"
        query += " ORDER BY created_at DESC"
        with self._lock, self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def mark_notification_read(self, notification_id: int) -> None:
        with self._lock, self._connect() as connection:
            connection.execute("UPDATE notifications SET read_at = ? WHERE id = ?", (iso_now(), notification_id))

    def upsert_freehire_jobs(self, postings: Iterable[dict[str, Any]]) -> tuple[int, int]:
        inserted = 0
        updated = 0
        with self._lock, self._connect() as connection:
            for posting in postings:
                freehire_id = str(posting.get("freehire_id") or posting.get("id") or "").strip()
                if not freehire_id:
                    continue
                existing = connection.execute("SELECT id FROM jobs WHERE freehire_id = ?", (freehire_id,)).fetchone()
                job_id = str(posting.get("job_id") or f"freehire-{freehire_id}")
                values = (
                    job_id,
                    freehire_id,
                    posting.get("title") or "Untitled role",
                    posting.get("company") or "Unknown company",
                    posting.get("location_city") or posting.get("location") or "Remote",
                    posting.get("location_state") or "",
                    json_dump(posting.get("skills") or []),
                    posting.get("description") or "",
                    posting.get("salary") or "Not listed",
                    "freehire",
                    posting.get("source_url") or posting.get("url"),
                    posting.get("board"),
                    posting.get("provider"),
                    posting.get("posted_at") or iso_now(),
                    int(posting.get("likes_count") or 0),
                    int(posting.get("saves_count") or 0),
                )
                connection.execute(
                    """INSERT INTO jobs
                    (id,freehire_id,title,company,location_city,location_state,skills_json,description,salary,source,source_url,board,provider,posted_at,likes_count,saves_count)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(freehire_id) DO UPDATE SET
                      title=excluded.title, company=excluded.company, location_city=excluded.location_city,
                      location_state=excluded.location_state, skills_json=excluded.skills_json,
                      description=excluded.description, salary=excluded.salary, source_url=excluded.source_url,
                      board=excluded.board, provider=excluded.provider, posted_at=excluded.posted_at""",
                    values,
                )
                if existing:
                    updated += 1
                else:
                    inserted += 1
        return inserted, updated

    def upsert_kaggle_jobs(self, postings: Iterable[dict[str, Any]]) -> tuple[int, int]:
        inserted = 0
        updated = 0
        with self._lock, self._connect() as connection:
            for posting in postings:
                source_id = str(posting.get("freehire_id") or posting.get("id") or "").strip()
                if not source_id:
                    continue
                job_id = str(posting.get("job_id") or f"kaggle-{source_id}")
                existing = connection.execute("SELECT id FROM jobs WHERE id = ?", (job_id,)).fetchone()
                values = (
                    job_id,
                    None,
                    posting.get("title") or "Untitled role",
                    posting.get("company") or "Unknown company",
                    posting.get("location") or "India",
                    posting.get("location_state") or "",
                    json_dump(posting.get("skills") or []),
                    posting.get("description") or "",
                    posting.get("salary") or "Not listed",
                    "kaggle_india",
                    posting.get("url"),
                    posting.get("board") or "kaggle_india",
                    posting.get("provider") or "kaggle_india",
                    posting.get("posted_at") or iso_now(),
                    int(posting.get("likes_count") or 0),
                    int(posting.get("saves_count") or 0),
                )
                connection.execute(
                    """INSERT INTO jobs
                    (id,freehire_id,title,company,location_city,location_state,skills_json,description,salary,source,source_url,board,provider,posted_at,likes_count,saves_count)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(id) DO UPDATE SET
                      title=excluded.title, company=excluded.company, location_city=excluded.location_city,
                      location_state=excluded.location_state, skills_json=excluded.skills_json,
                      description=excluded.description, salary=excluded.salary, source_url=excluded.source_url,
                      board=excluded.board, provider=excluded.provider, posted_at=excluded.posted_at""",
                    values,
                )
                if existing:
                    updated += 1
                else:
                    inserted += 1
        return inserted, updated

    def upsert_schemes(self, schemes: Iterable[dict[str, Any]]) -> tuple[int, int]:
        inserted = 0
        updated = 0
        with self._lock, self._connect() as connection:
            for scheme in schemes:
                scheme_id = str(scheme.get("id") or "").strip()
                if not scheme_id:
                    continue
                existing = connection.execute("SELECT id FROM schemes WHERE id = ?", (scheme_id,)).fetchone()
                connection.execute(
                    """INSERT INTO schemes
                    (id,scheme_name,ministry,category,benefits,eligibility_json,application_url,state,posted_at)
                    VALUES (?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(id) DO UPDATE SET
                      scheme_name=excluded.scheme_name, ministry=excluded.ministry, category=excluded.category,
                      benefits=excluded.benefits, eligibility_json=excluded.eligibility_json,
                      application_url=excluded.application_url, state=excluded.state, posted_at=excluded.posted_at""",
                    (
                        scheme_id,
                        scheme.get("name") or "Government scheme",
                        scheme.get("ministry") or "Government of India",
                        scheme.get("category") or "Career",
                        scheme.get("benefit") or "See official scheme details",
                        json_dump(scheme.get("eligibility") or {}),
                        scheme.get("application_url"),
                        scheme.get("state") or "India",
                        scheme.get("posted_at") or iso_now(),
                    ),
                )
                if existing:
                    updated += 1
                else:
                    inserted += 1
        return inserted, updated

    def source_counts(self) -> dict[str, int]:
        with self._lock, self._connect() as connection:
            rows = connection.execute("SELECT source, COUNT(*) AS count FROM jobs GROUP BY source").fetchall()
        counts = {row["source"]: int(row["count"]) for row in rows}
        counts["total"] = sum(counts.values())
        return counts

    @staticmethod
    def _user(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"], "email": row["email"], "full_name": row["full_name"], "city": row["city"], "state": row["state"],
            "experience_level": row["experience_level"], "skills": json_load(row["skills_json"], []), "interests": json_load(row["interests_json"], []),
            "hates": json_load(row["hates_json"], []), "education": row["education"], "resume_json": json_load(row["resume_json"], None), "ats_score": row["ats_score"],
        }

    @staticmethod
    def _job(row: sqlite3.Row) -> dict[str, Any]:
        posted = datetime.fromisoformat(row["posted_at"])
        hours = max(0, (utc_now() - posted).total_seconds() / 3600)
        return {
            "id": row["id"], "freehire_id": row["freehire_id"], "title": row["title"], "company": row["company"], "location": row["location_city"],
            "location_state": row["location_state"], "skills": json_load(row["skills_json"], []), "description": row["description"], "salary": row["salary"],
            "source": row["source"], "source_url": row["source_url"], "board": row["board"], "provider": row["provider"], "posted_at": row["posted_at"],
            "fresh_hours": hours, "likes": row["likes_count"], "saves": row["saves_count"], "type": "job",
        }

    @staticmethod
    def _scheme(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"], "name": row["scheme_name"], "ministry": row["ministry"], "category": row["category"], "benefit": row["benefits"],
            "eligibility": json_load(row["eligibility_json"], {}), "application_url": row["application_url"], "state": row["state"], "posted_at": row["posted_at"], "type": "scheme",
        }

    @staticmethod
    def _peer(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"], "name": row["name"], "city": row["city"], "distance_km": row["distance_km"], "role": row["role"],
            "skills": json_load(row["skills_json"], []), "interests": json_load(row["interests_json"], []), "mutual_count": row["mutual_count"], "color": row["color"], "type": "peer",
        }

    @staticmethod
    def _startup(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"], "owner": row["owner"], "title": row["title"], "description": row["description"], "category": row["category"],
            "skills": json_load(row["skills_json"], []), "location_city": row["location_city"], "match_score": row["match_score"],
            "likes": row["likes_count"], "created_at": row["created_at"], "type": "startup",
        }
