#!/usr/bin/env python3
"""Compare the built dataset manifests with a git baseline ref.

Build manifests are not committed, so the baseline comes from the ref's sources: its
record counts from the source YAML and its schema hashes from the committed contract.json.
The current side is the build directory (INTERNACIA_DATASETS_DIR, else data/datasets).
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)
import typer

from internacia_builder.contract import CONTRACT_FILE
from internacia_builder.paths import datasets_dir, project_root
from internacia_builder.release import Snapshot, extract_sources

app = typer.Typer(help="Diff dataset manifests against baseline branch")

DATASETS = ("countries", "intblocks", "blocktypes")


def baseline_counts(root: Path, ref: str) -> dict[str, int]:
    """Record count of each dataset in the sources at ``ref``."""
    with tempfile.TemporaryDirectory() as tmp:
        snapshot = Snapshot.load(extract_sources(root, ref, Path(tmp)))
    return {name: len(getattr(snapshot, name)) for name in DATASETS}


def baseline_schema_hashes(root: Path, ref: str) -> dict[str, str]:
    """Schema hash of each table in the contract.json committed at ``ref``."""
    result = subprocess.run(
        ["git", "show", f"{ref}:data/datasets/{CONTRACT_FILE}"], cwd=root, capture_output=True, check=False
    )
    if result.returncode != 0:
        return {}
    return {t["name"]: t.get("schema_hash") for t in json.loads(result.stdout)["tables"]}


def diff_dataset(
    dataset: str,
    current: dict,
    baseline_rows: int,
    baseline_hash: str | None,
    baseline_ref: str,
    fail_on_row_count_change: bool,
) -> int:
    typer.echo(f"[{dataset}] Baseline: {baseline_ref} (row_count={baseline_rows}, schema_hash={baseline_hash})")
    typer.echo(f"[{dataset}] Current:  row_count={current.get('row_count')}, schema_hash={current.get('schema_hash')}")

    exit_code = 0
    if current.get("row_count") != baseline_rows:
        typer.echo(f"WARN: [{dataset}] row_count changed {baseline_rows} -> {current.get('row_count')}", err=True)
        if fail_on_row_count_change:
            exit_code = 1

    if baseline_hash and current.get("schema_hash") != baseline_hash:
        typer.echo(f"NOTE: [{dataset}] schema_hash changed {baseline_hash} -> {current.get('schema_hash')}")

    return exit_code


@app.command()
def main(
    baseline_ref: str = typer.Option(
        "origin/main",
        "--baseline",
        help="Git ref to compare with (e.g. origin/main)",
    ),
    fail_on_row_count_change: bool = typer.Option(
        True,
        "--fail-on-row-count-change/--allow-row-count-change",
    ),
) -> None:
    """Compare the built dataset manifests to the baseline ref."""
    root = project_root()
    built = datasets_dir()
    current = {}
    for dataset in DATASETS:
        path = built / f"{dataset}.manifest.json"
        if not path.exists():
            typer.echo(f"ERROR: missing {path}; run `python scripts/builder.py build` first", err=True)
            raise typer.Exit(1)
        current[dataset] = json.loads(path.read_text(encoding="utf-8"))
    try:
        rows = baseline_counts(root, baseline_ref)
    except subprocess.CalledProcessError:
        typer.echo(f"No sources at {baseline_ref}; skipping diff")
        raise typer.Exit(0) from None
    hashes = baseline_schema_hashes(root, baseline_ref)

    exit_code = 0
    for dataset in DATASETS:
        exit_code = max(
            exit_code,
            diff_dataset(
                dataset, current[dataset], rows[dataset], hashes.get(dataset), baseline_ref, fail_on_row_count_change
            ),
        )
    raise typer.Exit(exit_code)


if __name__ == "__main__":
    app()
