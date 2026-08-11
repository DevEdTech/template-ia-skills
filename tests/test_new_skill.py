"""Testes do gerador de skills."""

from __future__ import annotations

from pathlib import Path

import pytest
from scripts.check_evals import check_evals
from scripts.check_skills import validate_skill
from scripts.new_skill import create_skill, slugify


def test_slug_normaliza_acentos_e_espacos() -> None:
    assert slugify("Resumir Planilhã Mensal") == "resumir-planilha-mensal"


def test_slug_recusa_nome_invalido() -> None:
    with pytest.raises(ValueError, match="começando por letra"):
        slugify("123")
    with pytest.raises(ValueError, match="5 termos"):
        slugify("uma skill com termos demais aqui")


def test_dry_run_nao_cria_arquivos(tmp_path: Path) -> None:
    planned = create_skill(tmp_path, "resumir planilha", {"scripts"}, dry_run=True)

    assert [path.name for path in planned] == [
        "SKILL.md",
        "resumir_planilha.py",
        "resumir-planilha.json",
    ]
    assert not (tmp_path / "skills").exists()


def test_esqueleto_gerado_passa_nas_verificacoes(tmp_path: Path) -> None:
    create_skill(tmp_path, "resumir planilha", {"scripts", "assets", "reference"})

    skill = tmp_path / "skills" / "resumir-planilha"
    assert validate_skill(skill) == []
    assert check_evals(tmp_path) == []
    assert (skill / "scripts/resumir_planilha.py").is_file()
    assert (skill / "assets/output-template.md").is_file()
    assert (skill / "reference/details.md").is_file()


def test_esqueleto_minimo_sem_partes_opcionais(tmp_path: Path) -> None:
    create_skill(tmp_path, "resumir planilha", set())

    skill = tmp_path / "skills" / "resumir-planilha"
    assert sorted(path.name for path in skill.iterdir()) == ["SKILL.md"]
    assert validate_skill(skill) == []


def test_recusa_parte_desconhecida(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Partes desconhecidas"):
        create_skill(tmp_path, "resumir planilha", {"docs"})


def test_recusa_skill_existente(tmp_path: Path) -> None:
    create_skill(tmp_path, "resumir planilha", set())

    with pytest.raises(FileExistsError):
        create_skill(tmp_path, "resumir planilha", set())


def test_recusa_avaliacao_existente(tmp_path: Path) -> None:
    (tmp_path / "evals").mkdir()
    (tmp_path / "evals" / "resumir-planilha.json").write_text("{}", encoding="utf-8")

    with pytest.raises(FileExistsError, match="avaliação"):
        create_skill(tmp_path, "resumir planilha", set())
