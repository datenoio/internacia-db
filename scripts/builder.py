#!/usr/bin/env python3
"""Thin CLI shim over :mod:`internacia_builder.build`.

Build/export logic now lives in the installable package. This shim keeps the
historical ``python scripts/builder.py ...`` entry point (and ``import builder``
in tests) working, from any directory and in any git worktree: it always uses this
checkout's package. The ``internacia-build`` console script runs the installed checkout.
"""

from __future__ import annotations

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)

from internacia_builder.build import *  # noqa: F401,F403 (re-export package API)
from internacia_builder.build import main

if __name__ == "__main__":
    main()
