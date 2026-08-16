from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.auth.service import (
    AuthSession,
    AuthStatus,
    LoginInput,
    RegisterInput,
    auth_status_for,
    extract_bearer_token,
    login_user,
    register_user,
    revoke_token,
    user_from_token,
)
from app.db.session import get_session

router = APIRouter(prefix="/auth", tags=["auth"])
SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/register", response_model=AuthSession)
def register(payload: RegisterInput, request: Request, session: SessionDep) -> AuthSession:
    return register_user(session, payload, request)


@router.post("/login", response_model=AuthSession)
def login(payload: LoginInput, request: Request, session: SessionDep) -> AuthSession:
    return login_user(session, payload, request)


@router.post("/logout")
def logout(request: Request, session: SessionDep) -> dict[str, str]:
    revoke_token(session, extract_bearer_token(request))
    return {"status": "ok"}


@router.get("/me", response_model=AuthStatus)
def me(request: Request, session: SessionDep) -> AuthStatus:
    user = user_from_token(session, extract_bearer_token(request))
    return auth_status_for(user)
