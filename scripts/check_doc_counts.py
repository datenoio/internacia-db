#!/usr/bin/env python3
"""Assert consumer-facing docs advertise the current manifest row counts.

Run: python scripts/check_doc_counts.py
Exit 1 when a listed file omits a current count or still claims a stale
intblock headline count from pre-2.0.0 docs.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "data" / "datasets"

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
STALE_INTBLOCKS = (1078, 1076, 1071, 1070, 1065, 1021)


def load_counts() -> dict[str, int]:
    out: dict[str, int] = {}
    for name in ("countries", "intblocks", "blocktypes"):
        path = DATASETS / f"{name}.manifest.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        out[name] = int(payload["row_count"])
    return out


def check(root: Path | None = None) -> list[str]:
    base = root or ROOT
    counts = load_counts() if root is None else {
        name: int(
            json.loads((base / "data" / "datasets" / f"{name}.manifest.json").read_text())[
                "row_count"
            ]
        )
        for name in ("countries", "intblocks", "blocktypes")
    }
    errors: list[str] = []
    for rel, needed in REQUIRE.items():
        path = base / rel
        if not path.is_file():
            errors.append(f"missing {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for dataset in needed:
            n = counts[dataset]
            if str(n) not in text:
                errors.append(f"{rel}: missing current {dataset} count {n}")
        current_ib = counts["intblocks"]
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
        f"(countries={counts['countries']}, intblocks={counts['intblocks']}, "
        f"blocktypes={counts['blocktypes']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
