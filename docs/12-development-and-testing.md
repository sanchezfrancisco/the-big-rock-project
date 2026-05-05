# Development and Testing

Install:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Optional providers:
```powershell
pip install -e ".[providers]"
```

Tests:
- Unit/integration tests in `tests/test_core.py`.
- Run `pytest` when available in environment.

Recommended checks:
- `ruff`
- `mypy`
- `pytest`

