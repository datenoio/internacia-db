"""Safety and ordering properties of the actual CI/release configuration."""
import ast
import json
import os
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


LIGHT_PATHS = r"^(openspec|dev|website)/"
FULL = "steps.scope.outputs.full == 'true'"


def runs_on(step, version, full=True):
    """Whether a validate step runs on a matrix leg; ``full`` is False for a pull request that
    changes only openspec/, dev/ or website/. Only python-version and scope conditions are expected."""
    terms = [t for t in (step.get("if") or "").split(" && ") if t and t != "always()"]
    if FULL in terms:
        terms.remove(FULL)
        if not full:
            return False
    assert len(terms) <= 1, f"unexpected condition: {step['if']}"
    if not terms:
        return True
    match = re.fullmatch(r"matrix\.python-version (==|!=) '([\d.]+)'", terms[0])
    assert match, f"unexpected condition: {step['if']}"
    return (match.group(2) == version) == (match.group(1) == "==")


def matrix_legs():
    """The validate legs of a pull request and of a push to main."""
    expression = workflow("validate.yml")["jobs"]["validate"]["strategy"]["matrix"]["python-version"]
    match = re.fullmatch(
        r"\$\{\{ fromJSON\(github\.event_name == 'push' && '(\[[^']*\])' \|\| '(\[[^']*\])'\) \}\}", expression
    )
    assert match, expression
    push, pull_request = (json.loads(group) for group in match.groups())
    return pull_request, push


def test_every_python_runs_the_suite_and_the_costly_checks_run_once():
    validate = workflow("validate.yml")["jobs"]["validate"]
    versions, _ = matrix_legs()
    assert versions == ["3.11", "3.12", "3.13"]

    def legs(pattern):
        return [v for v in versions for s in validate["steps"] if re.search(pattern, s.get("run", "")) and runs_on(s, v)]

    suite = r"\bpytest tests/(\s|$)"
    assert sorted(legs(suite)) == sorted(versions), "every Python version runs pytest tests/ exactly once"
    assert all("-n auto" in s["run"] for s in validate["steps"] if re.search(suite, s.get("run", "")))
    assert legs(r"--cov=internacia_builder") == ["3.12"]
    assert len(legs(r"check_reproducible_build\.py")) == 1
    assert len(legs(r"scripts/builder\.py build")) == len(versions) + 1, "one build per leg, plus the reproducibility build"

    # Checks that do not depend on the Python version run on one leg, never the coverage leg
    # (the slowest) or the reproducibility leg (which builds twice).
    data_checks = [
        r"pip-audit --requirement",
        r"check_min_duckdb\.py",
        r"check_generated_artifacts\.py",
        r"check_release_bundle\.py",
        r"validate_countries\.py",
        r"validate_intblocks\.py",
        r"check_doc_counts\.py",
        r"check_markdown_links\.py",
        r"generate_data_dictionary\.py --check",
        r"generate_agent_shims\.py --check",
        r"analyze-quality",
        r"check_quality_report\.py",
    ]
    busy = {*legs(r"--cov=internacia_builder"), *legs(r"check_reproducible_build\.py")}
    for check in data_checks:
        ran = legs(check)
        assert len(ran) == 1 and ran[0] not in busy, f"{check} runs on {ran}"


def test_a_push_to_main_runs_one_leg_with_the_data_checks_and_reports():
    validate = workflow("validate.yml")["jobs"]["validate"]
    _, push = matrix_legs()
    assert push == ["3.13"]
    (leg,) = push
    checks = (r"\bpytest tests/(\s|$)", r"scripts/builder\.py build", r"validate_intblocks\.py", r"check_quality_report\.py")
    for pattern in checks:
        assert any(re.search(pattern, s.get("run", "")) and runs_on(s, leg) for s in validate["steps"]), pattern
    uploads = [s for s in validate["steps"] if s.get("uses", "").startswith("actions/upload-artifact@")]
    assert uploads and all(runs_on(s, leg) for s in uploads)


def test_pull_requests_that_change_only_openspec_dev_or_website_skip_the_heavy_steps():
    validate = workflow("validate.yml")["jobs"]["validate"]
    steps = validate["steps"]
    scope = next(i for i, s in enumerate(steps) if s.get("id") == "scope")
    assert all(FULL not in (s.get("if") or "") for s in steps[:scope])
    assert LIGHT_PATHS in steps[scope]["run"]
    ungated = {s.get("name") or s["uses"].split("@")[0] for s in steps if runs_on(s, "3.13", full=False)}
    assert ungated == {
        "actions/checkout",
        "Detect a pull request that changes only openspec/, dev/ or website/",
        "actions/setup-python",
        "astral-sh/setup-uv",
        "Install dependencies",
        "Check internal Markdown links",
    }
    # Those directories must still trigger the workflow: its legs are required checks.
    paths = workflow("validate.yml")["on"]["pull_request"]["paths"]
    assert {"openspec/**", "dev/**", "website/**"} <= set(paths)


@pytest.mark.parametrize(
    ("event", "changed", "full"),
    [
        ("pull_request", ["openspec/changes/x/proposal.md", "website/docs/a.md", "dev/notes.md"], "false"),
        ("pull_request", ["openspec/changes/x/proposal.md", "data/intblocks/misc/EU.yaml"], "true"),
        ("pull_request", ["website/docs/a.md", ".github/workflows/validate.yml"], "true"),
        ("pull_request", ["openspec-notes.md"], "true"),
        ("push", ["openspec/changes/x/proposal.md"], "true"),
    ],
)
def test_scope_step_runs_everything_unless_only_light_paths_change(tmp_path, event, changed, full):
    repo = tmp_path / "repo"
    repo.mkdir()
    step = next(s for s in workflow("validate.yml")["jobs"]["validate"]["steps"] if s.get("id") == "scope")

    def git(*args):
        identity = ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
        return subprocess.run(["git", *identity, *args], cwd=repo, check=True, capture_output=True, text=True).stdout

    git("init", "-q")
    (repo / "README.md").write_text("base\n")
    git("add", ".")
    git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD").strip()
    for name in changed:
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        (repo / name).write_text("change\n")
    git("add", ".")
    git("commit", "-qm", "change")
    output = tmp_path / "output"
    env = {
        **os.environ,
        "GITHUB_EVENT_NAME": event,
        "BASE_SHA": base if event == "pull_request" else "",
        "GITHUB_OUTPUT": str(output),
        "GITHUB_STEP_SUMMARY": str(tmp_path / "summary"),
    }
    subprocess.run(["bash", "-e", "-c", step["run"]], cwd=repo, env=env, check=True)
    assert output.read_text() == f"full={full}\n"


def test_validate_installs_with_uv_not_pip():
    config = workflow("validate.yml")["jobs"]["validate"]
    runs = "\n".join(commands(config))
    assert "uv pip install --system -r requirements-dev.txt" in runs
    assert not re.search(r"(?<!uv )\bpip install", runs)
    setup_python = next(s for s in config["steps"] if s.get("uses", "").startswith("actions/setup-python@"))
    assert "cache" not in setup_python["with"]


def test_only_pull_request_builds_lower_the_zstd_level():
    assert workflow("validate.yml")["jobs"]["validate"]["env"]["INTERNACIA_ZSTD_LEVEL"] == "3"
    for path in (project_root() / ".github/workflows").glob("*.yml"):
        if path.name != "validate.yml":
            assert "INTERNACIA_ZSTD_LEVEL" not in path.read_text(encoding="utf-8"), path.name


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
