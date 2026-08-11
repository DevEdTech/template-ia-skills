# Atalhos de conveniencia para macOS e Linux.
# No Windows (ou em qualquer SO), use diretamente: python scripts/dev.py <tarefa>
#
# Todos os alvos delegam ao runner cross-platform scripts/dev.py, que e a
# fonte unica de verdade das tarefas.

PY ?= python

.PHONY: help format format-check lint lint-fix typecheck test test-cov sync-skills check-skills check-evals check-docs new-skill package smoke-bundles eval-sheet validate

help:
	@$(PY) scripts/dev.py help

format:
	@$(PY) scripts/dev.py format

format-check:
	@$(PY) scripts/dev.py format-check

lint:
	@$(PY) scripts/dev.py lint

lint-fix:
	@$(PY) scripts/dev.py lint-fix

typecheck:
	@$(PY) scripts/dev.py typecheck

test:
	@$(PY) scripts/dev.py test

test-cov:
	@$(PY) scripts/dev.py test-cov

sync-skills:
	@$(PY) scripts/dev.py sync-skills

check-skills:
	@$(PY) scripts/dev.py check-skills

check-evals:
	@$(PY) scripts/dev.py check-evals

check-docs:
	@$(PY) scripts/dev.py check-docs

new-skill:
	@$(PY) scripts/dev.py new-skill $(ARGS)

package:
	@$(PY) scripts/dev.py package

smoke-bundles:
	@$(PY) scripts/dev.py smoke-bundles

eval-sheet:
	@$(PY) scripts/dev.py eval-sheet $(ARGS)

validate:
	@$(PY) scripts/dev.py validate
