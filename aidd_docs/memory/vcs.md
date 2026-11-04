# VCS

## Setup

- Main branch: `main`
- Platform: GitHub (`cmnemoi/emush_rag`)
- Tickets: none in practice
- Hooks: `make setup-git-hooks` points `core.hooksPath` to `hooks/`; pre-commit lints and type checks, pre-push runs `make check` and `make test`, post-commit runs `make semantic-release`

## Branches

- Work lands directly on `main`; only Dependabot opens branches and pull requests.

## Commits

- Convention: Conventional Commits, read by python-semantic-release to bump the version.
- Format: `type: Description`, description capitalized, imperative mood.
- Types in use: `feat`, `fix`, `refactor`, `ci`, `chore`.
- The post-commit hook amends each commit with the bumped `pyproject.toml` and `uv.lock`: expect the commit hash to change right after committing.

## Commit Strategy

AI should auto commit: never
