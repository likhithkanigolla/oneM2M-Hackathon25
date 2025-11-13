"""
Simple async rate limiter for LLM requests.

Implements a sliding-window limiter: at most `max_calls` allowed per `period` seconds.
This is lightweight and works without background refill tasks. Callers should `await
acquire()` before performing an LLM request; the method will sleep if necessary until
the request is allowed.
"""
import asyncio
import time
from collections import deque
from typing import Deque


class LLMRateLimiter:
    def __init__(self, max_calls: int = 5, period: float = 60.0):
        self.max_calls = max_calls
        self.period = period
        self._timestamps: Deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until making a new request would not exceed the rate limit.

        This method will sleep for the minimal required time if the recent
        requests in the rolling window already reached `max_calls`.
        """
        while True:
            now = time.monotonic()
            async with self._lock:
                # Remove timestamps older than the period
                while self._timestamps and now - self._timestamps[0] >= self.period:
                    self._timestamps.popleft()

                if len(self._timestamps) < self.max_calls:
                    # We can proceed
                    self._timestamps.append(now)
                    return

                # Otherwise, compute sleep time until oldest timestamp exits window
                oldest = self._timestamps[0]
                sleep_for = self.period - (now - oldest)

            # Sleep outside the lock and log if caller had to wait
            if sleep_for > 0:
                # A small informative print is useful in logs to diagnose throttling
                try:
                    print(f"LLMRateLimiter: rate limit reached, sleeping for {sleep_for:.2f}s")
                except Exception:
                    pass
                await asyncio.sleep(sleep_for)
            else:
                # Fallback small yield to avoid busy loop
                await asyncio.sleep(0.1)


import os

# Module-level singleton limiter for all LLM clients. Default: 10 requests/minute.
# Can be configured with environment variable LLM_MAX_REQUESTS_PER_MINUTE.
_env_max = os.getenv("LLM_MAX_REQUESTS_PER_MINUTE")
try:
    _max_calls = int(_env_max) if _env_max is not None else 5
except ValueError:
    _max_calls = 5

_global_llm_rate_limiter: LLMRateLimiter = LLMRateLimiter(max_calls=_max_calls, period=60.0)


def get_global_llm_rate_limiter() -> LLMRateLimiter:
    return _global_llm_rate_limiter
