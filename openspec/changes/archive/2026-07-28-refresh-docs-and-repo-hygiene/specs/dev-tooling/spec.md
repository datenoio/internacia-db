## ADDED Requirements

### Requirement: Repository ignores editor and OS artifacts

`.gitignore` SHALL ignore `.DS_Store` and similar OS/editor artifacts, and no such artifacts SHALL remain tracked in the repository.

#### Scenario: DS_Store ignored

- **WHEN** a contributor on macOS creates a `.DS_Store` file in the working tree
- **THEN** `git status` does not list it as an untracked or staged file

#### Scenario: No tracked DS_Store

- **WHEN** the repository file list is inspected
- **THEN** no `.DS_Store` file is tracked
