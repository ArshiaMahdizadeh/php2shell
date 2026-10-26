# Python 3.11 · token-bucket rate limiter
from __future__ import annotations

import asyncio
import time


class RateLimiter:
    def __init__(self, rate_per_sec: float, burst: int | None = None) -> None:
        self.rate = float(rate_per_sec)
        self.burst = burst or max(1, int(rate_per_sec))
        self.tokens = float(self.burst)
        self.last = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last
            self.last = now
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            if self.tokens < 1.0:
                need = (1.0 - self.tokens) / self.rate
                await asyncio.sleep(need)
                self.tokens = 0.0
                self.last = time.monotonic()
            else:
                self.tokens -= 1.0