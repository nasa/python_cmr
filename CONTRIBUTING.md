# Contributing

## Development setup

Install the project dependencies with Poetry:

```bash
poetry install
```

## Pre-commit checks

The repository includes pre-commit hooks that mirror the important local CI checks:

- critical `flake8` errors run before commits;
- `mypy` runs before commits;
- the full `pytest` suite runs before pushes.

Install pre-commit, then enable both hook stages:

```bash
python -m pip install pre-commit
pre-commit install --hook-type pre-commit --hook-type pre-push
```

Run all commit-stage hooks manually with:

```bash
pre-commit run --all-files
```

Run the pre-push test hook manually with:

```bash
pre-commit run --all-files --hook-stage pre-push
```

The hook commands use the project's Poetry environment, so run `poetry install` first.
