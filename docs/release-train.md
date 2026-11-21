# Release train

Releases follow the data: once a month a workflow checks what changed since the last release
and, if anything did, opens a release pull request. A maintainer reviews and merges it; the rest
is automatic.

```
release-train.yml (8th of the month, or Run workflow)
  └─ scripts/prepare_release.py: level and summary
       ├─ nothing changed  → stop
       ├─ MAJOR change     → stop; the summary lists why (release by hand)
       └─ PATCH or MINOR   → PR "Release vX.Y.Z" on release/next
merge the PR
  └─ release-tag.yml: tag vX.Y.Z on the merge commit
       └─ release.yml: gates, SDK contract suite, Release assets, Hugging Face, Zenodo
            └─ repository_dispatch internacia-db-release → internacia-python, internacia-api
```

## How the level is chosen

[versioning-policy.md](versioning-policy.md) defines the levels; `internacia_builder/release.py`
applies them to the differences between the latest `vX.Y.Z` tag and `main`:

| Level | When |
|---|---|
| none | nothing under `data/` or `internacia_builder/` changed |
| PATCH | values changed (rosters, descriptions, provenance, fill rates) |
| MINOR | records, tables, columns, source fields or enum values were added |
| MAJOR (stops) | a record id, table, column, source field or enum value was removed, or a column type changed |

The train never releases MAJOR changes: they are batched by hand, at most once or twice a year.
Removing a record usually means it was merged or renamed; add it to the alias map and decide on
the release with the maintainers.

## The release pull request

The PR, opened by `internacia-bot`, contains:

- the CHANGELOG `[Unreleased]` entries and the `changelog.d/` fragments merged under
  `## [X.Y.Z] - <date>` (grouped by subsection; the fragments are deleted), followed by "Data changes
  since the previous release" (record counts, ids added and removed, membership edges added,
  removed and changed, new aliases, schema additions);
- the version in `pyproject.toml`, `internacia_builder/__init__.py`, `CITATION.cff`
  (with `date-released`) and `uv.lock`;
- the rebuilt tracked descriptors in `data/datasets/` (such as `contract.json`).

Validation runs on it like on any PR. Edit the CHANGELOG wording on the branch if needed. If the
train runs again before the PR is merged, it rebuilds the branch from the current `main`.

To check a release by hand at any time:

```bash
python scripts/prepare_release.py                 # plan only
python scripts/prepare_release.py --level minor   # at least MINOR
python scripts/prepare_release.py --apply         # write the bump locally
```

Exit codes: 0 release planned, 3 nothing to release, 4 MAJOR changes.

## After the merge

`release-tag.yml` reads the version from the CHANGELOG, checks it against `pyproject.toml`, and
pushes `vX.Y.Z`. `release.yml` publishes the release and adds a `data` section to
`migration.vX.Y.Z.json` with the same record-level diff. It then notifies internacia-python and
internacia-api, which also poll for new releases daily.

## Requirements

The workflows use the internacia-bot GitHub App (secrets `INTERNACIA_BOT_CLIENT_ID` and
`INTERNACIA_BOT_PRIVATE_KEY`), because pull requests and tags created with the default
`GITHUB_TOKEN` do not start other workflows.

| Workflow | App installed on | Permissions |
|---|---|---|
| `release-train.yml` | internacia-db | Contents, Pull requests: write |
| `release-tag.yml` | internacia-db | Contents: write |
| `release.yml` (notification) | internacia-python, internacia-api | Contents: write |

Without the secrets, `release-train.yml` still writes the plan to the job summary and the
`release-plan` artifact, `release-tag.yml` fails with instructions to tag by hand, and
`release.yml` skips the notification.
