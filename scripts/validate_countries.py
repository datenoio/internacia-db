#!/usr/bin/env python3
"""Backward-compatible CLI shim for country validation."""

from internacia_builder.validate.countries import *  # noqa: F403
from internacia_builder.validate.countries import app

if __name__ == "__main__":
    app()
