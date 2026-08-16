from datetime import UTC, datetime, timedelta
from os import getenv
from uuid import uuid4

from fastapi import HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import (
    SESSION_TTL_SECONDS,
    auth_attempt_rate_limit,
    auth_required,
    hash_password,
    hash_session_token,
    new_session_token,
    verify_password,
)
from app.core.seeds import DEFAULT_PROFILE_ID
from app.db.bootstrap import ensure_named_profile
from app.db.models import SessionRecord, UserRecord


class RegisterInput(BaseModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=200)
    name: str = Field(default="", max_length=200)


class LoginInput(BaseModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=200)


class AuthUser(BaseModel):
    id: str
    email: str
    name: str
    profile_id: str
    role: str


class AuthSession(BaseModel):
    token: str
    user: AuthUser


class AuthStatus(BaseModel):
    auth_required: bool
    user: AuthUser | None
    profile_id: str


def _user_out(user: UserRecord) -> AuthUser:
    return AuthUser(
        id=user.id,
        email=user.email,
        name=user.name,
        profile_id=user.profile_id,
        role=user.role,
    )


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _admin_email() -> str:
    return getenv("ADMIN_EMAIL", "").strip().lower()


def _initial_role(session: Session, email: str) -> str:
    if _admin_email() and email == _admin_email():
        return "admin"
    user_count = session.scalar(select(func.count()).select_from(UserRecord)) or 0
    if user_count == 0:
        return "admin"
    return "user"


def _promote_admin_email(session: Session, user: UserRecord) -> UserRecord:
    if _admin_email() and user.email == _admin_email() and user.role != "admin":
        user.role = "admin"
        session.flush()
    return user


def register_user(session: Session, payload: RegisterInput, request: Request) -> AuthSession:
    auth_attempt_rate_limit(request, "register")
    email = _normalize_email(str(payload.email))
    existing = session.scalar(select(UserRecord).where(UserRecord.email == email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ese correo ya tiene cuenta.")
    user_id = str(uuid4())
    profile_id = f"user-{user_id}"
    name = payload.name.strip() or email.split("@", 1)[0]
    ensure_named_profile(session, profile_id, name)
    user = UserRecord(
        id=user_id,
        email=email,
        name=name,
        password_hash=hash_password(payload.password),
        profile_id=profile_id,
        role=_initial_role(session, email),
        created_at=datetime.now(UTC),
    )
    session.add(user)
    session.flush()
    return issue_session(session, user)


def login_user(session: Session, payload: LoginInput, request: Request) -> AuthSession:
    auth_attempt_rate_limit(request, "login")
    email = _normalize_email(str(payload.email))
    user = session.scalar(select(UserRecord).where(UserRecord.email == email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o contraseña no valen.")
    return issue_session(session, _promote_admin_email(session, user))


def issue_session(session: Session, user: UserRecord) -> AuthSession:
    token = new_session_token()
    now = datetime.now(UTC)
    session.add(
        SessionRecord(
            id=str(uuid4()),
            user_id=user.id,
            token_hash=hash_session_token(token),
            created_at=now,
            expires_at=now + timedelta(seconds=SESSION_TTL_SECONDS),
        )
    )
    session.commit()
    return AuthSession(token=token, user=_user_out(user))


def user_from_token(session: Session, token: str | None) -> UserRecord | None:
    if not token:
        return None
    record = session.scalar(
        select(SessionRecord).where(SessionRecord.token_hash == hash_session_token(token))
    )
    if record is None or _as_utc(record.expires_at) < datetime.now(UTC):
        return None
    return session.get(UserRecord, record.user_id)


def revoke_token(session: Session, token: str | None) -> None:
    if not token:
        return
    record = session.scalar(
        select(SessionRecord).where(SessionRecord.token_hash == hash_session_token(token))
    )
    if record is not None:
        session.delete(record)
        session.commit()


def extract_bearer_token(request: Request) -> str | None:
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        token = header[7:].strip()
        return token or None
    return request.cookies.get("editados_session")


def auth_status_for(user: UserRecord | None) -> AuthStatus:
    if user is not None:
        return AuthStatus(
            auth_required=auth_required(),
            user=_user_out(user),
            profile_id=user.profile_id,
        )
    return AuthStatus(
        auth_required=auth_required(),
        user=None,
        profile_id=DEFAULT_PROFILE_ID,
    )
