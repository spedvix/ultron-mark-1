from __future__ import annotations

from datetime import timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select, text

from ..api.deps import get_repository
from ..db.models import SyncState
from ..db.repo import Repository
from ..settings import settings

router = APIRouter()


@router.get("/health")
async def health_check(repo: Repository = Depends(get_repository)) -> dict[str, object]:
    session = repo.session
    try:
        session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:  # pragma: no cover - health check failure path
        db_status = f"error: {exc}"

    syncs = {}
    for state in session.execute(select(SyncState)).scalars():
        syncs[state.source] = state.updated_ts.isoformat()

    return {
        "ok": db_status == "ok",
        "env": settings.ultron_env,
        "db": db_status,
        "last_syncs": syncs,
    }

