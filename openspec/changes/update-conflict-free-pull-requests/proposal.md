# Change: Conflict-free pull requests

## Why

Agent sessions spend most of their time waiting for CI, and most of those CI runs only repeat a green result. In the three days before 2026-11-21, 38 pull requests merged and their branches took 57 merges of `main`. A pull request with one commit merged in 7 to 9 minutes. Pull requests opened in a parallel wave lived 2 to 3 hours: #145 took 10 merges of `main` and 10 validate runs, #141 took 8 merges. Every one of those runs passed. Each run takes 7 to 10 minutes.

The reruns come from merge conflicts, not from failures. Every data pull request edits the same few files, so it conflicts with every other open data pull request:

- `data/datasets/*.manifest.json` and `data/datasets/datapackage.json` (changed by 38 of 38 pull requests). They hold the SHA-256 and size of every export, the row count, and the build date and commit. Any data change rewrites the same lines.
- `CHANGELOG.md`. Every pull request inserts its bullet at the top of `### Added` under `[Unreleased]`, often with a running total such as "(1304 intblocks)".
- The exact intblock count, which `scripts/check_doc_counts.py` requires in 10 documentation files, and which the build writes into the committed dataset card `data/datasets/README.md`.

When one pull request merges, all other open ones conflict. Each session then merges `main`, rebuilds, pushes and waits for CI again, so the number of CI runs grows with the square of the number of parallel sessions.

## What Changes

- **Build descriptors are build outputs.** `*.manifest.json` and `datapackage.json` are no longer committed. The build still writes them to `data/datasets/`, and every GitHub Release still ships them. The small descriptors that change only with the schema or with rare source edits stay committed and gated: `contract.json`, `README.md`, the alias files, `attribute_intblock_migrations.json` and `border_status.json`.
- **The baseline diff no longer needs committed manifests.** `scripts/diff_countries_baseline.py` reads the current manifests from the build directory, counts the baseline records from the source YAML at the baseline ref, and reads the baseline schema hashes from the committed `contract.json`.
- **Documentation and the dataset card state the intblock count rounded down to the hundred** (for example `1300+`, `internacia_builder/doc_counts.py`). `scripts/check_doc_counts.py` reads the built manifests and requires that rounded figure. Country and blocktype counts stay exact; they change rarely.
- **Changelog fragments.** A pull request adds its entry as `changelog.d/<slug>.md` with Keep a Changelog subsections instead of editing `CHANGELOG.md`. The release train merges the fragments into the dated release section and deletes them. Entries do not carry running record totals; the release section already gets a generated data-change summary.

## Impact

- Affected specs: `dataset-release` (committed dataset freshness gate, changelog fragments), `contributor-docs` (README accuracy, documentation count accuracy).
- Affected code: `.gitignore`, `internacia_builder/snapshot.py`, `internacia_builder/release.py`, new `internacia_builder/changelog.py` and `internacia_builder/doc_counts.py`, `internacia_builder/export.py` (dataset card), `scripts/check_doc_counts.py`, `scripts/diff_countries_baseline.py`, `.github/workflows/release-train.yml`.
- Affected docs: the 10 files with dataset counts, `CONTRIBUTING.md`, `docs/agents/contribute.md` (and `zh/`), `docs/agents/add-intblock-example.md`, `.agent/workflows/edit-intblock.md`, `data/datasets/README.md`, `docs/getting-started.md`, new `changelog.d/README.md`.
- Consumers: no export changes. Release assets keep every descriptor. Anyone who read the manifests or `datapackage.json` from a git checkout without building gets them from the latest GitHub Release, or from `python scripts/builder.py build`.
- Approval: the maintainer chose this design in the session of 2026-11-21 (descriptors out of git, rounded intblock count, changelog fragments).
