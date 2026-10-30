from __future__ import annotations

from typing import Any

from .config import settings
from .store import Store


def create_store() -> Any:
    if settings.store_backend == "supabase":
        from .integrations.supabase_store import SupabaseStore

        return SupabaseStore()
    return Store(settings.db_path)
