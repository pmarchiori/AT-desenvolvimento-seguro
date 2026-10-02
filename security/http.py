import os
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

class LoginRateLimiter:
    def __init__(self) -> None:
        self.limit = int(os.getenv("LOGIN_RATE_LIMIT", "5"))
        self.window_seconds = int(os.getenv("LOGIN_RATE_WINDOW_SECONDS", "60"))
        self._failures = defaultdict(deque)
        self._lock = Lock()

    def _remove_expired(self, key: str, now: float) -> None:
        failures = self._failures[key]
        cutoff = now - self.window_seconds
        while failures and failures[0] <= cutoff:
            failures.popleft()
        if not failures:
            self._failures.pop(key, None)

    def is_blocked(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            self._remove_expired(key, now)
            return len(self._failures.get(key, ())) >= self.limit

    def register_failure(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            self._remove_expired(key, now)
            self._failures[key].append(now)

    def clear(self, key: str) -> None:
        with self._lock:
            self._failures.pop(key, None)

    def reset(self) -> None:
        with self._lock:
            self._failures.clear()

login_rate_limiter = LoginRateLimiter()

class LoginRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method != "POST" or request.url.path != "/user/signin":
            return await call_next(request)

        client_key = request.client.host if request.client else "unknown"
        if login_rate_limiter.is_blocked(client_key):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Muitas tentativas de login. Tente novamente mais tarde."},
                headers={"Retry-After": str(login_rate_limiter.window_seconds)},
            )

        response = await call_next(request)
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            login_rate_limiter.register_failure(client_key)
        elif response.status_code < 400:
            login_rate_limiter.clear(client_key)
        return response

