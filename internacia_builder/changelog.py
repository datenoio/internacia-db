"""Changelog fragments: one file per pull request under ``changelog.d/``.

Pull requests do not edit ``CHANGELOG.md``: every one of them used to insert its entry at
the top of ``### Added`` under ``[Unreleased]``, so any two open pull requests conflicted.
Each pull request adds ``changelog.d/<slug>.md`` instead, holding only Keep a Changelog
subsections. The release train merges the ``[Unreleased]`` body and every fragment into
the dated release section (``release.apply_version``) and deletes the fragments.
"""

from __future__ import annotations

import re
from pathlib import Path

FRAGMENTS_DIR = "changelog.d"
README = "README.md"

# Keep a Changelog subsections, in the order a release section lists them.
SECTIONS = ("Added", "Changed", "Deprecated", "Removed", "Fixed", "Security")

_HEADING = re.compile(r"^### (.+?)\s*$")
# A running dataset total such as "(1304 intblocks)": it is stale as soon as another
# pull request merges, and it makes every entry conflict with its neighbours.
_RUNNING_TOTAL = re.compile(r"\(\d+ (?:intblocks|countries|blocktypes|records)\)")


def fragment_paths(root: Path) -> list[Path]:
    directory = root / FRAGMENTS_DIR
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.glob("*.md") if p.name != README)


def split_sections(text: str) -> tuple[str, dict[str, list[str]]]:
    """Text before the first ``### `` heading, and each subsection's body in order."""
    preamble: list[str] = []
    sections: dict[str, list[str]] = {}
    current: list[str] | None = None
    for line in text.splitlines():
        match = _HEADING.match(line)
        if match:
            current = sections.setdefault(match.group(1), [])
            continue
        (preamble if current is None else current).append(line)
    return "\n".join(preamble).strip("\n"), {name: _block(lines) for name, lines in sections.items()}


def _block(lines: list[str]) -> list[str]:
    text = "\n".join(lines).strip("\n")
    return [text] if text.strip() else []


def check_fragment(path: Path) -> list[str]:
    """Problems with one fragment; an empty list means it can be merged."""
    text = path.read_text(encoding="utf-8")
    name = f"{FRAGMENTS_DIR}/{path.name}"
    problems: list[str] = []
    preamble, sections = split_sections(text)
    if preamble.strip():
        problems.append(f"{name}: text before the first '### ' subsection")
    if not sections:
        problems.append(f"{name}: no '### ' subsection ({', '.join(SECTIONS)})")
    for section, blocks in sections.items():
        if section not in SECTIONS:
            problems.append(f"{name}: unknown subsection '### {section}' (use {', '.join(SECTIONS)})")
        if not blocks:
            problems.append(f"{name}: empty subsection '### {section}'")
    if re.search(r"(?m)^#{1,2} ", text):
        problems.append(f"{name}: '#' or '##' headings belong to CHANGELOG.md, not to a fragment")
    for total in _RUNNING_TOTAL.findall(text):
        problems.append(f"{name}: running dataset total {total}; the release adds a data-change summary")
    return problems


def _join(blocks: list[str]) -> str:
    out = ""
    for block in blocks:
        if out:
            out += "\n" if block.startswith("- ") and out.splitlines()[-1].startswith(("- ", "  ")) else "\n\n"
        out += block
    return out


def merge(unreleased: str, fragments: list[str]) -> str:
    """One release body from the ``[Unreleased]`` body and the fragment texts.

    Subsections come in Keep a Changelog order (unknown ones from ``[Unreleased]`` after
    them, in their original order); within a subsection, ``[Unreleased]`` entries come
    first, then each fragment's, in the order given.
    """
    preamble, merged = split_sections(unreleased)
    for text in fragments:
        for section, blocks in split_sections(text)[1].items():
            merged.setdefault(section, []).extend(blocks)
    order = [s for s in SECTIONS if s in merged] + [s for s in merged if s not in SECTIONS]
    parts = [preamble] if preamble else []
    parts.extend(f"### {section}\n\n{_join(merged[section])}" for section in order if merged[section])
    return "\n\n".join(parts)
