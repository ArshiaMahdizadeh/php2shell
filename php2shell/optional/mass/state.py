# Python 3.11 · per-target state, durable in SQLite
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, asdict, field
from pathlib import Path


@dataclass
class TargetState:
    target: str
    phase: str = "new"
    cves: list[str] = field(default_factory=list)
    whoami: str | None = None
    shell_url: str | None = None
    exfil_files: list[str] = field(default_factory=list)
    last_error: str | None = None


class StateStore:
    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS state (target TEXT PRIMARY KEY, json TEXT NOT NULL)"
        )
        self.conn.commit()

    def get_or_create(self, target: str) -> TargetState:
        cur = self.conn.execute("SELECT json FROM state WHERE target=?", (target,))
        row = cur.fetchone()
        if row:
            return TargetState(**json.loads(row[0]))
        st = TargetState(target=target)
        self.save(st)
        return st

    def save(self, st: TargetState) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO state (target, json) VALUES (?, ?)",
            (st.target, json.dumps(asdict(st))),
        )
        self.conn.commit()