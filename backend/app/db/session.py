from collections.abc import Generator
from functools import lru_cache
from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DEFAULT_DATABASE_URL = "sqlite:///./minicerebro.sqlite3"


class Base(DeclarativeBase):
    pass


@lru_cache
def database_url() -> str:
    return getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


@lru_cache
def engine():
    url = database_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine())


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

