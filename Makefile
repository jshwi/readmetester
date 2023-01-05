all: install
install: install-deps install-hooks
remove: remove-hooks remove-deps

install-deps:
	@POETRY_VIRTUALENVS_IN_PROJECT=1 poetry install

install-pre-commit:
	@poetry run command -v pre-commit > /dev/null 2>&1 \
		|| poetry run pip --quiet install pre-commit

install-hooks: install-pre-commit
	@poetry run pre-commit install \
		--hook-type pre-commit \
		--hook-type pre-merge-commit \
		--hook-type pre-push \
		--hook-type prepare-commit-msg \
		--hook-type commit-msg \
		--hook-type post-commit \
		--hook-type post-checkout \
		--hook-type post-merge \
		--hook-type post-rewrite

remove-hooks: install-pre-commit
	@poetry run pre-commit uninstall \
		--hook-type pre-commit \
		--hook-type pre-merge-commit \
		--hook-type pre-push \
		--hook-type prepare-commit-msg \
		--hook-type commit-msg \
		--hook-type post-commit \
		--hook-type post-checkout \
		--hook-type post-merge \
		--hook-type post-rewrite

remove-deps:
	rm -rf $(shell dirname $(shell dirname $(shell poetry run which python)))
