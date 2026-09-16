"""Test bootstrap.

``internacia_builder`` is expected to be installed (``pip install -e .``), so no
repository-root ``sys.path`` insert is needed. Scripts under ``scripts/`` are not
part of the package (see the deferred ``refactor-scripts-package`` OpenSpec
change), so tests that exercise them import via this path insert.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
