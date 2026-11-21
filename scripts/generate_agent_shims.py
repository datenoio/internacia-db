#!/usr/bin/env python3
"""Generate the per-platform agent instruction files and llms-full.txt.

Hand-maintained: AGENTS.md, AGENTS.zh.md, llms.txt, llms.zh.txt and docs/agents/.
Generated: every file under templates/agent-shims/ (written to the same relative path,
with {{ fragment }} placeholders from templates/agent-shims/_fragments.yaml) and
llms-full.txt (llms.txt followed by templates/llms-full-extended.txt).
Run with --check in CI to fail when a generated file was edited by hand or is stale.
"""
import argparse
import re
import sys
from pathlib import Path

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)

from internacia_builder.yaml_io import safe_load

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates" / "agent-shims"
FRAGMENTS = TEMPLATES / "_fragments.yaml"
PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def _notice(rel: str) -> str:
    return (
        f"<!-- Generated from templates/agent-shims/{rel} by scripts/generate_agent_shims.py; "
        "edit the template and rerun. -->\n"
    )


def render(template: Path, fragments: dict[str, str]) -> str:
    rel = template.relative_to(TEMPLATES).as_posix()
    text = PLACEHOLDER.sub(lambda m: fragments[m.group(1)], template.read_text(encoding="utf-8"))
    if text.startswith("---\n"):
        end = text.index("\n---\n", 4) + 5
        return text[:end] + _notice(rel) + text[end:]
    return _notice(rel) + text


def outputs() -> dict[Path, str]:
    fragments = safe_load(FRAGMENTS.read_text(encoding="utf-8"))
    files = {
        ROOT / path.relative_to(TEMPLATES): render(path, fragments)
        for path in sorted(TEMPLATES.rglob("*"))
        if path.is_file() and path != FRAGMENTS
    }
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    extended = (ROOT / "templates" / "llms-full-extended.txt").read_text(encoding="utf-8")
    files[ROOT / "llms-full.txt"] = llms.rstrip("\n") + "\n\n" + extended
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if any output differs")
    args = parser.parse_args()
    stale = []
    for path, content in outputs().items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        if args.check:
            stale.append(path.relative_to(ROOT).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")
    if stale:
        print("Generated agent files are stale; run `python scripts/generate_agent_shims.py`:")
        for name in stale:
            print(f"  {name}")
        return 1
    if args.check:
        print("Agent files OK: generated files match their templates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
