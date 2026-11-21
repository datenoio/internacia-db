## 1. Implementation
- [x] 1.1 `Rule.dated` in the rule registry; mark intblock `last verified`, both `provenance freshness` rules and `border status freshness`
- [x] 1.2 `validator_messages` returns dated warnings separately; both validators report them and `--fail-on-warning` ignores them
- [x] 1.3 Run both validators with `--fail-on-warning` in `.github/workflows/validate.yml`
- [x] 1.4 Tests: the set of dated rules; with a far-future date `--fail-on-warning` passes on the repository data, and a planted plain warning fails it
- [x] 1.5 Update `CONTRIBUTING.md` and `docs/agents/contribute.md`
