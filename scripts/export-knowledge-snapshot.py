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

from app.knowledge.catalog import LATEST_PUBLISHED_KNOWLEDGE_VERSION  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exporta una foto reproducible del conocimiento sembrado.",
    )
    parser.add_argument("--version", default=LATEST_PUBLISHED_KNOWLEDGE_VERSION)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with tempfile.NamedTemporaryFile(prefix="minicerebro-knowledge-export-", suffix=".sqlite3") as db:
        os.environ["DATABASE_URL"] = f"sqlite:///{db.name}"

        from app.db.bootstrap import ensure_seed_data, upgrade_database
        from app.db.session import SessionLocal
        from app.knowledge.snapshot_export import export_knowledge_seed_snapshot

        upgrade_database()
        with SessionLocal() as session:
            ensure_seed_data(session)
            export = export_knowledge_seed_snapshot(session, version=args.version)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(export, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
