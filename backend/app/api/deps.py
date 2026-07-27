from typing import Annotated
from threading import Lock

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.repository import Repository
from app.db.bootstrap import ensure_seed_data
from app.db.session import get_session

_SEEDED_DATABASE_URLS: set[str] = set()
_SEED_LOCK = Lock()


def ensure_seed_data_once(session: Session) -> None:
    database_url = str(session.get_bind().url)
    if database_url in _SEEDED_DATABASE_URLS:
        return
    with _SEED_LOCK:
        if database_url in _SEEDED_DATABASE_URLS:
            return
        ensure_seed_data(session)
        _SEEDED_DATABASE_URLS.add(database_url)


def get_repository(session: Annotated[Session, Depends(get_session)]) -> Repository:
    ensure_seed_data_once(session)
    return Repository(session)
