"""Database helpers for customer service."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from customer_service.config import settings


class Base(DeclarativeBase):
    """Base class for customer service ORM models."""


connect_args = {}
engine_kwargs = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    if settings.database_url in {"sqlite://", "sqlite:///:memory:"}:
        engine_kwargs["poolclass"] = StaticPool

engine = create_engine(settings.database_url, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def create_schema() -> None:
    from customer_service import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
