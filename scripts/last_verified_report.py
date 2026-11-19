#!/usr/bin/env python3
"""Print the last_verified KPI (never verified / overdue, overall and for tier 1)."""
import argparse
import json
import sys

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)
import yaml

from internacia_builder.freshness import kpi_markdown, last_verified_kpi, load_tier1
from internacia_builder.paths import project_root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--markdown", action="store_true", help="Markdown table (CI job summary)")
    args = parser.parse_args()
    root = project_root()
    config = yaml.safe_load((root / "data/schemas/intblocks_completeness.yaml").read_text()) or {}
    quality = config.get("quality") or {}
    records = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted((root / "data/intblocks").rglob("*.yaml"))]
    kpi = last_verified_kpi(
        records,
        load_tier1(root),
        max_age_months=int(quality.get("last_verified_max_age_months") or 12),
        tier1_max_age_months=int(quality.get("last_verified_tier1_max_age_months") or 6),
    )
    sys.stdout.write(kpi_markdown(kpi) if args.markdown else json.dumps(kpi, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
