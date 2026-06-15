from __future__ import annotations

import time
from typing import Any

import requests

DEFAULT_RATE_LIMIT_S = 0.1
DEFAULT_TIMEOUT_S = 60
DEFAULT_RETRIES = 3


class HttpClient:
    """Shared HTTP session with simple retry and rate limiting."""

    def __init__(
        self,
        *,
        rate_limit_s: float = DEFAULT_RATE_LIMIT_S,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        retries: int = DEFAULT_RETRIES,
        session: requests.Session | None = None,
    ) -> None:
        self.rate_limit_s = rate_limit_s
        self.timeout_s = timeout_s
        self.retries = retries
        self.session = session or requests.Session()
        self._last_request_at = 0.0

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.rate_limit_s:
            time.sleep(self.rate_limit_s - elapsed)

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout_s)
        last_exc: Exception | None = None
        for attempt in range(self.retries):
            self._throttle()
            try:
                response = self.session.request(method, url, **kwargs)
                self._last_request_at = time.monotonic()
                if response.status_code in {429, 500, 502, 503, 504} and attempt + 1 < self.retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                last_exc = exc
                if attempt + 1 >= self.retries:
                    raise
                time.sleep(0.5 * (attempt + 1))
        raise last_exc  # pragma: no cover

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", url, **kwargs)

    def get_json(self, url: str, **kwargs: Any) -> Any:
        return self.get(url, **kwargs).json()
