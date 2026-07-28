#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.knowledge.snapshot_data import load_knowledge_seed_snapshot  # noqa: E402


DEFAULT_OUTPUT_DIR = BACKEND_DIR / "alembic" / "versions"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "knowledge_snapshot"


def render_migration(
    *,
    version: str,
    revision_id: str,
    down_revision: str,
    create_date: str,
    message: str,
) -> str:
    return f'''"""{message}

Revision ID: {revision_id}
Revises: {down_revision}
Create Date: {create_date}
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

from app.knowledge.snapshot_data import load_knowledge_seed_snapshot

revision: str = "{revision_id}"
down_revision: str | None = "{down_revision}"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SNAPSHOT_VERSION = "{version}"


def upgrade() -> None:
    snapshot = load_knowledge_seed_snapshot(SNAPSHOT_VERSION)
    bind = op.get_bind()
    metadata = sa.MetaData()

    for table_name, rows in snapshot["tables"].items():
        table = sa.Table(table_name, metadata, autoload_with=bind)
        primary_key = next(iter(table.primary_key.columns))
        for row in rows:
            exists = bind.execute(
                sa.select(primary_key).where(primary_key == row[primary_key.name])
            ).first()
            if exists is not None:
                continue
            bind.execute(table.insert().values(**row))


def downgrade() -> None:
    # The upgrade is idempotent and may skip rows that already existed before this migration.
    # A destructive downgrade could delete pre-existing published knowledge, so data is preserved.
    return
'''


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Crea una migracion Alembic de datos para un snapshot publicado.",
    )
    parser.add_argument("--version", required=True)
    parser.add_argument("--revision-id", required=True)
    parser.add_argument("--down-revision", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--create-date", default=date.today().isoformat())
    parser.add_argument("--message")
    args = parser.parse_args()

    load_knowledge_seed_snapshot(args.version)

    message = args.message or f"seed {args.version} snapshot"
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{args.revision_id}_{slugify(message)}.py"
    if output_path.exists():
        raise FileExistsError(f"Migration already exists: {output_path}")

    output_path.write_text(
        render_migration(
            version=args.version,
            revision_id=args.revision_id,
            down_revision=args.down_revision,
            create_date=args.create_date,
            message=message,
        ),
        encoding="utf-8",
    )
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
