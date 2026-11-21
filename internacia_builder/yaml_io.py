"""Load YAML with libyaml's C parser when PyYAML was built with it.

``yaml.safe_load`` always uses the pure-Python parser, which is about eight times slower: on the
1,600 source records it cost a build ~30% of its time. ``CSafeLoader`` resolves the same safe
tags into the same Python objects, so the build's output is byte-for-byte the same.

Only loading goes through libyaml. Keep dumping on PyYAML's Python emitter: libyaml escapes
characters outside the Basic Multilingual Plane, so ``flag_emoji: 🇦🇩`` would be written as
``"\\U0001F1E6\\U0001F1E9"`` and the ``*.yaml.zst`` exports would change.

``ruff`` bans ``yaml.safe_load`` (``TID251`` in ``pyproject.toml``); use :func:`safe_load`.
"""

from __future__ import annotations

from typing import IO, Any

import yaml

SafeLoader: type[yaml.SafeLoader] = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def safe_load(stream: str | bytes | IO[str] | IO[bytes]) -> Any:
    """Parse one YAML document like ``yaml.safe_load``, through libyaml when available."""
    return yaml.load(stream, Loader=SafeLoader)  # noqa: S506  (a safe loader)
