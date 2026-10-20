"""Small, process-local request limiter for the public API surface.

This is deliberately a safety net, not a replacement for an edge/WAF rate
limit. Deployments with multiple workers or instances must also enforce the
same limits at the reverse proxy or API gateway.
"""

from collections import deque
from dataclasses import dataclass, field
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request, status


@dataclass
class _RateLimitBucket:
    requests: deque[float] = field(default_factory=deque)


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, _RateLimitBucket] = {}
        self._lock = Lock()

    def check(self, *, key: str, limit: int, window_seconds: int) -> None:
        now = monotonic()
        cutoff = now - window_seconds
        with self._lock:
            bucket = self._buckets.setdefault(key, _RateLimitBucket())
            while bucket.requests and bucket.requests[0] <= cutoff:
                bucket.requests.popleft()
            if len(bucket.requests) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again shortly.",
                    headers={"Retry-After": str(window_seconds)},
                )
            bucket.requests.append(now)


rate_limiter = InMemoryRateLimiter()


def client_identifier(request: Request) -> str:
    """Returns the direct peer address without trusting spoofable headers.

    Configure rate limiting at the trusted proxy as well. If the deployment
    later enables trusted forwarded headers, this helper can be extended in
    one place with explicit proxy validation.
    """

    return request.client.host if request.client else "unknown"
