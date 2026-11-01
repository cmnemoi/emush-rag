all: setup-env-variables setup-git-hooks install check test build-watch

build-watch:
	docker compose up --build --watch

check: check-format check-lint check-types

check-format:
	uv run ruff format . --diff

check-lint:
	uv run ruff check .

check-types:
	uv run mypy .

index-documents:
	mush-wikis-scrap > data/wikis.json
	rm -rf chroma
	uv run emush_rag/cli/index_documents.py
	scp -P 49512 -r ./chroma askneron@cmnemoi.com:~/www/new_chroma
	ssh askneron@cmnemoi.com -p 49512 "rm -rf ~/www/chroma && mv ~/www/new_chroma ~/www/chroma && rm -rf ~/www/new_chroma"
	ssh askneron@cmnemoi.com -p 49512 "docker compose -f compose.prod.yml -f ~/compose.vps.yaml down && docker compose -f compose.prod.yml -f ~/compose.vps.yaml up -d --remove-orphans"

install:
	uv lock
	uv sync --locked --group dev --group lint --group test

lint:
	uv run ruff format .
	uv run ruff check . --fix

semantic-release:
	uv run semantic-release version --no-changelog --no-push --no-vcs-release --skip-build --no-commit --no-tag
	uv lock
	git add pyproject.toml uv.lock
	git commit --allow-empty --amend --no-edit 

setup-env-variables:
	cp .env.example .env

setup-git-hooks:
	chmod +x hooks/pre-commit
	chmod +x hooks/pre-push
	chmod +x hooks/post-commit
	git config core.hooksPath hooks

run:
	docker compose up -d --watch

run-lite:
	docker compose -f compose.dev.yml up --watch

test:
	uv run python -m pytest -v --cov=emush_rag --cov-report=xml

test-fast:
	uv run python -m pytest -v tests/unit tests/integration

upgrade-dependencies:
	uv lock --upgrade

watch:
	docker compose up --watch

.PHONY: all build-watch check check-format check-lint check-types install lint semantic-release setup-env-variables setup-git-hooks test upgrade-dependencies