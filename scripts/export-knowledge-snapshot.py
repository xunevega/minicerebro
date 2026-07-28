#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exporta una foto reproducible del conocimiento publicado persistido.",
    )
    parser.add_argument("--version")
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--database-url",
        help="Exporta desde una base existente. Si se omite, crea una SQLite temporal y aplica Alembic.",
    )
    args = parser.parse_args()

    if args.database_url:
        os.environ["DATABASE_URL"] = args.database_url
        export = _export_snapshot(args.version)
    else:
        with tempfile.NamedTemporaryFile(prefix="minicerebro-knowledge-export-", suffix=".sqlite3") as db:
            os.environ["DATABASE_URL"] = f"sqlite:///{db.name}"

            from app.db.bootstrap import upgrade_database

            upgrade_database()
            export = _export_snapshot(args.version, ensure_profile_seed=True)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(export, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


def _export_snapshot(version: str | None, *, ensure_profile_seed: bool = False) -> dict:
    from app.db.bootstrap import ensure_seed_data
    from app.db.session import SessionLocal
    from app.knowledge.snapshot_export import (
        export_knowledge_seed_snapshot,
        latest_published_snapshot_version,
    )

    with SessionLocal() as session:
        if ensure_profile_seed:
            ensure_seed_data(session)
        resolved_version = version or latest_published_snapshot_version(session)
        return export_knowledge_seed_snapshot(session, version=resolved_version)


if __name__ == "__main__":
    raise SystemExit(main())
