from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from ..db.base import get_session
from ..db.repo import Repository


def get_repository(session: Session = Depends(get_session)) -> Repository:
    return Repository(session)

