# Python 3.11 · runtime config
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    safe: bool = True
    concurrency: int = 20
    rate: float = 25.0
    tor: bool = False
    proxy: str | None = None
    output_dir: Path = Path("./out")
    verify_tls: bool = False
    log_level: str = "INFO"
    collector_url: str | None = None
    authz_doc: Path | None = None