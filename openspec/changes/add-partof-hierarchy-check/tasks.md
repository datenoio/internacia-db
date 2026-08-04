## 1. Validation rule
- [x] 1.1 Implement check: `partof.id` target must not be `legal_status: treaty` or primary blocktype `agreement`
- [x] 1.2 Add IMPORTANT or CRITICAL priority in quality analyzer
- [x] 1.3 Add unit tests with EU→EEA fixture (should fail until EU fixed)

## 2. UN agency convention
- [x] 2.1 Document preferred `partof: UN` for specialized agencies in inclusion policy
- [x] 2.2 (Optional) Normalize ILO and peers in a follow-up data PR

## 3. CI
- [x] 3.1 Run rule in validate workflow; fail on CRITICAL findings
