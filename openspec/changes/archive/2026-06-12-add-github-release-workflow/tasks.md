## 1. Release workflow

- [x] 1.1 Create `.github/workflows/release.yml` on push tags matching `v*`
- [x] 1.2 Run validation, full build (`builder.py build`), and upload dataset artifacts
- [x] 1.3 Generate GitHub Release notes from tag and manifest versions

## 2. Documentation

- [x] 2.1 Document release process in README (clone vs download)
- [x] 2.2 Add CHANGELOG release section template with manifest version alignment
- [x] 2.3 Decide transition plan for git-tracked binaries (document, do not remove in this change unless approved)

## 3. Validation

- [x] 3.1 Run `openspec validate add-github-release-workflow --strict`
