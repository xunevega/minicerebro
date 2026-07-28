from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.knowledge.snapshot_export import SNAPSHOT_EXPORT_FORMAT

SNAPSHOT_DATA_DIR = Path(__file__).resolve().parent / "data"


def knowledge_snapshot_path(version: str) -> Path:
    return SNAPSHOT_DATA_DIR / f"{version}.snapshot.json"


def load_knowledge_seed_snapshot(version: str) -> dict[str, Any]:
    path = knowledge_snapshot_path(version)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload["format"] != SNAPSHOT_EXPORT_FORMAT:
        raise RuntimeError(f"unexpected knowledge snapshot format: {payload['format']}")
    if payload["version"] != version:
        raise RuntimeError(f"unexpected knowledge snapshot version: {payload['version']}")
    return payload
