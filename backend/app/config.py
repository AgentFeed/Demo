from __future__ import annotations

import os
from dataclasses import dataclass


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Environment-backed runtime configuration.

    The local SQLite mode remains the default. Setting ``BCT_STORE_BACKEND``
    to ``supabase`` opts into the real Supabase/Auth/pgvector path.
    """

    app_env: str
    store_backend: str
    db_path: str | None
    supabase_url: str | None
    supabase_key: str | None
    groq_api_key: str | None
    groq_model: str
    embedding_backend: str
    embedding_model: str
    embedding_api_url: str | None
    embedding_api_key: str | None
    embedding_dimension: int
    use_langgraph: bool
    freehire_api_url: str | None
    freehire_api_key: str | None
    freehire_json_url: str | None
    freehire_database_url: str | None
    freehire_max_pages: int
    myscheme_api_url: str | None
    myscheme_api_key: str | None
    myscheme_resource_id: str | None
    admin_token: str | None
    cors_origins: tuple[str, ...]

    @classmethod
    def from_env(cls) -> "Settings":
        cors = tuple(value.strip() for value in os.getenv("CORS_ORIGINS", "*").split(",") if value.strip()) or ("*",)
        return cls(
            app_env=os.getenv("APP_ENV", "local"),
            store_backend=os.getenv("BCT_STORE_BACKEND", "sqlite").strip().lower(),
            db_path=os.getenv("BCT_DB_PATH"),
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY"),
            groq_api_key=os.getenv("GROQ_API_KEY"),
            groq_model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            embedding_backend=os.getenv("EMBEDDING_BACKEND", "sentence-transformers" if os.getenv("BCT_STORE_BACKEND", "sqlite").lower() == "supabase" else "none"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            embedding_api_url=os.getenv("EMBEDDING_API_URL"),
            embedding_api_key=os.getenv("EMBEDDING_API_KEY"),
            embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "384")),
            use_langgraph=_as_bool(os.getenv("USE_LANGGRAPH"), True),
            freehire_api_url=os.getenv("FREEHIRE_API_URL", "https://freehire.me/api/v1/jobs"),
            freehire_api_key=os.getenv("FREEHIRE_API_KEY"),
            freehire_json_url=os.getenv("FREEHIRE_JSON_URL"),
            freehire_database_url=os.getenv("FREEHIRE_DATABASE_URL"),
            freehire_max_pages=int(os.getenv("FREEHIRE_MAX_PAGES", "10")),
            myscheme_api_url=os.getenv("MYSCHEME_API_URL"),
            myscheme_api_key=os.getenv("MYSCHEME_API_KEY"),
            myscheme_resource_id=os.getenv("MYSCHEME_RESOURCE_ID"),
            admin_token=os.getenv("BCT_ADMIN_TOKEN"),
            cors_origins=cors,
        )

    @property
    def supabase_configured(self) -> bool:
        return self.store_backend == "supabase" and bool(self.supabase_url and self.supabase_key)

    @property
    def groq_configured(self) -> bool:
        return bool(self.groq_api_key)

    @property
    def freehire_configured(self) -> bool:
        return bool(self.freehire_json_url or self.freehire_database_url or self.freehire_api_url)

    @property
    def myscheme_configured(self) -> bool:
        return bool(self.myscheme_api_url and self.myscheme_api_key)


settings = Settings.from_env()


def integration_status() -> dict[str, object]:
    try:
        import langgraph  # type: ignore

        langgraph_available = True
    except ImportError:
        langgraph_available = False
    try:
        import groq  # type: ignore

        groq_available = True
    except ImportError:
        groq_available = False
    try:
        from .integrations.embeddings import get_embedding_provider

        embeddings_available = get_embedding_provider().available
    except Exception:
        embeddings_available = False
    try:
        from .learning import load_runtime_ranker

        ranker_available = load_runtime_ranker() is not None
    except Exception:
        ranker_available = False
    return {
        "store": settings.store_backend,
        "supabase": settings.supabase_configured,
        "groq": settings.groq_configured and groq_available,
        "langgraph": settings.use_langgraph and langgraph_available,
        "embeddings": embeddings_available,
        "ranker": ranker_available,
        "freehire": settings.freehire_configured,
        "myscheme": settings.myscheme_configured,
        "environment": settings.app_env,
    }
