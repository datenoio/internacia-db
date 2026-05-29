#!/usr/bin/env python3
"""Compare countries dataset manifest against a git baseline branch."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import typer

app = typer.Typer(help="Diff countries manifest against baseline branch")

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "datasets" / "countries.manifest.json"


def git_show_manifest(ref: str) -> dict | None:
    try:
        result = subprocess.run(
            ["git", "show", f"{ref}:data/datasets/countries.manifest.json"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=True,
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return None


@app.command()
def main(
    baseline_ref: str = typer.Option(
        "origin/main",
        "--baseline",
        help="Git ref for baseline manifest (e.g. origin/main)",
    ),
    fail_on_row_count_change: bool = typer.Option(
        True,
        "--fail-on-row-count-change/--allow-row-count-change",
    ),
) -> None:
    """Compare current countries.manifest.json to baseline ref."""
    if not MANIFEST.exists():
        typer.echo(f"ERROR: missing {MANIFEST}", err=True)
        raise typer.Exit(1)

    current = json.loads(MANIFEST.read_text(encoding="utf-8"))
    baseline = git_show_manifest(baseline_ref)

    if baseline is None:
        typer.echo(
            f"No baseline manifest at {baseline_ref}:data/datasets/countries.manifest.json; skipping diff"
        )
        raise typer.Exit(0)

    typer.echo(f"Baseline: {baseline_ref} (row_count={baseline.get('row_count')}, "
               f"schema_hash={baseline.get('schema_hash')})")
    typer.echo(f"Current:  row_count={current.get('row_count')}, "
               f"schema_hash={current.get('schema_hash')}")

    exit_code = 0
    if current.get("row_count") != baseline.get("row_count"):
        typer.echo(
            f"WARN: row_count changed {baseline.get('row_count')} -> {current.get('row_count')}",
            err=True,
        )
        if fail_on_row_count_change:
            exit_code = 1

    if current.get("schema_hash") != baseline.get("schema_hash"):
        typer.echo(
            f"NOTE: schema_hash changed {baseline.get('schema_hash')} -> {current.get('schema_hash')}"
        )

    raise typer.Exit(exit_code)


if __name__ == "__main__":
    app()
