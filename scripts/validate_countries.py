#!/usr/bin/env python3
"""Backward-compatible CLI shim for country validation."""

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)

from internacia_builder.validate.countries import *  # noqa: F403
from internacia_builder.validate.countries import app

if __name__ == "__main__":
    app()
