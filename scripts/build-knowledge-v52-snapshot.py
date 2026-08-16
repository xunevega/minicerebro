#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.knowledge.snapshot_data import knowledge_snapshot_path  # noqa: E402
from app.knowledge.v52_spanish_writing_batch import VERSION, build_v52_snapshot  # noqa: E402


def main() -> int:
    snapshot = build_v52_snapshot()
    output_path = knowledge_snapshot_path(VERSION)
    output_path.write_text(
        json.dumps(snapshot, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output_path)
    print("units", snapshot["counts"]["knowledge_cards"])
    print("snapshot_cards", snapshot["snapshot_counts"]["card_count"])
    print("snapshot_sources", snapshot["snapshot_counts"]["source_count"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
