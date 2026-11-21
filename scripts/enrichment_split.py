#!/usr/bin/env python3
"""Split an enrichment run into one pull request per source.

    # after enrich_countries.py / enrich_intblocks.py changed the working tree:
    python scripts/enrichment_split.py snapshot --output enrichment.json
    # on a clean checkout of the same commit, once per source:
    python scripts/enrichment_split.py apply --source wb-indicators enrichment.json --pr-body body.md

``snapshot`` records the changed records before and after enrichment and lists the sources
with changes. ``apply`` writes only that source's changes and reports whether the pull request
may merge without review (data/schemas/enrichment_sources.yaml, docs/enrichment.md).
Both write their results to ``GITHUB_OUTPUT`` when it is set.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)
import typer

from internacia_builder import enrichment_sources as es
from internacia_builder.enrichment import write_enriched_yaml
from internacia_builder.paths import project_root
from internacia_builder.validate.registry import load_yaml
from internacia_builder.yaml_io import safe_load

app = typer.Typer(help=__doc__.splitlines()[0])
SOURCE_DIRS = ("data/countries", "data/intblocks")
SAMPLE_LIMIT = 40


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout


def _output(**values: str) -> None:
    if path := os.environ.get("GITHUB_OUTPUT"):
        with open(path, "a", encoding="utf-8") as f:
            f.writelines(f"{key}={value}\n" for key, value in values.items())


@app.command()
def snapshot(output: Path = typer.Option(..., "--output", help="Snapshot JSON to write")) -> None:
    """Record the records enrichment changed (before and after) and the sources involved."""
    root = project_root()
    paths = _git(root, "diff", "--name-only", "HEAD", "--", *SOURCE_DIRS).split()
    paths += _git(root, "ls-files", "--others", "--exclude-standard", "--", *SOURCE_DIRS).split()
    base: es.Records = {}
    enriched: es.Records = {}
    for rel in sorted(set(p for p in paths if p.endswith(".yaml"))):
        before = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=root, capture_output=True, text=True)
        if before.returncode == 0:
            base[rel] = safe_load(before.stdout) or {}
        if (root / rel).exists():
            enriched[rel] = load_yaml(root / rel) or {}
    policy = es.load_policy(root)
    sources = sorted(es.split(base, enriched, policy))
    output.write_text(json.dumps({"base": base, "enriched": enriched}, ensure_ascii=False, default=str))
    typer.echo(f"{len(enriched)} changed record(s); sources: {', '.join(sources) or 'none'}")
    _output(sources=json.dumps(sources), changed=str(bool(sources)).lower())


@app.command()
def apply(
    snapshot_file: Path = typer.Argument(..., help="JSON written by `snapshot`"),
    source: str = typer.Option(..., "--source", help="Source name from enrichment_sources.yaml"),
    pr_body: Path = typer.Option(None, "--pr-body", help="Write the pull request body here"),
) -> None:
    """Write one source's changes to the working tree and decide whether review is needed."""
    root = project_root()
    data = json.loads(snapshot_file.read_text(encoding="utf-8"))
    policy = es.load_policy(root)
    if source not in policy.sources:
        raise typer.BadParameter(f"unknown source {source!r}")
    base: es.Records = data["base"]
    patched = es.split(base, data["enriched"], policy).get(source, {})
    for rel, record in sorted(patched.items()):
        write_enriched_yaml(root / rel, record, es.dataset_of(rel))
    reasons = es.review_reasons(source, base, patched, policy)
    spec = policy.sources[source]
    typer.echo(f"{spec.title}: {len(patched)} record(s); " + ("needs review" if reasons else "auto-merge"))
    for reason in reasons[:SAMPLE_LIMIT]:
        typer.echo(f"  {reason}")
    if pr_body:
        pr_body.write_text(_body(spec, base, patched, reasons), encoding="utf-8")
    _output(auto_merge=str(not reasons).lower(), records=str(len(patched)), title=spec.title)


def _short(value: Any) -> str:
    if isinstance(value, dict) and "value" in value:
        value = value["value"]
    text = json.dumps(value, ensure_ascii=False, default=str)
    return text if len(text) <= 60 else text[:57] + "..."


def _body(spec: es.Source, base: es.Records, patched: es.Records, reasons: list[str]) -> str:
    lines = [
        f"Automated monthly enrichment: **{spec.title}** ({len(patched)} record(s)), from "
        "`enrichment-check.yml`. Only this source's fields and their provenance change.",
        "",
    ]
    if reasons:
        lines += ["**Needs review**:", *(f"- {r}" for r in reasons[:SAMPLE_LIMIT])]
        if len(reasons) > SAMPLE_LIMIT:
            lines.append(f"- … and {len(reasons) - SAMPLE_LIMIT} more")
    else:
        lines.append(
            "Every change fills an empty value, only adds items, or stays within the thresholds in "
            "`data/schemas/enrichment_sources.yaml`, so this merges automatically once CI passes."
        )
    changes = []
    for rel, after in sorted(patched.items()):
        before = base.get(rel) or {}
        for name in sorted(es.changed_fields(before, after)):
            if before.get(name) != after.get(name):
                changes.append(f"- `{es.record_id(rel, after)}.{name}`: {_short(before.get(name))} → {_short(after.get(name))}")
    lines += ["", f"### Changes ({len(changes)})", "", *changes[:SAMPLE_LIMIT]]
    if len(changes) > SAMPLE_LIMIT:
        lines.append(f"- … and {len(changes) - SAMPLE_LIMIT} more (see the diff)")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    app()
