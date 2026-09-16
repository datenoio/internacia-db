"""Build identity (version, commit, frozen timestamp) and manifest sidecars."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow as pa
import typer

from internacia_builder.paths import project_root
from internacia_builder.schemas import schema_hash


def get_git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=project_root(),
            check=True,
        )
        return result.stdout.strip() or "unknown"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"

def get_dataset_version() -> str:
    changelog = project_root() / "CHANGELOG.md"
    if not changelog.exists():
        return "unknown"
    text = changelog.read_text(encoding="utf-8")
    dated = re.findall(r"## \[([^\]]+)\] - \d{4}-\d{2}-\d{2}", text)
    if dated:
        return dated[0]
    match = re.search(r"## \[([^\]]+)\]", text)
    return match.group(1) if match else "unknown"

# SPDX identifier for the dataset (data) license; see DATA_LICENSE / ATTRIBUTION.md.
DATA_LICENSE_SPDX = "CC-BY-4.0"

# Frozen per-build identity so every manifest, sidecar, and DuckDB _meta row
# emitted by a single build shares one build_date and git_commit.
_BUILD_DATE: str | None = None
_BUILD_COMMIT: str | None = None

def begin_build_context() -> None:
    """Freeze build_date and git_commit for the duration of one build."""
    global _BUILD_DATE, _BUILD_COMMIT
    _BUILD_DATE = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    _BUILD_COMMIT = get_git_commit()

def dataset_metadata(
    dataset: str,
    schema: pa.Schema,
    row_count: int,
) -> dict[str, Any]:
    """Build the canonical metadata record shared by manifests, the DuckDB
    ``_meta`` table, and Parquet ``.meta.json`` sidecars."""
    return {
        "dataset": dataset,
        "version": get_dataset_version(),
        "build_date": _BUILD_DATE or datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": _BUILD_COMMIT or get_git_commit(),
        "row_count": row_count,
        "schema_hash": schema_hash(schema),
        "data_license": DATA_LICENSE_SPDX,
    }

def write_manifest(
    output_dir: Path,
    dataset: str,
    schema: pa.Schema,
    row_count: int,
) -> None:
    manifest = dataset_metadata(dataset, schema, row_count)
    path = output_dir / f"{dataset}.manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"✓ Saved manifest: {path}")

def write_meta_sidecar(
    output_dir: Path,
    dataset: str,
    schema: pa.Schema,
    row_count: int,
) -> None:
    """Write a ``<dataset>.meta.json`` sidecar next to the Parquet export so
    Parquet-only consumers can read version info without the full manifest."""
    meta = dataset_metadata(dataset, schema, row_count)
    path = output_dir / f"{dataset}.meta.json"
    path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"✓ Saved meta sidecar: {path}")
