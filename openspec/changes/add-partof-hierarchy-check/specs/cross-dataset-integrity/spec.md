## ADDED Requirements

### Requirement: Partof referential integrity

Cross-dataset validation SHALL verify that every `partof.id` resolves to an existing intblock record and that the parent-child direction matches organizational hierarchy semantics enforced by the partof hierarchy rule.

#### Scenario: Broken partof reference fails

- **WHEN** an intblock references `partof.id: NONEXISTENT`
- **THEN** cross-dataset validation reports an unresolved reference error
