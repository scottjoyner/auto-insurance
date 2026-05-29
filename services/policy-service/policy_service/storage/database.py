"""Database session helpers for policy persistence."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from policy_service.config.settings import settings


class Base(DeclarativeBase):
    """Base class for policy service ORM models."""


sync_database_url = settings.database_url.replace("sqlite+aiosqlite", "sqlite")
connect_args = {}
engine_kwargs = {}
if sync_database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    if sync_database_url in {"sqlite://", "sqlite:///:memory:"}:
        engine_kwargs["poolclass"] = StaticPool

engine = create_engine(sync_database_url, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def create_schema() -> None:
    from policy_service.storage import orm  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
