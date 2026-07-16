"""Data-quality analysis entry point.

The analyzer implementation currently lives alongside the build orchestration in
:mod:`internacia_builder.build`. This module exposes it under a stable name so it
can be imported and run independently of the build CLI.
"""

from __future__ import annotations

import typer

from internacia_builder.build import analyze_quality

app = typer.Typer(help="Run internacia-db data-quality analysis")
app.command("analyze-quality")(analyze_quality)


def main() -> None:
    """Console entry point for the quality analyzer."""
    app()


if __name__ == "__main__":
    main()
