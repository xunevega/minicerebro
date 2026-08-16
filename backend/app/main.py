from os import getenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.api.routes import router
from app.auth.routes import router as auth_router
from app.core.security import docs_enabled, localhost_cors_allowed

DEFAULT_CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


def cors_allow_origins() -> list[str]:
    configured_origins = [
        origin.strip().rstrip("/")
        for origin in getenv("CORS_ALLOW_ORIGINS", "").split(",")
        if origin.strip()
    ]
    if localhost_cors_allowed():
        extra = [origin for origin in configured_origins if origin not in DEFAULT_CORS_ORIGINS]
        return [*DEFAULT_CORS_ORIGINS, *extra]
    return configured_origins


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        return response


app = FastAPI(
    title="Editados API",
    version="1.0.0",
    description="API para Editados V1.",
    docs_url="/docs" if docs_enabled() else None,
    redoc_url="/redoc" if docs_enabled() else None,
    openapi_url="/openapi.json" if docs_enabled() else None,
)

app.add_middleware(SecurityHeadersMiddleware)
cors_kwargs: dict = {
    "allow_origins": cors_allow_origins(),
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
if localhost_cors_allowed():
    cors_kwargs["allow_origin_regex"] = r"^http://(localhost|127\.0\.0\.1):\d+$"

app.add_middleware(CORSMiddleware, **cors_kwargs)

app.include_router(auth_router)
app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    payload = {
        "name": "Editados API",
        "status": "ok",
        "health": "/health",
        "frontend": "https://frontend-production-834c.up.railway.app",
    }
    if docs_enabled():
        payload["docs"] = "/docs"
    return payload


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
