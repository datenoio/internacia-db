#!/usr/bin/env python3
"""Report intblock include names that differ from canonical country names."""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from pathlib import Path

import typer
import yaml

app = typer.Typer(help="Audit intblock include name vs country canonical name mismatches")

ROOT = Path(__file__).resolve().parents[1]
COUNTRIES_DIR = ROOT / "data" / "countries"
INTBLOCKS_DIR = ROOT / "data" / "intblocks"


def normalize_name(name: str) -> str:
    text = unicodedata.normalize("NFKD", name)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    return text


def load_canonical_names() -> dict[str, str]:
    names: dict[str, str] = {}
    for path in COUNTRIES_DIR.glob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        code = data.get("code")
        if code:
            names[str(code)] = str(data.get("name", ""))
    return names


@app.command()
def main(
    limit: int = typer.Option(20, help="Max example mismatches to print"),
) -> None:
    """Log name mismatches (warn-only, exit 0)."""
    canonical = load_canonical_names()
    mismatches: list[tuple[str, str, str, str]] = []
    pair_counts: Counter[tuple[str, str]] = Counter()

    for path in sorted(INTBLOCKS_DIR.rglob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rel = str(path.relative_to(ROOT))
        for inc in data.get("includes") or []:
            if not isinstance(inc, dict) or inc.get("type") != "country":
                continue
            cid = str(inc.get("id", "")).strip()
            if len(cid) != 2 or not cid.isalpha():
                continue
            include_name = str(inc.get("name", "")).strip()
            canon = canonical.get(cid.upper(), "")
            if not include_name or not canon:
                continue
            if normalize_name(include_name) == normalize_name(canon):
                continue
            mismatches.append((rel, cid, include_name, canon))
            pair_counts[(include_name, canon)] += 1

    typer.echo(f"Include name mismatches: {len(mismatches)} total")
    typer.echo(f"Unique alias pairs: {len(pair_counts)}")
    for (inc_name, canon), count in pair_counts.most_common(limit):
        typer.echo(f"  {count:4d}x  include={inc_name!r}  canonical={canon!r}")

    raise typer.Exit(0)


if __name__ == "__main__":
    app()
