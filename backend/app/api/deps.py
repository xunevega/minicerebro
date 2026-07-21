from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.repository import Repository
from app.db.bootstrap import ensure_seed_data
from app.db.session import get_session


def get_repository(session: Annotated[Session, Depends(get_session)]) -> Repository:
    ensure_seed_data(session)
    return Repository(session)
