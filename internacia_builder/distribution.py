"""Validate published bundles and prepare the intentionally partial HF mirror."""
from __future__ import annotations

import json
import re
import shutil
import tomllib
from pathlib import Path

from internacia_builder import __version__
from internacia_builder.contract import CONTRACT_FILE, contract_version, file_digest, verify_checksums
from internacia_builder.manifest import get_dataset_version
from internacia_builder.paths import project_root
from internacia_builder.yaml_io import safe_load


def validate_package(root: Path, package: dict | None = None) -> None:
    package = package if package is not None else json.loads((root / "datapackage.json").read_text())
    resources = package.get("resources") or []
    names = [r["name"] for r in resources]
    if not names or len(names) != len(set(names)):
        raise ValueError("Data package must have resources with unique names")
    for resource in resources:
        path = root / resource["path"]
        if not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError(f"Unresolvable data package path: {resource['path']}")
        digest = file_digest(path)
        if resource.get("bytes") != digest["bytes"] or resource.get("hash") != f"sha256:{digest['sha256']}":
            raise ValueError(f"Data package bytes/hash do not match {resource['path']}")


def validate_bundle(root: Path) -> None:
    """Validate the data package and ``SHA256SUMS`` of a complete release bundle."""
    validate_package(root)
    problems = verify_checksums(root)
    if problems:
        raise ValueError("; ".join(problems))


def check_release_version(version: str, datasets: Path) -> None:
    expected = version.removeprefix("v")
    root = project_root()
    package_version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    citation = safe_load((root / "CITATION.cff").read_text(encoding="utf-8")) or {}
    values = {
        "CHANGELOG": get_dataset_version(),
        "package": __version__,
        "pyproject": package_version,
        "CITATION.cff": str(citation.get("version")),
    }
    for path in datasets.glob("*.manifest.json"):
        values[path.name] = json.loads(path.read_text())["version"]
    contract_path = datasets / CONTRACT_FILE
    contract = json.loads(contract_path.read_text()) if contract_path.is_file() else {}
    values[CONTRACT_FILE] = contract.get("dataset_version", "missing")
    values[f"{CONTRACT_FILE} contract_version"] = (
        expected if contract.get("contract_version") == contract_version(expected) else contract.get("contract_version")
    )
    if not list(datasets.glob("*.manifest.json")) or any(value != expected for value in values.values()):
        raise ValueError(f"Release {version} disagrees with source/artifact versions: {values}")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    dated = re.search(rf"^## \[{re.escape(expected)}\] - (\d{{4}}-\d{{2}}-\d{{2}})", changelog, re.MULTILINE)
    released = str(citation.get("date-released"))
    if not dated or dated.group(1) != released:
        raise ValueError(
            f"CITATION.cff date-released {released} disagrees with CHANGELOG date for {expected}: "
            f"{dated.group(1) if dated else 'missing'}"
        )


def prepare_huggingface_bundle(source: Path, destination: Path) -> None:
    validate_package(source)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Hugging Face staging destination must be empty")
    destination.mkdir(parents=True, exist_ok=True)
    package = json.loads((source / "datapackage.json").read_text())
    selected = []
    for resource in package["resources"]:
        table = resource.get("table")
        if table not in ("countries", "intblocks", "blocktypes", "memberships") or resource["format"] != "parquet":
            continue
        target = Path(table) / Path(resource["path"]).name
        (destination / target).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / resource["path"], destination / target)
        selected.append({**resource, "path": target.as_posix()})
        for suffix in ("manifest.json", "meta.json"):
            path = source / f"{table}.{suffix}"
            shutil.copy2(path, destination / path.name)
    if len(selected) != 4:
        raise ValueError("Hugging Face bundle requires all four primary tables")
    package["resources"] = selected
    (destination / "datapackage.json").write_text(json.dumps(package, indent=2) + "\n")
    for name in ("README.md", CONTRACT_FILE):
        if (source / name).is_file():
            shutil.copy2(source / name, destination / name)
    validate_package(destination)
