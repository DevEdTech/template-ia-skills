"""Testes da personalização do template."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts.setup_project import setup_project, slugify

STATE = {
    "projectName": "skills-project-template",
    "displayName": "Skills Project Template",
    "description": "Template para criar skills.",
    "repository": "https://github.com/DevEdTech/project-template-skills",
    "exampleRemoved": False,
}


def _template(root: Path) -> None:
    (root / ".template-state.json").write_text(json.dumps(STATE), encoding="utf-8")
    (root / "pyproject.toml").write_text(
        'name = "skills-project-template"\ndescription = "Template para criar skills."\n',
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "# skills-project-template\n\nSkills Project Template.\n"
        "https://github.com/DevEdTech/project-template-skills\n",
        encoding="utf-8",
    )
    (root / "tasks.md").write_text("# Tarefas\n\n- [ ] antiga\n", encoding="utf-8")
    example = root / "skills" / "summarize-csv"
    example.mkdir(parents=True)
    (example / "SKILL.md").write_text("# Resumir CSV\n", encoding="utf-8")
    (root / "evals").mkdir()
    (root / "evals" / "summarize-csv.json").write_text("{}", encoding="utf-8")
    tests = root / "tests" / "skills"
    tests.mkdir(parents=True)
    (tests / "test_summarize_csv.py").write_text("# teste\n", encoding="utf-8")


def test_slug_recusa_nome_invalido() -> None:
    with pytest.raises(ValueError, match="começando por letra"):
        slugify("42-skills")


def test_dry_run_apenas_planeja(tmp_path: Path) -> None:
    _template(tmp_path)

    actions = setup_project(tmp_path, name="Skills Financeiro", remove_example=True, dry_run=True)

    assert any("skills-financeiro" in action for action in actions)
    assert any("demonstração" in action for action in actions)
    assert (tmp_path / "skills" / "summarize-csv").is_dir()
    assert "skills-project-template" in (tmp_path / "pyproject.toml").read_text(encoding="utf-8")


def test_personaliza_arquivos_e_estado(tmp_path: Path) -> None:
    _template(tmp_path)

    setup_project(
        tmp_path,
        name="Skills Financeiro",
        display_name="Skills do Financeiro",
        description="Skills do time financeiro.",
        repository="https://github.com/org/skills-financeiro",
    )

    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    state = json.loads((tmp_path / ".template-state.json").read_text(encoding="utf-8"))
    assert "skills-financeiro" in pyproject
    assert "Skills do time financeiro." in pyproject
    assert "Skills do Financeiro" in readme
    assert "org/skills-financeiro" in readme
    assert state["projectName"] == "skills-financeiro"
    assert state["exampleRemoved"] is False


def test_remove_exemplo_e_zera_tarefas(tmp_path: Path) -> None:
    _template(tmp_path)

    setup_project(tmp_path, remove_example=True, reset_tasks=True)

    state = json.loads((tmp_path / ".template-state.json").read_text(encoding="utf-8"))
    assert not (tmp_path / "skills" / "summarize-csv").exists()
    assert not (tmp_path / "evals" / "summarize-csv.json").exists()
    assert not (tmp_path / "tests" / "skills" / "test_summarize_csv.py").exists()
    assert state["exampleRemoved"] is True
    assert "Nenhuma tarefa" in (tmp_path / "tasks.md").read_text(encoding="utf-8")


def test_repeticao_e_idempotente(tmp_path: Path) -> None:
    _template(tmp_path)
    setup_project(tmp_path, name="skills-financeiro", remove_example=True)
    before = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")

    actions = setup_project(tmp_path, name="skills-financeiro", remove_example=True)

    assert (tmp_path / "pyproject.toml").read_text(encoding="utf-8") == before
    assert actions == ["nada a fazer: o projeto já está personalizado"]


def test_falha_restaura_estado_anterior(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _template(tmp_path)
    original = (tmp_path / "README.md").read_text(encoding="utf-8")

    def explode(*_args: object, **_kwargs: object) -> None:
        raise OSError("disco cheio")

    monkeypatch.setattr("scripts.setup_project.shutil.move", explode)
    with pytest.raises(OSError, match="disco cheio"):
        setup_project(tmp_path, name="skills-financeiro", remove_example=True)

    assert (tmp_path / "README.md").read_text(encoding="utf-8") == original
    assert (tmp_path / "skills" / "summarize-csv").is_dir()
