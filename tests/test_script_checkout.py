"""Scripts and tests use this checkout's internacia_builder, never another installed checkout."""

import ast
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from internacia_builder.paths import project_root

ROOT = project_root()
SCRIPTS = sorted((ROOT / "scripts").glob("*.py"))


def first_line(tree, predicate):
    lines = [
        node.lineno
        for node in tree.body
        if isinstance(node, ast.Import | ast.ImportFrom)
        and any(predicate(name) for name in ([node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names]))
    ]
    return min(lines, default=None)


@pytest.mark.parametrize("path", SCRIPTS, ids=lambda p: p.name)
def test_scripts_bootstrap_their_checkout_before_importing_the_package(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    package = first_line(tree, lambda name: (name or "").split(".")[0] == "internacia_builder")
    if package is None:
        return
    bootstrap = first_line(tree, lambda name: name == "_checkout")
    assert bootstrap is not None and bootstrap < package, f"{path.name}: import _checkout before internacia_builder"


def test_tests_import_this_checkout():
    import internacia_builder

    assert Path(internacia_builder.__file__).resolve().parent == ROOT / "internacia_builder"


def test_a_copied_checkout_uses_its_own_package_and_data(tmp_path):
    """A second checkout (like a git worktree) resolves to itself, even with this one installed."""
    copy = tmp_path / "checkout"
    for part in ("internacia_builder", "scripts"):
        shutil.copytree(ROOT / part, copy / part, ignore=shutil.ignore_patterns("__pycache__"))
    probe = copy / "scripts" / "probe_root.py"
    probe.write_text(
        "import _checkout  # noqa: F401\n"
        "import internacia_builder\n"
        "from internacia_builder.paths import project_root\n"
        "print(internacia_builder.__file__)\n"
        "print(project_root())\n",
        encoding="utf-8",
    )
    # The other checkout is importable too. Coverage variables are dropped: pytest-cov would
    # follow the child into tmp_path, measure it without this repo's branch=true config, and
    # fail to combine its data with the parent's.
    env = {k: v for k, v in os.environ.items() if not k.startswith(("COV_CORE_", "COVERAGE_"))}
    env["PYTHONPATH"] = str(ROOT)
    result = subprocess.run(
        [sys.executable, str(probe)], cwd=tmp_path, env=env, capture_output=True, text=True, check=True
    )
    module, root = result.stdout.splitlines()
    assert Path(module).resolve().is_relative_to(copy.resolve())
    assert Path(root).resolve() == copy.resolve()
