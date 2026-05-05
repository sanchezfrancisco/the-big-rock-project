# Versioning Policy (SemVer)

This project follows Semantic Versioning: `MAJOR.MINOR.PATCH`.

## Rules

- `MAJOR`: incompatible API/behavior changes.
- `MINOR`: backward-compatible feature additions.
- `PATCH`: backward-compatible fixes and non-breaking improvements.

## Scope of Compatibility

Compatibility applies to:
- CLI command semantics and options.
- HTTP API contract (paths, required fields, response structure).
- Core configuration keys (`SCN_*`).

Non-contractual internal details:
- Internal ranking heuristics and implementation internals can evolve in minor versions if external contracts remain stable.

## Release Bump Guide

- Bump `PATCH` when:
  - bug fixes
  - docs/test updates without interface changes
  - performance improvements with stable outputs/contracts
- Bump `MINOR` when:
  - new CLI/API/UI features are added compatibly
  - new optional configuration is introduced
- Bump `MAJOR` when:
  - existing CLI/API contracts break
  - required configuration or behavior changes incompatibly

## Version Source of Truth

- `VERSION` file at repo root is the release source of truth.
- `pyproject.toml` version should match `VERSION` for tagged releases.

