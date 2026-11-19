"""Test bootstrap.

``pythonpath = ["."]`` in ``pyproject.toml`` puts this checkout first, so tests import
its ``internacia_builder`` even when another checkout is installed in editable mode (a
git worktree next to the main checkout). Scripts under ``scripts/`` are not part of the
package (see the deferred ``refactor-scripts-package`` OpenSpec change), so tests that
exercise them import via this path insert.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def pytest_sessionstart(session):
    """Build data/datasets first if it holds only the committed descriptors.

    Generated exports are not committed (D3). CI points INTERNACIA_DATASETS_DIR at its
    own fresh build, so this only runs in a fresh local checkout."""
    if os.environ.get("INTERNACIA_DATASETS_DIR") or (ROOT / "data/datasets/internacia.duckdb").is_file():
        return
    print("\ndata/datasets has no build yet; running scripts/builder.py build", file=sys.stderr)
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/builder.py"), "build"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
    )
