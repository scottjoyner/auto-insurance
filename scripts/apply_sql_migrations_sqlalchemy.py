#!/usr/bin/env python3
"""Apply SQL migrations through SQLAlchemy.

This runner is intended for CI validation against Postgres and other SQLAlchemy
supported databases. It tracks migrations by service-qualified filename to avoid
collisions across service migration directories.

Usage:
    python scripts/apply_sql_migrations_sqlalchemy.py \
      --database-url postgresql+psycopg2://postgres:postgres@localhost:5432/auto_insurance_test \
      --service quote \
      --migrations services/quote-service/migrations
"""

from __future__ import annotations

import argparse
from pathlib import Path

from sqlalchemy import create_engine, text


def apply_migrations(database_url: str, service: str, migrations_dir: Path) -> list[str]:
    if not migrations_dir.exists():
        raise FileNotFoundError(f"Migrations directory not found: {migrations_dir}")
    migration_files = sorted(migrations_dir.glob("*.sql"))
    if not migration_files:
        raise FileNotFoundError(f"No .sql migrations found in: {migrations_dir}")

    engine = create_engine(database_url)
    applied: list[str] = []
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS schema_migrations (service VARCHAR(128) NOT NULL, filename VARCHAR(256) NOT NULL, applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(service, filename))"))
        existing = {
            row[0]
            for row in conn.execute(
                text("SELECT filename FROM schema_migrations WHERE service = :service"),
                {"service": service},
            )
        }
        for migration in migration_files:
            if migration.name in existing:
                continue
            sql = migration.read_text(encoding="utf-8")
            for statement in [chunk.strip() for chunk in sql.split(";") if chunk.strip()]:
                conn.execute(text(statement))
            conn.execute(
                text("INSERT INTO schema_migrations(service, filename) VALUES (:service, :filename)"),
                {"service": service, "filename": migration.name},
            )
            applied.append(migration.name)
    return applied


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--service", required=True)
    parser.add_argument("--migrations", required=True, type=Path)
    args = parser.parse_args()
    applied = apply_migrations(args.database_url, args.service, args.migrations)
    if applied:
        print(f"Applied {args.service} migrations:")
        for migration in applied:
            print(f"- {migration}")
    else:
        print(f"No new {args.service} migrations to apply.")


if __name__ == "__main__":
    main()
