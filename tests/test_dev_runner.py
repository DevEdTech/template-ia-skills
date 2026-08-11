"""Testes do runner de tarefas e da coerência do ferramental."""

from __future__ import annotations

import tomllib
from collections.abc import Sequence
from pathlib import Path

import pytest
from scripts import dev

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def recorded(monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    """Substitui a execução real por um registro dos comandos montados."""
    commands: list[list[str]] = []

    def fake_run(cmd: Sequence[str]) -> int:
        commands.append(list(cmd))
        return 0

    monkeypatch.setattr(dev, "_run", fake_run)
    return commands


def test_help_lista_todas_as_tarefas(capsys: pytest.CaptureFixture[str]) -> None:
    assert dev.main([]) == 0

    output = capsys.readouterr().out
    for task in dev.TASKS:
        assert task in output


def test_tarefa_desconhecida_retorna_codigo_dois(capsys: pytest.CaptureFixture[str]) -> None:
    assert dev.main(["inexistente"]) == 2
    assert "Tarefa desconhecida" in capsys.readouterr().err


def test_toda_tarefa_monta_um_comando(recorded: list[list[str]]) -> None:
    # `audit` e `check-workflows` dependem de rede/uv e são exercitadas à parte.
    ignoradas = {"audit", "check-workflows"}
    for name in dev.TASKS:
        if name in ignoradas:
            continue
        assert dev.main([name]) == 0, name

    assert len(recorded) >= len(dev.TASKS) - len(ignoradas)


def test_validate_roda_a_sequencia_completa(recorded: list[list[str]]) -> None:
    assert dev.main(["validate"]) == 0

    executados = [" ".join(cmd) for cmd in recorded]
    for esperado in (
        "sync_skills.py",
        "check_skills.py",
        "check_evals.py",
        "check_docs.py",
        "ruff",
        "mypy",
        "pytest",
        "package_skills.py",
        "smoke_bundles.py",
    ):
        assert any(esperado in cmd for cmd in executados), esperado


def test_validate_para_no_primeiro_erro(monkeypatch: pytest.MonkeyPatch) -> None:
    chamadas: list[list[str]] = []

    def fake_run(cmd: Sequence[str]) -> int:
        chamadas.append(list(cmd))
        return 1

    monkeypatch.setattr(dev, "_run", fake_run)

    assert dev.main(["validate"]) == 1
    assert len(chamadas) == 1


def test_eval_sheet_aceita_nome_da_skill(recorded: list[list[str]]) -> None:
    assert dev.main(["eval-sheet", "summarize-csv"]) == 0

    assert recorded[-1][-3:] == ["--sheet", "--skill", "summarize-csv"]


def test_interrupcao_do_usuario(monkeypatch: pytest.MonkeyPatch) -> None:
    def interrompe(cmd: Sequence[str]) -> int:
        raise KeyboardInterrupt

    monkeypatch.setattr(dev, "_run", interrompe)

    assert dev.main(["test"]) == 130


def test_check_workflows_sem_diretorio(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(dev, "PROJECT_ROOT", tmp_path)

    assert dev.task_check_workflows([]) == 0
    assert "Nenhum workflow" in capsys.readouterr().out


def test_dependencias_de_dev_espelhadas_no_requirements() -> None:
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    grupo = sorted(pyproject["dependency-groups"]["dev"])
    arquivo = sorted(
        line.strip()
        for line in (PROJECT_ROOT / "requirements-dev.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    )

    assert grupo == arquivo


def test_tarefas_relevantes_documentadas_no_readme() -> None:
    # Variações de conveniência não precisam de linha própria na tabela.
    variacoes = {"format-check", "lint-fix"}
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    ausentes = {name for name in dev.TASKS if f"dev.py {name}" not in readme} - variacoes

    assert ausentes == set()
