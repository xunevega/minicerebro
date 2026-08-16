from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from hashlib import pbkdf2_hmac, sha256
from os import getenv
from secrets import token_hex, token_urlsafe
from threading import Lock
from time import time

from fastapi import HTTPException, Request, status

PBKDF2_ITERATIONS = 200_000
SESSION_COOKIE_NAME = "editados_session"
SESSION_TTL_SECONDS = 60 * 60 * 24 * 14
AUTH_PUBLIC_PATHS = {
    "/",
    "/health",
    "/security/status",
    "/knowledge/status",
    "/auth/register",
    "/auth/login",
    "/auth/me",
}
KNOWLEDGE_WRITE_PREFIXES = (
    "/knowledge/candidates",
    "/knowledge/publications",
    "/knowledge/sources",
    "/knowledge/editions",
    "/knowledge/index",
    "/knowledge/segments",
    "/knowledge/extractions",
    "/knowledge/proposals",
)
GENERATION_PATHS = {
    "/generation",
    "/correction",
    "/rewrite",
    "/sendable",
    "/continue",
    "/variants",
    "/revision",
    "/lab/simulate",
}

_rate_buckets: dict[str, deque[float]] = defaultdict(deque)
_rate_lock = Lock()


def app_env() -> str:
    if getenv("RAILWAY_ENVIRONMENT") or getenv("APP_ENV", "").strip().lower() == "production":
        return "production"
    return getenv("APP_ENV", "local").strip().lower() or "local"


def is_production() -> bool:
    return app_env() == "production"


def auth_required() -> bool:
    explicit = getenv("AUTH_REQUIRED", "").strip().lower()
    if explicit in {"1", "true", "yes"}:
        return True
    if explicit in {"0", "false", "no"}:
        return False
    return is_production()


def docs_enabled() -> bool:
    explicit = getenv("ENABLE_DOCS", "").strip().lower()
    if explicit in {"1", "true", "yes"}:
        return True
    if explicit in {"0", "false", "no"}:
        return False
    return not is_production()


def localhost_cors_allowed() -> bool:
    explicit = getenv("CORS_ALLOW_LOCALHOST", "").strip().lower()
    if explicit in {"1", "true", "yes"}:
        return True
    if explicit in {"0", "false", "no"}:
        return False
    return not is_production()


def session_secret() -> str:
    secret = getenv("SESSION_SECRET", "").strip()
    if secret:
        return secret
    database_url = getenv("DATABASE_URL", "").strip()
    if is_production() and database_url:
        return sha256(f"editados|{database_url}".encode()).hexdigest()
    if is_production():
        raise RuntimeError("SESSION_SECRET is required in production")
    return "dev-insecure-editados-session"


def hash_password(password: str, salt: str | None = None) -> str:
    actual_salt = salt or token_hex(16)
    digest = pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        actual_salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    ).hex()
    return f"{actual_salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _digest = stored.split("$", 1)
    except ValueError:
        return False
    return hash_password(password, salt) == stored


def hash_session_token(token: str) -> str:
    return sha256(f"{session_secret()}|{token}".encode()).hexdigest()


def new_session_token() -> str:
    return token_urlsafe(32)


def client_key(request: Request, user_id: str | None = None) -> str:
    if user_id:
        return f"user:{user_id}"
    host = request.client.host if request.client else "unknown"
    return f"ip:{host}"


def enforce_rate_limit(key: str, max_requests: int, window_seconds: int) -> None:
    now = time()
    with _rate_lock:
        bucket = _rate_buckets[key]
        while bucket and now - bucket[0] > window_seconds:
            bucket.popleft()
        if len(bucket) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiadas peticiones. Espera un momento.",
            )
        bucket.append(now)


def generation_rate_limit(request: Request, user_id: str | None) -> None:
    max_requests = 20 if is_production() else 1000
    enforce_rate_limit(
        f"generation:{client_key(request, user_id)}",
        max_requests=max_requests,
        window_seconds=3600,
    )


def auth_attempt_rate_limit(request: Request, bucket: str) -> None:
    enforce_rate_limit(
        f"{bucket}:{client_key(request)}",
        max_requests=10,
        window_seconds=900,
    )


def is_public_path(path: str) -> bool:
    return path in AUTH_PUBLIC_PATHS or path.startswith(("/docs", "/redoc", "/openapi.json"))


def is_knowledge_write(method: str, path: str) -> bool:
    if method in {"GET", "HEAD", "OPTIONS"}:
        return False
    return any(path == prefix or path.startswith(prefix + "/") for prefix in KNOWLEDGE_WRITE_PREFIXES)


def is_generation_path(path: str) -> bool:
    return path in GENERATION_PATHS or path.endswith("/revision")


@dataclass(frozen=True)
class Actor:
    user_id: str | None
    profile_id: str
    email: str | None
    role: str
    authenticated: bool

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"
