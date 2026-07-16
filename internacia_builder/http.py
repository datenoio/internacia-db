"""Shared HTTP helpers for enrichment scripts.

A single place for the JSON-over-HTTP client so enrichment tools share one
User-Agent, timeout, and decoding behavior instead of duplicating urllib code.
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any

DEFAULT_USER_AGENT = "Internacia-DB Enricher/1.0"
DEFAULT_TIMEOUT = 60


def fetch_json(
    url: str,
    *,
    user_agent: str = DEFAULT_USER_AGENT,
    timeout: int = DEFAULT_TIMEOUT,
) -> Any:
    """Fetch ``url`` and decode the response body as JSON.

    Uses ``utf-8-sig`` decoding to tolerate BOM-prefixed responses (some
    upstream APIs emit them).
    """
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - trusted upstream APIs
        return json.loads(resp.read().decode("utf-8-sig"))
