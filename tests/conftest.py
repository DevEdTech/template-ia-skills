"""Configuração e fixtures compartilhadas de teste.

A fixture `skill_script` carrega um script de skill pelo caminho: as pastas de
skill não são pacotes Python (o nome tem hífen e a skill precisa ser
distribuível), então o import normal não alcança esses arquivos.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Raiz do repositório."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def skill_script() -> Callable[[str, str], ModuleType]:
    """Carrega `skills/<skill>/scripts/<arquivo>` como módulo."""

    def load(skill: str, filename: str) -> ModuleType:
        path = PROJECT_ROOT / "skills" / skill / "scripts" / filename
        name = f"skill_{skill.replace('-', '_')}_{path.stem}"
        if name in sys.modules:
            return sys.modules[name]
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:  # pragma: no cover - caminho inexistente
            raise ImportError(f"Não foi possível carregar {path}.")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    return load


@pytest.fixture
def skill_factory(tmp_path: Path) -> Callable[..., Path]:
    """Cria um repositório mínimo com uma skill válida, para os testes de regras."""

    def make(
        name: str = "resumir-csv",
        *,
        description: str = (
            "Resume um arquivo CSV em estatísticas por coluna. Use quando o pedido "
            "citar planilha exportada ou conferência de dados."
        ),
        body: str = "# Resumir CSV\n\n## Objetivo\n\nResumir.\n",
        files: dict[str, str] | None = None,
        root: Path | None = None,
    ) -> Path:
        base = root if root is not None else tmp_path
        skill_dir = base / "skills" / name
        skill_dir.mkdir(parents=True)
        frontmatter = f"---\nname: {name}\ndescription: {description}\n---\n\n"
        (skill_dir / "SKILL.md").write_text(frontmatter + body, encoding="utf-8")
        for relative, content in (files or {}).items():
            destination = skill_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
        return skill_dir

    return make


@pytest.fixture
def eval_factory(tmp_path: Path) -> Callable[..., Path]:
    """Cria um `evals/<skill>.json` completo, para os testes de cenários."""

    def make(name: str = "resumir-csv", root: Path | None = None, **overrides: object) -> Path:
        base = root if root is not None else tmp_path
        payload: dict[str, object] = {
            "skill": name,
            "trigger": [
                {"prompt": "Resume essa planilha.", "should_trigger": True},
                {"prompt": "O que tem nesse CSV?", "should_trigger": True},
                {"prompt": "Converta o CSV para JSON.", "should_trigger": False},
            ],
            "execution": [
                {
                    "prompt": "Resuma vendas.csv.",
                    "expect": ["Rodou o script.", "Escreveu o relatório."],
                    "red_flags": ["Inventou estatística."],
                }
            ],
        }
        payload.update(overrides)
        evals = base / "evals"
        evals.mkdir(parents=True, exist_ok=True)
        path = evals / f"{name}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    return make
