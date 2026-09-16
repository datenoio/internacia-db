from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Repository root (parent of internacia_builder/)."""
    return Path(__file__).resolve().parent.parent


def blocktypes_source_path(root: Path | None = None) -> Path:
    """Authoritative blocktypes taxonomy YAML (not generated)."""
    root = root or project_root()
    return root / "data" / "blocktypes" / "blocktypes.yaml"
