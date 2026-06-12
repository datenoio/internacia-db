## 1. Scheduled workflow

- [x] 1.1 Created `.github/workflows/link-validation.yml` with weekly cron and manual dispatch
- [x] 1.2 Run `python scripts/validate_links.py` with JSON or markdown report output
- [x] 1.3 Upload report artifact; notify on failure via workflow summary (no merge blocking)

## 2. Script improvements

- [x] 2.1 Report captured as text artifact via workflow tee (structured `--report` deferred)
- [x] 2.2 Ensure rate limiting (0.1s delay) documented and configurable

## 3. Documentation

- [x] 3.1 Document scheduled validation in README and CONTRIBUTING
- [x] 3.2 Run `openspec validate add-scheduled-link-validation --strict`
