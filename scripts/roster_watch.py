#!/usr/bin/env python3
"""Compare tier-1 rosters with Wikidata; optionally sync one GitHub issue per organization."""
import argparse
import json
import os
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)

from internacia_builder.roster_watch import IssueSync, report_markdown, run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ids", nargs="*", help="intblock ids (default: tier 1 from data/watch/rosters.yaml)")
    parser.add_argument("--output", type=Path, help="write the JSON report here")
    parser.add_argument("--markdown", action="store_true", help="print a Markdown summary")
    parser.add_argument("--sync-issues", action="store_true", help="open/update/close issues (GITHUB_TOKEN, GITHUB_REPOSITORY)")
    args = parser.parse_args()
    as_of = date.today().isoformat()
    drifts = run(args.ids or None)
    if args.output:
        args.output.write_text(json.dumps([asdict(d) for d in drifts], indent=2) + "\n", encoding="utf-8")
    print(report_markdown(drifts, as_of) if args.markdown else json.dumps([asdict(d) for d in drifts], indent=2))
    if args.sync_issues:
        actions = IssueSync(os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"]).sync(drifts, as_of)
        print(f"issues: {json.dumps(actions)}", file=sys.stderr)
    failed = [d.id for d in drifts if d.error]
    if failed:
        print(f"could not check: {', '.join(failed)}", file=sys.stderr)
    return 1 if failed and len(failed) == len(drifts) else 0


if __name__ == "__main__":
    sys.exit(main())
