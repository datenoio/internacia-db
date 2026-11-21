"""Safety and ordering properties of the actual CI/release configuration."""
import ast
import re
import subprocess
import sys

import pytest
import yaml

from internacia_builder.paths import project_root


def workflow(name):
    return yaml.load((project_root() / ".github/workflows" / name).read_text(), Loader=yaml.BaseLoader)


SHA = re.compile(r"^[0-9a-f]{40}$")


def commands(job):
    return [step.get("run", "") for step in job["steps"]]


def index(job, text):
    return next(i for i, command in enumerate(commands(job)) if text in command)


@pytest.mark.parametrize(("name", "job"), [("validate.yml", "validate"), ("release.yml", "build")])
def test_committed_snapshot_is_checked_against_the_build_and_final_artifacts_are_tested(name, job):
    config = workflow(name)["jobs"][job]
    build = index(config, "scripts/builder.py build")
    assert build < index(config, "scripts/check_committed_snapshot.py --fresh") and build < index(config, "pytest tests/")
    assert any("check_generated_artifacts.py --datasets-dir" in command for command in commands(config))
    assert "INTERNACIA_DATASETS_DIR" in config["env"]
    assert any("check_quality_report.py" in command for command in commands(config))
    assert any("check_release_bundle.py" in command for command in commands(config))


def test_sdk_contract_suite_runs_on_the_build_at_one_pinned_commit():
    validate = workflow("validate.yml")["jobs"]["validate"]
    release = workflow("release.yml")["jobs"]
    assert index(validate, "scripts/builder.py build") < index(validate, "pytest tests/contract")
    assert release["sdk-contract"]["needs"] == "build"
    assert any("pytest tests/contract" in command for command in commands(release["sdk-contract"]))
    ref = release["sdk-contract"]["env"]["INTERNACIA_SDK_REF"]
    assert SHA.match(ref) and validate["env"]["INTERNACIA_SDK_REF"] == ref


def runs_on(step, version):
    """Whether a validate step runs on a matrix leg; only python-version conditions are expected."""
    condition = step.get("if")
    if condition is None:
        return True
    match = re.fullmatch(r"matrix\.python-version (==|!=) '([\d.]+)'", condition)
    assert match, f"unexpected condition: {condition}"
    return (match.group(2) == version) == (match.group(1) == "==")


def test_every_python_runs_the_suite_and_the_costly_checks_run_once():
    validate = workflow("validate.yml")["jobs"]["validate"]
    versions = validate["strategy"]["matrix"]["python-version"]

    def legs(pattern):
        return [v for v in versions for s in validate["steps"] if re.search(pattern, s.get("run", "")) and runs_on(s, v)]

    suite = r"\bpytest tests/(\s|$)"
    assert sorted(legs(suite)) == sorted(versions), "every Python version runs pytest tests/ exactly once"
    assert all("-n auto" in s["run"] for s in validate["steps"] if re.search(suite, s.get("run", "")))
    assert legs(r"--cov=internacia_builder") == ["3.12"]
    assert legs(r"check_reproducible_build\.py") == ["3.12"]


def test_every_action_is_pinned_to_a_commit_with_its_version():
    for path in (project_root() / ".github/workflows").glob("*.yml"):
        for line in path.read_text().splitlines():
            if line.strip().startswith(("uses:", "- uses:")):
                ref = line.split("uses:", 1)[1].strip()
                assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40} # v\d+\.\d+\.\d+", ref), f"{path.name}: {ref}"


def test_release_secrets_and_write_access_stay_in_the_publish_job():
    config = workflow("release.yml")
    assert config["permissions"] == {"contents": "read"}
    jobs = config["jobs"]
    assert {name for name, job in jobs.items() if job.get("permissions")} == {"publish"}
    assert jobs["publish"]["permissions"] == {"contents": "write"}
    assert set(jobs["publish"]["needs"]) == {"build", "sdk-contract"}
    for name in ("build", "sdk-contract"):
        assert "secrets." not in yaml.safe_dump(jobs[name]), name
    for name, job in jobs.items():
        for step in job["steps"]:
            if step.get("uses", "").startswith("actions/checkout@"):
                assert step["with"]["persist-credentials"] == "false", name


def test_publish_verifies_the_build_digest_then_releases_github_before_hugging_face():
    jobs = workflow("release.yml")["jobs"]
    assert jobs["build"]["outputs"]["digest"] == "${{ steps.digest.outputs.digest }}"
    steps = jobs["publish"]["steps"]
    names = [step.get("name", step.get("uses", "")) for step in steps]
    verify = names.index("Verify artifacts against the build digest")
    release = names.index("Create GitHub release with dataset assets")
    hf = names.index("Push to Hugging Face (optional)")
    assert verify < release < hf
    assert "needs.build.outputs.digest" in steps[verify]["env"]["DIGEST"]
    assert "scripts/push_huggingface.py" in steps[hf]["run"] and "requirements-publish.txt" in steps[hf]["run"]
    assert "pip install -r requirements-dev.txt" not in yaml.safe_dump(jobs["publish"])


def test_validate_workflow_token_is_read_only():
    assert workflow("validate.yml")["permissions"] == {"contents": "read"}
    assert workflow("link-validation.yml")["permissions"] == {"contents": "read"}


def test_docs_pr_build_has_no_publication_permissions_or_deployment():
    config = workflow("deploy-docs.yml")
    assert "pull_request" in config["on"]
    assert config["permissions"] == {"contents": "read"}
    assert config["jobs"]["deploy"]["if"] == "github.event_name != 'pull_request'"
    for step in config["jobs"]["build"]["steps"]:
        if step.get("uses", "").startswith("actions/upload-pages-artifact"):
            assert step["if"] == "github.event_name != 'pull_request'"


def test_workflow_shell_and_embedded_python_parse():
    for path in (project_root() / ".github/workflows").glob("*.yml"):
        for job in workflow(path.name)["jobs"].values():
            for step in job.get("steps", []):
                if "run" not in step:
                    continue
                result = subprocess.run(["bash", "-n"], input=step["run"], text=True, capture_output=True)
                assert result.returncode == 0, f"{path.name}: {result.stderr}"
                for python in re.findall(r"python - <<'PY'\n(.*?)\nPY", step["run"], re.S):
                    ast.parse(python)


def test_generated_agent_files_are_current():
    result = subprocess.run(
        [sys.executable, "scripts/generate_agent_shims.py", "--check"],
        cwd=project_root(),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout
