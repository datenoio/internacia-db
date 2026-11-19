"""Runtime dependencies are declared once in pyproject.toml and must agree everywhere else.

``requirements.txt`` (CI installs, pip-audit, Dependabot) and ``uv.lock`` (the resolved lock)
repeat the same pins. Dependabot's pip updates do not touch ``uv.lock``, so this test turns a
divergence into a CI failure: change a pin in ``pyproject.toml`` and ``requirements.txt``
together, then run ``uv lock``.
"""

import re
import tomllib

from internacia_builder.paths import project_root

ROOT = project_root()
PIN = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s;#]+)$")


def _canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _pins(lines) -> dict[str, str]:
    pins = {}
    for line in lines:
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        match = PIN.match(line)
        assert match, f"not an exact pin: {line!r}"
        pins[_canonical(match.group(1))] = match.group(2)
    return pins


def _pyproject() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_requirements_txt_matches_pyproject():
    declared = _pins(_pyproject()["project"]["dependencies"])
    required = _pins((ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines())
    assert required == declared


def test_uv_lock_resolves_exactly_the_declared_pins():
    project = _pyproject()["project"]
    declared = _pins(project["dependencies"])
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    packages = {_canonical(p["name"]): p for p in lock["package"]}
    root = packages[_canonical(project["name"])]
    assert root["version"] == project["version"], "run `uv lock` after a version bump"
    requires = {_canonical(r["name"]): r.get("specifier") for r in root["metadata"]["requires-dist"]}
    assert requires == {name: f"=={version}" for name, version in declared.items()}, "run `uv lock`"
    assert {name: packages[name]["version"] for name in declared} == declared
