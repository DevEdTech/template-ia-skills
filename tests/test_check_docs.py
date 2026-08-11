"""Testes da validação de links, tarefas e catálogo da documentação."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from scripts.check_docs import check_docs

SkillFactory = Callable[..., Path]


def _docs(root: Path, readme: str = "", catalog: str | None = None) -> None:
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text(readme, encoding="utf-8")
    if catalog is not None:
        (root / "docs" / "agents.md").write_text(catalog, encoding="utf-8")


def test_aceita_link_e_tarefa_documentada(tmp_path: Path) -> None:
    _docs(tmp_path, "[Arquitetura](docs/architecture.md) e `python scripts/dev.py validate`.")
    (tmp_path / "docs/architecture.md").write_text("# Arquitetura\n", encoding="utf-8")

    assert check_docs(tmp_path) == []


def test_encontra_link_e_tarefa_inexistentes(tmp_path: Path) -> None:
    _docs(tmp_path, "[Ausente](docs/nope.md) e `python scripts/dev.py nao-existe`.")

    assert len(check_docs(tmp_path)) == 2


def test_catalogo_precisa_listar_todas_as_skills(
    tmp_path: Path, skill_factory: SkillFactory
) -> None:
    skill_factory(root=tmp_path)
    _docs(tmp_path, catalog="# Catálogo\n")

    assert any("não está no catálogo" in error for error in check_docs(tmp_path))


def test_catalogo_com_skill_inexistente(tmp_path: Path) -> None:
    _docs(tmp_path, catalog="- **fantasma** — skill que não existe.\n")

    assert any("skill inexistente" in error for error in check_docs(tmp_path))


def test_catalogo_coerente_passa(tmp_path: Path, skill_factory: SkillFactory) -> None:
    skill_factory(root=tmp_path)
    _docs(tmp_path, catalog="- **resumir-csv** — resume planilhas quando o pedido citar CSV.\n")

    assert check_docs(tmp_path) == []


def test_identificador_do_template_apos_setup(tmp_path: Path) -> None:
    _docs(tmp_path, "Projeto skills-project-template.")
    (tmp_path / ".template-state.json").write_text(
        json.dumps({"projectName": "skills-financeiro"}), encoding="utf-8"
    )

    assert any("identificador original" in error for error in check_docs(tmp_path))


def test_documentacao_do_repositorio_esta_coerente(project_root: Path) -> None:
    assert check_docs(project_root) == []
