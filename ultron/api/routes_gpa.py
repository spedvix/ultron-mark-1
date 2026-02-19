from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/estimate")
async def gpa_estimate() -> dict[str, object]:
    return {"estimate": None, "status": "coming_soon"}

