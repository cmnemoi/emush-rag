# Coding Assertions

## Before commit

The `pre-commit` hook runs these when staged files include Python.

| Order | Command            | Checks                      |
| ----- | ------------------ | --------------------------- |
| 1     | `make lint`        | Ruff format and autofix     |
| 2     | `make check-types` | Mypy                        |

## Before push

The `pre-push` hook runs these.

| Order | Command      | Checks                                            |
| ----- | ------------ | ------------------------------------------------- |
| 1     | `make check` | Ruff format diff, Ruff lint, Mypy                 |
| 2     | `make test`  | all pytest layers with coverage (Docker needed)   |

## Behavior

If a fix is needed, spawn 1 agent per assertion to fix (e.g typechecking / tests / rules violated on category UI = 3 agents).
