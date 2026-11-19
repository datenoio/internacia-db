#!/usr/bin/env python3
"""Push a prepared Hugging Face bundle to the dataset repository in one commit.

The bundle comes from ``internacia_builder.distribution.prepare_huggingface_bundle``. Every file
is added, and the legacy flat ``<table>.parquet`` files are deleted, in a single commit, so the
Hugging Face ``main`` revision never mixes two releases. With ``--tag`` the commit is also tagged
(for example ``v3.2.0``) so consumers can pin ``revision=``.

Only the standard library and ``huggingface_hub`` are imported: the release workflow runs this in
the job that holds ``HF_TOKEN`` without installing the project.

Usage:
    HF_TOKEN=... python scripts/push_huggingface.py .hf-release --message "Release v3.2.0" --tag v3.2.0
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

DEFAULT_REPO = "datenoio/internacia"
TABLES = ("countries", "intblocks", "blocktypes", "memberships")
# Files from the pre-folder layout, removed when still present.
LEGACY_FILES = tuple(f"{table}.parquet" for table in TABLES)


def bundle_files(root: Path) -> list[tuple[str, Path]]:
    """``(path in repo, local path)`` for every file of the bundle, sorted."""
    files = sorted((p.relative_to(root).as_posix(), p) for p in root.rglob("*") if p.is_file())
    if not files:
        raise ValueError(f"Hugging Face bundle {root} is empty")
    return files


def push(api, hub, root: Path, repo_id: str, message: str, tag: str | None = None):
    """Create the repo if needed and push ``root`` as one commit; return the commit info."""
    api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True)
    existing = set(api.list_repo_files(repo_id=repo_id, repo_type="dataset"))
    operations = [hub.CommitOperationAdd(path_in_repo=name, path_or_fileobj=str(path)) for name, path in bundle_files(root)]
    operations += [hub.CommitOperationDelete(path_in_repo=name) for name in LEGACY_FILES if name in existing]
    info = api.create_commit(repo_id=repo_id, repo_type="dataset", operations=operations, commit_message=message)
    if tag:
        api.create_tag(repo_id=repo_id, repo_type="dataset", tag=tag, revision=info.oid, exist_ok=True)
    return info


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("bundle", type=Path, help="Directory produced by prepare_huggingface_bundle")
    parser.add_argument("--repo", default=os.environ.get("HF_DATASET_REPO") or DEFAULT_REPO)
    parser.add_argument("--message", required=True, help="Commit message, e.g. 'Release v3.2.0'")
    parser.add_argument("--tag", help="Tag the commit with this name (e.g. the release tag)")
    args = parser.parse_args(argv)

    token = os.environ.get("HF_TOKEN")
    if not token:
        print("HF_TOKEN not set; skipping Hugging Face upload")
        return 0
    import huggingface_hub as hub  # noqa: PLC0415 (optional dependency)

    info = push(hub.HfApi(token=token), hub, args.bundle, args.repo, args.message, args.tag)
    print(f"HF push complete: {args.repo} @ {info.oid}" + (f" (tag {args.tag})" if args.tag else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
