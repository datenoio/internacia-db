#!/usr/bin/env python3
"""Compare dataset manifests against a git baseline branch."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import typer

app = typer.Typer(help="Diff dataset manifests against baseline branch")

ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = ROOT / "data" / "datasets"
DATASETS = ("countries", "intblocks")


def git_show_manifest(ref: str, dataset: str) -> dict | None:
    try:
        result = subprocess.run(
            ["git", "show", f"{ref}:data/datasets/{dataset}.manifest.json"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=True,
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return None


def diff_dataset(dataset: str, baseline_ref: str, fail_on_row_count_change: bool) -> int:
    manifest_path = DATASETS_DIR / f"{dataset}.manifest.json"
    if not manifest_path.exists():
        typer.echo(f"ERROR: missing {manifest_path}", err=True)
        return 1

    current = json.loads(manifest_path.read_text(encoding="utf-8"))
    baseline = git_show_manifest(baseline_ref, dataset)

    if baseline is None:
        typer.echo(f"No baseline manifest at {baseline_ref}:data/datasets/{dataset}.manifest.json; skipping diff")
        return 0

    typer.echo(
        f"[{dataset}] Baseline: {baseline_ref} (row_count={baseline.get('row_count')}, "
        f"schema_hash={baseline.get('schema_hash')})"
    )
    typer.echo(f"[{dataset}] Current:  row_count={current.get('row_count')}, schema_hash={current.get('schema_hash')}")

    exit_code = 0
    if current.get("row_count") != baseline.get("row_count"):
        typer.echo(
            f"WARN: [{dataset}] row_count changed {baseline.get('row_count')} -> {current.get('row_count')}",
            err=True,
        )
        if fail_on_row_count_change:
            exit_code = 1

    if current.get("schema_hash") != baseline.get("schema_hash"):
        typer.echo(
            f"NOTE: [{dataset}] schema_hash changed {baseline.get('schema_hash')} -> {current.get('schema_hash')}"
        )

    return exit_code


@app.command()
def main(
    baseline_ref: str = typer.Option(
        "origin/main",
        "--baseline",
        help="Git ref for baseline manifests (e.g. origin/main)",
    ),
    fail_on_row_count_change: bool = typer.Option(
        True,
        "--fail-on-row-count-change/--allow-row-count-change",
    ),
) -> None:
    """Compare current dataset manifests to the baseline ref."""
    exit_code = 0
    for dataset in DATASETS:
        exit_code = max(
            exit_code,
            diff_dataset(dataset, baseline_ref, fail_on_row_count_change),
        )
    raise typer.Exit(exit_code)


if __name__ == "__main__":
    app()
