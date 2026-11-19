"""scripts/push_huggingface.py pushes a bundle in one commit (offline, fake API)."""

from types import SimpleNamespace

import push_huggingface as ph
import pytest


class FakeHub:
    @staticmethod
    def CommitOperationAdd(path_in_repo, path_or_fileobj):  # noqa: N802 (mirrors huggingface_hub)
        return ("add", path_in_repo, path_or_fileobj)

    @staticmethod
    def CommitOperationDelete(path_in_repo):  # noqa: N802
        return ("delete", path_in_repo)


class FakeApi:
    def __init__(self, existing):
        self.existing, self.calls = existing, []

    def create_repo(self, **kwargs):
        self.calls.append(("create_repo", kwargs))

    def list_repo_files(self, **kwargs):
        return list(self.existing)

    def create_commit(self, **kwargs):
        self.calls.append(("create_commit", kwargs))
        return SimpleNamespace(oid="abc123")

    def create_tag(self, **kwargs):
        self.calls.append(("create_tag", kwargs))


def bundle(tmp_path):
    (tmp_path / "countries").mkdir()
    (tmp_path / "countries" / "countries.parquet").write_bytes(b"x")
    (tmp_path / "datapackage.json").write_text("{}")
    return tmp_path


def test_one_commit_adds_every_file_and_deletes_only_present_legacy_files(tmp_path):
    api = FakeApi(existing=["countries.parquet", "README.md"])
    ph.push(api, FakeHub, bundle(tmp_path), "org/repo", "Release v9.9.9", tag="v9.9.9")
    commits = [kw for name, kw in api.calls if name == "create_commit"]
    assert len(commits) == 1
    ops = commits[0]["operations"]
    assert [op[:2] for op in ops] == [
        ("add", "countries/countries.parquet"),
        ("add", "datapackage.json"),
        ("delete", "countries.parquet"),
    ]
    assert commits[0]["commit_message"] == "Release v9.9.9" and commits[0]["repo_type"] == "dataset"
    assert ("create_tag", {"repo_id": "org/repo", "repo_type": "dataset", "tag": "v9.9.9", "revision": "abc123", "exist_ok": True}) in api.calls


def test_empty_bundle_is_refused(tmp_path):
    with pytest.raises(ValueError, match="empty"):
        ph.push(FakeApi([]), FakeHub, tmp_path, "org/repo", "m")


def test_missing_token_skips_without_importing_the_hub(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    assert ph.main([str(tmp_path), "--message", "m"]) == 0
    assert "HF_TOKEN not set" in capsys.readouterr().out
