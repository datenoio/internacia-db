"""Put this checkout's root first on ``sys.path``.

``python scripts/<name>.py`` adds ``scripts/`` to ``sys.path``, not the repository root, so
``import internacia_builder`` finds whichever copy is installed. With an editable install from
another checkout (the main checkout, while working in a git worktree) a script would silently
run that checkout's code against that checkout's data. Scripts import this module before any
``internacia_builder`` import; ``tests/test_script_checkout.py`` enforces it.
"""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[1])

while ROOT in sys.path:
    sys.path.remove(ROOT)
sys.path.insert(0, ROOT)
