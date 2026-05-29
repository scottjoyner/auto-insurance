#!/usr/bin/env python3
"""Apply service SQL migrations to a SQLite database.

This is a lightweight Phase 1 bridge until Alembic environments are added for
all services. It is intentionally simple and deterministic: files are applied in
lexicographic order from a service migrations directory.

Usage:
    python scripts/apply_sql_migrations.py --database ./phase1.db --migrations services/quote-service/migrations
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def apply_migrations(database: Path, migrations_dir: Path) -> list[str]:
    if not migrations_dir.exists():
        raise FileNotFoundError(f"Migrations directory not found: {migrations_dir}")
    migration_files = sorted(migrations_dir.glob("*.sql"))
    if not migration_files:
        raise FileNotFoundError(f"No .sql migrations found in: {migrations_dir}")

    applied: list[str] = []
    database.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations "
            "(filename TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        existing = {row[0] for row in conn.execute("SELECT filename FROM schema_migrations")}
        for migration in migration_files:
            if migration.name in existing:
                continue
            sql = migration.read_text(encoding="utf-8")
            conn.executescript(sql)
            conn.execute("INSERT INTO schema_migrations(filename) VALUES (?)", (migration.name,))
            applied.append(migration.name)
        conn.commit()
    return applied


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--migrations", required=True, type=Path)
    args = parser.parse_args()
    applied = apply_migrations(args.database, args.migrations)
    if applied:
        print("Applied migrations:")
        for name in applied:
            print(f"- {name}")
    else:
        print("No new migrations to apply.")


if __name__ == "__main__":
    main()
