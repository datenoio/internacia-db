#!/usr/bin/env python3
"""Check internal Markdown links in repository docs.

Scans tracked Markdown files for inline links of the form ``[text](target)`` and
verifies that relative link targets resolve to existing files or directories.
External links (http/https/mailto), in-page anchors, and template placeholders
are ignored. Exits non-zero when any internal link is broken.
"""

from __future__ import annotations

import re
from pathlib import Path

import typer

app = typer.Typer(add_completion=False, help="Validate internal Markdown links.")

REPO_ROOT = Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#", "<")
# Directories that are generated, vendored, historical, or intentionally excluded.
# Archived OpenSpec proposals and dev research are point-in-time snapshots whose
# relative links are not maintained.
SKIP_DIR_NAMES = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
}
# Path prefixes (from repo root) that are generated, historical, or snapshots.
SKIP_PATH_PREFIXES = {
    "data/_legacy",
    "dev",
    "openspec/changes/archive",
}


def _iter_markdown_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        rel = path.relative_to(root)
        if any(part in SKIP_DIR_NAMES for part in rel.parts):
            continue
        rel_posix = rel.as_posix()
        if any(rel_posix == d or rel_posix.startswith(f"{d}/") for d in SKIP_PATH_PREFIXES):
            continue
        files.append(path)
    return sorted(files)


def _target_exists(source: Path, target: str) -> bool:
    # Strip anchor and query fragments.
    clean = target.split("#", 1)[0].split("?", 1)[0].strip()
    if not clean:
        # Pure in-page anchor.
        return True
    candidate = (source.parent / clean).resolve()
    # Cannot verify links that escape the repository (e.g. sibling monorepo repos).
    try:
        candidate.relative_to(REPO_ROOT)
    except ValueError:
        return True
    return candidate.exists()


@app.command()
def main(
    root: Path = typer.Option(REPO_ROOT, help="Repository root to scan."),
) -> None:
    """Validate internal Markdown links and report broken targets."""
    root = root.resolve()
    broken: list[tuple[str, int, str]] = []
    checked = 0

    for md in _iter_markdown_files(root):
        lines = md.read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, start=1):
            for match in LINK_RE.finditer(line):
                target = match.group(1).strip()
                if target.startswith(SKIP_PREFIXES):
                    continue
                checked += 1
                if not _target_exists(md, target):
                    broken.append((md.relative_to(root).as_posix(), lineno, target))

    if broken:
        typer.echo(f"Broken internal Markdown links ({len(broken)}):")
        for rel, lineno, target in broken:
            typer.echo(f"  {rel}:{lineno} -> {target}")
        raise typer.Exit(code=1)

    typer.echo(f"Checked {checked} internal links across Markdown files: all valid.")


if __name__ == "__main__":
    app()
