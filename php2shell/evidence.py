# Python 3.11 · content-addressed evidence store
from __future__ import annotations

import hashlib
import json
from pathlib import Path


class EvidenceStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.index = self.root / "index.jsonl"

    def put(self, payload: dict) -> str:
        raw = json.dumps(payload, sort_keys=True, default=str).encode()
        h = hashlib.sha256(raw).hexdigest()
        (self.root / h).write_bytes(raw)
        with self.index.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"hash": h, "url": payload.get("url")}) + "\n")
        return h