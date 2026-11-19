#!/usr/bin/env python3
"""Plan the next dataset release and, with --apply, write the version bump.

Without --apply this only reports what changed since the last ``vX.Y.Z`` tag and which
version would come next (see internacia_builder.release for the rules). With --apply it dates
the CHANGELOG entry, adds the data-change summary, writes the version to pyproject.toml,
internacia_builder/__init__.py, CITATION.cff and uv.lock, and rebuilds the committed
descriptors in data/datasets.

Exit codes: 0 release planned (or applied), 3 nothing to release, 4 MAJOR changes found
(the release train stops; release by hand per docs/versioning-policy.md).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)

from internacia_builder import release
from internacia_builder.paths import project_root

NOTHING, MAJOR = 3, 4


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--previous", help="Release tag to compare with (default: the latest vX.Y.Z tag)")
    parser.add_argument("--level", choices=("patch", "minor"), help="Release at least this level")
    parser.add_argument("--apply", action="store_true", help="Write the version bump and rebuild descriptors")
    parser.add_argument("--summary", type=Path, help="Write the release PR body (Markdown) here")
    parser.add_argument("--diff", type=Path, help="Write the record-level data diff (JSON) here")
    args = parser.parse_args()

    root = project_root()
    plan = release.plan_release(root, args.previous)
    level = plan.level
    if args.level and level in ("none", "patch") and release.LEVELS.index(args.level) > release.LEVELS.index(level):
        level = args.level
    version = None if level in ("none", "major") else release.next_version(plan.previous, level)
    summary = release.render_summary(plan)

    print(f"Previous release: {plan.previous or 'none'}")
    print(f"Changed files since then: {len(plan.changed_paths)}")
    print(f"Level: {level}" + (f" -> v{version}" if version else ""))
    for name in ("major", "minor"):
        for reason in plan.reasons.get(name, []):
            print(f"  {name}: {reason}")
    if summary:
        print(summary)
    if args.diff and plan.diff is not None:
        args.diff.write_text(json.dumps(plan.diff, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    outputs = {"level": level, "version": version or "", "previous": plan.previous or ""}
    if args.summary:
        args.summary.write_text(_pr_body(plan, level, version, summary), encoding="utf-8")
    if github_output := os.environ.get("GITHUB_OUTPUT"):
        with open(github_output, "a", encoding="utf-8") as f:
            f.writelines(f"{key}={value}\n" for key, value in outputs.items())

    if level == "none":
        print("Nothing to release.")
        return NOTHING
    if level == "major":
        print("MAJOR changes found; the release train does not release them.", file=sys.stderr)
        return MAJOR
    if args.apply:
        released = datetime.now(UTC).date()
        for path in release.apply_version(root, version, released, summary):
            print(f"Updated {path.relative_to(root)}")
        subprocess.run([sys.executable, str(root / "scripts/builder.py"), "build"], cwd=root, check=True)
    return 0


def _pr_body(plan: release.Plan, level: str, version: str | None, summary: str) -> str:
    if level == "major":
        head = (
            f"The release train found changes since {plan.previous} that need a MAJOR release, "
            "which is not automated (docs/versioning-policy.md):\n\n"
            + "\n".join(f"- {reason}" for reason in plan.reasons["major"])
        )
    elif level == "none":
        head = f"Nothing that affects the datasets changed since {plan.previous}."
    else:
        head = (
            f"Release **v{version}** ({level}, previous {plan.previous}).\n\n"
            "Merging this pull request tags the merge commit, which runs `release.yml`: gates, "
            "SDK contract suite, Release assets, Hugging Face and Zenodo, then notifies "
            "internacia-python and internacia-api."
        )
    body = [head]
    if summary:
        body.append("## Data changes\n\n" + summary)
    return "\n\n".join(body) + "\n"


if __name__ == "__main__":
    sys.exit(main())
