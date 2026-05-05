# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- 

### Changed

- 

### Fixed

- 

### Security

- 

## [0.1.0] - 2026-05-05

### Added

- Local-first semantic code navigation across CLI, API, and Web UI.
- AST-aware Python chunking with contextual imports/docstrings.
- Secret redaction pipeline and `.scnignore` support.
- Hybrid retrieval with vector and keyword components.
- Explainability workflow (`explain`) with score breakdown.
- Evaluation workflow (`eval`) with recall/latency reporting and quality gates.
- Tuning workflow (`tune`) for hybrid keyword weight selection.
- Optional `openai` embedding backend support.
- Persistent embedding cache and cache operations (`cache-stats`, `cache-prune`).
- Runtime backend/weight overrides through API and Web UI.
- Web UI Ask suggestion endpoint with dynamic updates and `Tab` accept.
- Observability metrics stream and metrics panel in Web UI.
- Release governance artifacts:
  - `VERSION`
  - versioning policy
  - release checklist
  - release notes template
  - release notes `docs/releases/0.1.0.md`

### Changed

- `status` output expanded with embedding cache telemetry.
- README restructured with expanded Product Overview and full docs index.
- Documentation expanded under `docs/` with architecture, operations, security, API, CLI, UI, QA, and troubleshooting guides.

### Security

- Local-first backend remains default.
- Secret masking remains enabled before indexing.
- External provider flow remains explicit opt-in via environment key.

### Known Limitations

- Local hash embeddings can produce low semantic recall on broad or ambiguous queries.
- Suggestion quality depends on current index quality and query specificity.

## PR Label Convention

Use these labels to map changes into the changelog:
- `type:feature` -> `Added`
- `type:change` -> `Changed`
- `type:fix` -> `Fixed`
- `type:security` -> `Security`

Suggested release workflow:
1. Keep current work under `Unreleased`.
2. At release time, move items from `Unreleased` into a new version block.
3. Reset `Unreleased` to empty bullets.
