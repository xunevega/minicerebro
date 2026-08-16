from threading import Lock
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth.service import extract_bearer_token, user_from_token
from app.core.repository import Repository
from app.core.security import (
    Actor,
    auth_required,
    generation_rate_limit,
    is_generation_path,
    is_knowledge_write,
    is_public_path,
)
from app.core.seeds import DEFAULT_PROFILE_ID
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


def resolve_actor(request: Request, session: Session) -> Actor:
    user = user_from_token(session, extract_bearer_token(request))
    if user is not None:
        return Actor(
            user_id=user.id,
            profile_id=user.profile_id,
            email=user.email,
            role=user.role,
            authenticated=True,
        )
    return Actor(
        user_id=None,
        profile_id=DEFAULT_PROFILE_ID,
        email=None,
        role="anonymous",
        authenticated=False,
    )


def get_actor(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> Actor:
    actor = resolve_actor(request, session)
    request.state.actor = actor
    if not auth_required() or request.method == "OPTIONS" or is_public_path(request.url.path):
        return actor

    path = request.url.path
    method = request.method
    needs_session = method != "GET" or path.startswith(
        (
            "/profiles",
            "/preferences",
            "/texts",
            "/audit",
            "/feedback",
            "/comparisons",
            "/knowledge/query-history",
            "/knowledge/query-summary",
        )
    )
    if needs_session and not actor.authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Necesitas entrar con tu cuenta.",
        )
    if is_knowledge_write(method, path) and not actor.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta acción pide una cuenta de administración.",
        )
    if is_generation_path(path):
        generation_rate_limit(request, actor.user_id)
    return actor


def resolve_profile_id(profile_id: str, actor: Actor) -> str:
    if profile_id in {"me", "default"}:
        return actor.profile_id
    if auth_required() and profile_id != actor.profile_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes usar el perfil de otra cuenta.",
        )
    return profile_id
