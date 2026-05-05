# Semantic Code Navigator

Local-first CLI + API + Web UI for indexing private Python repositories and asking technical questions with verifiable citations.

## Product Overview

Semantic Code Navigator is a local-first AI engineering toolchain for understanding private codebases without requiring SaaS deployment. The system indexes Python repositories into a local vector-ready store, supports question answering with file/line citations, explains ranking behavior for retrieval debugging, and provides quality instrumentation (evaluation, tuning, and metrics) to improve relevance over time.

Primary goals:
- Ship a practical code intelligence workflow for real repositories.
- Keep sensitive code local by default.
- Make retrieval quality measurable, not subjective.
- Support iterative optimization with repeatable evaluation loops.

Core capabilities:
- Repository indexing with AST-aware chunking and secret redaction.
- Hybrid retrieval (`vector + keyword overlap`) with score breakdown.
- CLI, API, and polished local Web UI.
- Embedding backend selection (`local`, `openai`) at runtime.
- Persistent embedding cache to reduce reindex cost and latency.
- Evaluation and tuning with report export and quality gates.
- Operational observability through event metrics and cache telemetry.

Primary use cases:
- “Where is X implemented?” technical navigation across large repos.
- Retrieval quality regression tracking in CI.
- Prompt/retrieval iteration before building agentic automation.
- Local operator console for indexing, asking, tuning, and maintenance.

Non-goals (current version):
- Multi-tenant SaaS and auth/billing.
- Automated code modification loops.
- Cross-language deep semantic parsing beyond Python-first scope.

## Documentation Index

- [Documentation Root](./docs/00-index.md)
- [Architecture](./docs/02-architecture.md)
- [Configuration](./docs/03-configuration.md)
- [CLI Reference](./docs/04-cli-reference.md)
- [API Reference](./docs/05-api-reference.md)
- [Web UI Guide](./docs/06-web-ui-guide.md)
- [Embedding Cache](./docs/07-embedding-cache.md)
- [Evaluation and Tuning](./docs/08-evaluation-and-tuning.md)
- [Security and Privacy](./docs/09-security-and-privacy.md)
- [Operations Runbook](./docs/10-operations-runbook.md)
- [Troubleshooting](./docs/11-troubleshooting.md)
- [Development and Testing](./docs/12-development-and-testing.md)
- [Roadmap](./docs/13-roadmap.md)
- [Product Changelog](./CHANGELOG.md)
- [Docs Changelog](./docs/changelog.md)
- [Compatibility Matrix](./docs/compatibility-matrix.md)
- [Versioning Policy](./docs/versioning-policy.md)
- [Release Notes Template](./docs/release-notes-template.md)
- [Release Checklist](./docs/release-checklist.md)
- [Agile Learning System](./docs/agile-learning-system.md)

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
scn index C:\path\to\python\repo
scn ask "Where is user authentication handled?"
scn explain "how ranking was computed for auth?"
scn status
scn eval eval/eval_dataset.real.json
scn eval eval/eval_dataset.real.json --report-out reports/eval.json --min-recall 0.20
scn tune eval/eval_dataset.real.json --weights 0.20,0.35,0.55,0.70 --report-out reports/tune.json
```

Run the local API:

```powershell
uvicorn semantic_code_navigator.api:app --reload
```
Open `http://127.0.0.1:8000` for the local web UI.

## What Stays In README

- Primary local-first defaults:
  - local embedding backend by default
  - secret redaction before indexing
  - `.scnignore` support
  - local index and embedding cache persistence
- Quality loop:
  - `index -> ask/explain -> eval -> tune -> gate`
- Runtime override support:
  - backend and hybrid weight can be controlled from UI or API request body.

## Core Commands

- `scn index <repo>`: build or rebuild the local index.
- `scn ask <question>`: retrieve relevant chunks and produce an evidence-first answer.
- `scn explain <question>`: inspect ranking scores (hybrid, vector, keyword).
- `scn status`: show index health and repository stats.
- `scn reset-index`: delete the local index.
- `scn doctor`: check runtime and SQLite health.
- `scn eval <dataset.json>`: run recall and latency metrics against an eval set.
- `scn eval ... --report-out reports/eval.json --min-recall 0.20`: export report and fail under quality gate.
- `scn tune ... --weights ... --report-out reports/tune.json`: pick the best hybrid keyword weight.
- `scn cache-stats`: inspect embedding cache usage.
- `scn cache-prune --max-entries N`: limit cache size.

## Optional Provider Setup

- Install provider deps: `pip install -e ".[providers]"`
- Set `OPENAI_API_KEY`
- Select backend from UI runtime panel or environment variable.
