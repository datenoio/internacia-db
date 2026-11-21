#!/usr/bin/env python3
"""Assert consumer-facing docs advertise the current manifest row counts.

Run: python scripts/check_doc_counts.py (after `python scripts/builder.py build`; the
manifests are build outputs read from INTERNACIA_DATASETS_DIR, else data/datasets).

Country and blocktype counts are stated exactly. The intblock count is stated rounded
down to the hundred and written as ``N+`` (1304 -> ``1300+``; see
internacia_builder/doc_counts.py), so adding records does not touch ten documentation
files until the count crosses a hundred.

Exit 1 when a listed file omits a current count, states an older rounded intblock count,
or still claims a stale intblock headline count from pre-2.0.0 docs.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)

from internacia_builder.doc_counts import documented_count, intblocks_floor
from internacia_builder.paths import datasets_dir

ROOT = Path(__file__).resolve().parents[1]

# Files that publish "current dataset size" to humans and agents.
# Historical planning docs and CHANGELOG are excluded on purpose.
REQUIRE: dict[str, tuple[str, ...]] = {
    "README.md": ("countries", "intblocks", "blocktypes"),
    "AGENTS.md": ("countries", "intblocks", "blocktypes"),
    "AGENTS.zh.md": ("countries", "intblocks", "blocktypes"),
    "llms.txt": ("countries", "intblocks", "blocktypes"),
    "llms-full.txt": ("countries", "intblocks", "blocktypes"),
    "llms.zh.txt": ("countries", "intblocks", "blocktypes"),
    "docs/ai-consumers.md": ("countries", "intblocks", "blocktypes"),
    "docs/getting-started.md": ("countries", "intblocks", "blocktypes"),
    "docs/architecture.md": ("countries", "intblocks", "blocktypes"),
    "docs/country-code-policy.md": ("countries",),
}

# Headline intblock totals from retired releases — must not reappear as current.
STALE_INTBLOCKS = (1078, 1076, 1071, 1070, 1065, 1037, 1021)


def load_counts(datasets: Path | None = None) -> dict[str, int]:
    directory = datasets or datasets_dir()
    out: dict[str, int] = {}
    for name in ("countries", "intblocks", "blocktypes"):
        payload = json.loads((directory / f"{name}.manifest.json").read_text(encoding="utf-8"))
        out[name] = int(payload["row_count"])
    return out


def advertised(dataset: str, count: int) -> str:
    return documented_count(dataset, count)


def check(root: Path | None = None, counts: dict[str, int] | None = None) -> list[str]:
    base = root or ROOT
    counts = counts or load_counts()
    current_ib = counts["intblocks"]
    errors: list[str] = []
    for rel, needed in REQUIRE.items():
        path = base / rel
        if not path.is_file():
            errors.append(f"missing {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for dataset in needed:
            expected = advertised(dataset, counts[dataset])
            if expected not in text:
                errors.append(f"{rel}: missing current {dataset} count {expected}")
        for older in range(1000, intblocks_floor(current_ib), 100):
            if re.search(rf"\b{older}\+", text):
                errors.append(f"{rel}: older rounded intblock count {older}+ (current {advertised('intblocks', current_ib)})")
        for stale in STALE_INTBLOCKS:
            if stale == current_ib:
                continue
            if re.search(rf"\*\*{stale}\*\*|\b{stale}\s+intblocks\b", text, re.I):
                errors.append(f"{rel}: stale intblock count {stale}")
    return errors


def main() -> int:
    errors = check()
    if errors:
        print("Doc count drift:", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1
    counts = load_counts()
    print(
        "OK: consumer docs match manifests "
        f"(countries={counts['countries']}, intblocks={advertised('intblocks', counts['intblocks'])}, "
        f"blocktypes={counts['blocktypes']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
