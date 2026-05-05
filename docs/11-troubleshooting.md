# Troubleshooting

`No indexed context was found`:
- Run `scn index <repo>` with correct `--index-path`.

`OPENAI_API_KEY is required`:
- Set API key and ensure backend is `openai`.

`openai package is not installed`:
- `pip install -e ".[providers]"`

Low recall:
- Run `scn tune` and adjust hybrid weight.
- Expand/clean eval dataset.
- Improve chunking or backend model.

UI suggests nothing:
- Ensure index exists and question is non-empty.
- Confirm matching `index_path` in runtime panel.

