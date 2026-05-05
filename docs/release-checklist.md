# Release Checklist

## Pre-Release Quality

- [ ] `scn doctor` passes for target backend.
- [ ] `scn index <repo>` succeeds on representative repository.
- [ ] `scn eval eval/eval_dataset.real.json --report-out reports/eval.json --min-recall <target>` passes.
- [ ] `scn tune eval/eval_dataset.real.json --report-out reports/tune.json` reviewed.
- [ ] Cache behavior validated (`cache-stats`, `cache-prune`).

## Interface Validation

- [ ] CLI commands return expected JSON/text outputs.
- [ ] API endpoints respond correctly (`/index`, `/ask`, `/explain`, `/eval`, `/tune`, `/cache/*`, `/metrics/recent`, `/suggest`).
- [ ] Web UI flows verified end-to-end:
  - [ ] runtime backend switch
  - [ ] ask/explain with dynamic suggestions and `Tab` accept
  - [ ] eval/tune runs
  - [ ] cache operations
  - [ ] metrics refresh

## Security and Privacy

- [ ] `.scnignore` rules validated for sensitive paths.
- [ ] Secret redaction still active in indexing path.
- [ ] For `openai`, API key is managed via environment (not committed).

## Documentation and Artifacts

- [ ] README links and commands validated.
- [ ] `docs/` index and references are current.
- [ ] Eval and tune reports archived (`reports/`).
- [ ] Documentation changelog updated.

## Release Decision

- [ ] Compatibility matrix reviewed for target runtime.
- [ ] Known issues documented.
- [ ] Version/tag strategy confirmed.

