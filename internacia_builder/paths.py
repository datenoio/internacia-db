from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Repository root (parent of internacia_builder/)."""
    return Path(__file__).resolve().parent.parent
