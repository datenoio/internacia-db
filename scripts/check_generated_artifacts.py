#!/usr/bin/env python3
"""Verify that committed dataset artifacts are internally consistent.

Checks, for each dataset (countries, intblocks, blocktypes):

1. Primary-key parity: JSONL, YAML, Parquet, and DuckDB exports contain the
   same primary-key set and row count, and that set matches the YAML source ids.
2. Manifest row counts match actual exported rows.
3. Single build identity: all manifests, ``*.meta.json`` sidecars, and DuckDB
   ``_meta`` rows agree on ``version``, ``git_commit``, and ``build_date``.

Exits non-zero on any mismatch.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import duckdb
import pyarrow.parquet as pq
import typer
import yaml
import zstandard

app = typer.Typer(add_completion=False, help="Check generated dataset artifact consistency.")

ROOT = Path(__file__).resolve().parents[1]
DATASETS = {
    "countries": {"key": "code", "source": "data/countries", "glob": "*.yaml"},
    "intblocks": {"key": "id", "source": "data/intblocks", "glob": "*/*.yaml"},
    "blocktypes": {"key": "id", "source": None, "glob": None},
}


def _source_ids(spec: dict, root: Path) -> set[str] | None:
    if not spec["source"]:
        return None
    base = root / spec["source"]
    ids: set[str] = set()
    for path in base.glob(spec["glob"]):
        rec = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(rec, dict) and rec.get(spec["key"]) is not None:
            ids.add(str(rec[spec["key"]]))
    return ids


def _jsonl_ids(path: Path, key: str) -> set[str]:
    dctx = zstandard.ZstdDecompressor()
    ids: set[str] = set()
    with path.open("rb") as f:
        text = io.TextIOWrapper(dctx.stream_reader(f), encoding="utf-8")
        for line in text:
            line = line.strip()
            if line:
                ids.add(str(json.loads(line)[key]))
    return ids


def _yaml_zst_ids(path: Path, key: str) -> set[str]:
    dctx = zstandard.ZstdDecompressor()
    with path.open("rb") as f:
        data = yaml.safe_load(dctx.stream_reader(f))
    return {str(r[key]) for r in (data or [])}


def _parquet_ids(path: Path, key: str) -> set[str]:
    table = pq.read_table(path, columns=[key])
    return {str(v) for v in table.column(key).to_pylist()}


@app.command()
def main(
    datasets_dir: Path = typer.Option(ROOT / "data" / "datasets", help="Committed datasets directory."),
    root: Path = typer.Option(ROOT, help="Repository root for source YAML."),
) -> None:
    """Validate cross-format and build-identity consistency of committed artifacts."""
    datasets_dir = datasets_dir.resolve()
    root = root.resolve()
    problems: list[str] = []
    identities: dict[str, dict] = {}

    duck = duckdb.connect(str(datasets_dir / "internacia.duckdb"), read_only=True)
    meta_rows = {
        row[0]: {"version": row[1], "build_date": row[2], "git_commit": row[3]}
        for row in duck.execute("SELECT dataset, version, build_date, git_commit FROM _meta").fetchall()
    }

    for name, spec in DATASETS.items():
        key = spec["key"]
        format_ids = {
            "jsonl": _jsonl_ids(datasets_dir / f"{name}.jsonl.zst", key),
            "yaml": _yaml_zst_ids(datasets_dir / f"{name}.yaml.zst", key),
            "parquet": _parquet_ids(datasets_dir / f"{name}.parquet", key),
            "duckdb": {str(r[0]) for r in duck.execute(f"SELECT {key} FROM {name}").fetchall()},
        }
        source_ids = _source_ids(spec, root)
        reference = format_ids["parquet"]

        for fmt, ids in format_ids.items():
            if ids != reference:
                only_ref = sorted(reference - ids)[:10]
                only_fmt = sorted(ids - reference)[:10]
                problems.append(
                    f"[{name}] {fmt} id set differs from parquet: "
                    f"missing={only_ref} extra={only_fmt}"
                )
        if source_ids is not None and source_ids != reference:
            problems.append(
                f"[{name}] source id set differs from exports: "
                f"missing_from_export={sorted(source_ids - reference)[:10]} "
                f"extra_in_export={sorted(reference - source_ids)[:10]}"
            )

        manifest_path = datasets_dir / f"{name}.manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("row_count") != len(reference):
                problems.append(
                    f"[{name}] manifest row_count {manifest.get('row_count')} != actual {len(reference)}"
                )
            identities[f"{name}.manifest"] = {
                k: manifest.get(k) for k in ("version", "build_date", "git_commit")
            }
        else:
            problems.append(f"[{name}] missing manifest {manifest_path.name}")

        sidecar_path = datasets_dir / f"{name}.meta.json"
        if sidecar_path.exists():
            sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
            identities[f"{name}.meta"] = {k: sidecar.get(k) for k in ("version", "build_date", "git_commit")}
        if name in meta_rows:
            identities[f"{name}._meta"] = meta_rows[name]

    duck.close()

    distinct = {json.dumps(v, sort_keys=True) for v in identities.values()}
    if len(distinct) > 1:
        problems.append("build identity differs across artifacts:")
        for label, ident in sorted(identities.items()):
            problems.append(f"    {label}: {ident}")

    if problems:
        typer.echo("Artifact consistency check FAILED:")
        for p in problems:
            typer.echo(f"  {p}")
        raise typer.Exit(code=1)

    typer.echo(
        "Artifact consistency OK: "
        + ", ".join(f"{n}={len(_parquet_ids(datasets_dir / f'{n}.parquet', s['key']))}" for n, s in DATASETS.items())
        + " (all formats + source agree; single build identity)"
    )


if __name__ == "__main__":
    app()
