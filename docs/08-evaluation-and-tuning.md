# Evaluation and Tuning

Datasets:
- Sample: `eval/eval_dataset.sample.json`
- Real: `eval/eval_dataset.real.json`

Evaluation:
- Computes `recall@k` and mean latency.
- Can fail with threshold gate via `--min-recall`.

Tuning:
- Tests multiple hybrid weights and returns best candidate.
- Command: `scn tune ... --weights 0.20,0.35,0.55,0.70`

Reports:
- Save with `--report-out reports/<name>.json`.
- Use in CI and regression tracking.

