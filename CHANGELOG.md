# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Full documentation protocol implementation under `docs/` with structured references for architecture, configuration, CLI/API/UI usage, operations, security, troubleshooting, testing, roadmap, and release governance.
- Documentation root index (`docs/00-index.md`) with navigable links across all technical and operational documents.
- Publish-ready documentation assets:
  - `docs/changelog.md`
  - `docs/compatibility-matrix.md`
  - `docs/release-checklist.md`
  - `docs/versioning-policy.md`
  - `docs/release-notes-template.md`
- First release note artifact at `docs/releases/0.1.0.md`.
- Root project changelog (`CHANGELOG.md`) aligned with Keep a Changelog and SemVer workflow.
- Root `VERSION` file (`0.1.0`) as release source of truth.
- Changelog automation script `scripts/check_changelog.py`.
- CI workflow for changelog policy enforcement at `.github/workflows/changelog-check.yml`.
- CI PR feedback automation that comments failures with actionable detail when changelog checks fail.
- End-to-end language support parameter (`language`) across API operations (`ask`, `explain`, `eval`, `tune`, `suggest`).
- New i18n module for query normalization/tokenization and Spanish query expansion to improve bilingual retrieval.
- Full Web UI internationalization layer (`en`/`es`) with runtime language switching and scalable translation dictionary.
- Localized suggestions and localized Ask hint text with `Tab`-accept behavior preserved across languages.
- Enhanced answer synthesis for practical product usage:
  - direct capability-style response for payment-related questions
  - provider detection heuristics (for known gateways)
  - evidence-derived flow summary to explain implementation path

### Changed

- README promoted to product-facing entrypoint with expanded Product Overview (goals, capabilities, use cases, non-goals).
- README documentation index expanded to include release governance and changelog navigation.
- Documentation strategy moved from ad hoc notes to a formalized publish-ready documentation system.
- Changelog policy hardened:
  - `Unreleased` must contain meaningful entries when relevant files change.
  - Required changelog sections are validated based on changed file categories.
- Changelog validator made repository-root aware to work reliably across CI/local execution contexts.
- Search pipeline updated to language-aware query processing in `IndexStore.search`.
- Ask response behavior upgraded from citation-only summary to richer response shape (direct answer + flow suggestion + evidence summary).
- Web UI runtime controls expanded with language selector and dynamic interface text translation.

### Fixed

- Corrected Product Overview quote formatting in README to plain ASCII-safe quoting.
- Resolved changelog validator path-resolution issue that could fail when script ran outside repo cwd.
- Improved changelog automation diagnostics to make CI failures explicit and actionable for contributors.
- Resolved UI text encoding inconsistencies by normalizing language labels/content to ASCII-safe forms.

### Security

- Strengthened governance controls by enforcing mandatory change documentation before merge via CI.
- Reduced release-process risk by requiring explicit `Unreleased` entries for relevant code/docs/config changes.
- Maintained explicit opt-in posture for external embedding providers through documented release and policy artifacts.
- Preserved local-first privacy defaults while adding multilingual support, without introducing outbound data flow by default.

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
