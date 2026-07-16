#!/usr/bin/env python3
"""Thin CLI shim over :mod:`internacia_builder.build`.

Build/export logic now lives in the installable package. This shim keeps the
historical ``python scripts/builder.py ...`` entry point (and ``import builder``
in tests) working. Prefer the ``internacia-build`` console script.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure imports work even when invoked outside the repo root, e.g.:
#   python /path/to/internacia-db/scripts/builder.py
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from internacia_builder.build import *  # noqa: E402,F401,F403 (re-export package API)
from internacia_builder.build import main  # noqa: E402

if __name__ == "__main__":
    main()
