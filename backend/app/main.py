from os import getenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

DEFAULT_CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


def cors_allow_origins() -> list[str]:
    configured_origins = [
        origin.strip().rstrip("/")
        for origin in getenv("CORS_ALLOW_ORIGINS", "").split(",")
        if origin.strip()
    ]
    return [
        *DEFAULT_CORS_ORIGINS,
        *[origin for origin in configured_origins if origin not in DEFAULT_CORS_ORIGINS],
    ]


app = FastAPI(
    title="Minicerebro API",
    version="1.0.0",
    description="API inicial para Minicerebro V1.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allow_origins(),
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
