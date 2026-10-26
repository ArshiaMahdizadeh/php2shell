# Python 3.11 · scan orchestrator
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

import httpx

from .fingerprinter import fingerprint
from .ratelimit import RateLimiter
from .stealth import Stealth
from .triggers.fatal import FatalTrigger
from .triggers.oom import OOMTrigger


@dataclass
class ScanResult:
    url: str
    php_version: str | None
    sapi: str | None
    confident: list[str]
    suspected: list[str]
    evidence: dict = field(default_factory=dict)


class Scanner:
    def __init__(self, *, safe: bool = True, concurrency: int = 20, rate: float = 25.0, stealth: Stealth | None = None) -> None:
        self.safe = safe
        self.concurrency = concurrency
        self.limiter = RateLimiter(rate)
        self.stealth = stealth or Stealth()

    async def scan_one(self, client: httpx.AsyncClient, url: str) -> ScanResult:
        await self.limiter.acquire()
        fp = await fingerprint(client, url)
        triggers = [OOMTrigger(safe=self.safe), FatalTrigger(safe=self.safe)]
        confident, suspected, ev = [], [], {"trigger": {}}
        for t in triggers:
            res = await t.run(client, url)
            ev["trigger"][res.cve] = res.evidence
            if res.confidence >= 0.75:
                confident.append(res.cve)
            elif res.confidence >= 0.55:
                suspected.append(res.cve)
        return ScanResult(url=url, php_version=fp.php_version, sapi=fp.sapi,
                          confident=confident, suspected=suspected, evidence=ev)

    async def scan(self, urls: list[str]) -> list[ScanResult]:
        sem = asyncio.Semaphore(self.concurrency)
        out: list[ScanResult] = []
        async with self.stealth.client() as client:
            async def _one(u: str) -> None:
                async with sem:
                    try:
                        out.append(await self.scan_one(client, u))
                    except Exception as e:
                        out.append(ScanResult(u, None, None, [], [], {"error": str(e)}))
            await asyncio.gather(*(_one(u) for u in urls))
        return out