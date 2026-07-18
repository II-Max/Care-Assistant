"""
In-memory rate limiter for anonymous chat traffic.

This is deliberately small for Phase 1. Phase 3 replaces it with a Redis-backed
implementation so limits are shared across API replicas.
"""

import time
from collections import defaultdict, deque


class SlidingWindowRateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        events = self._events[key]

        while events and now - events[0] >= self.window_seconds:
            events.popleft()

        if len(events) >= self.limit:
            return False

        events.append(now)
        return True
