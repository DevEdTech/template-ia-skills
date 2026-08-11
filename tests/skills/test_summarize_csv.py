"""Testes do script da skill de demonstração summarize-csv."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

SkillScript = Callable[[str, str], ModuleType]


@pytest.fixture(scope="module")
def module(skill_script: SkillScript) -> ModuleType:
    return skill_script("summarize-csv", "summarize_csv.py")


def _csv(tmp_path: Path, content: str, name: str = "dados.csv") -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_identifica_faltantes(module: ModuleType) -> None:
    assert module.is_missing("  ") is True
    assert module.is_missing("N/A") is True
    assert module.is_missing("0") is False


def test_converte_numeros_em_formatos_comuns(module: ModuleType) -> None:
    assert module.parse_number("1.234,56") == 1234.56
    assert module.parse_number("1234,56") == 1234.56
    assert module.parse_number("1234.56") == 1234.56
    assert module.parse_number("abc") is None
    assert module.parse_number("   ") is None


def test_resume_colunas_numericas_e_de_texto(module: ModuleType, tmp_path: Path) -> None:
    path = _csv(tmp_path, "produto,valor\nA,10\nB,20\nA,30\n")

    summary = module.summarize_csv(path)

    assert summary["rows"] == 3
    assert summary["columns"] == 2
    produto, valor = summary["column_summaries"]
    assert produto["type"] == "text"
    assert produto["unique"] == 2
    assert produto["top_values"][0] == {"value": "A", "count": 2}
    assert valor["type"] == "numeric"
    assert valor["statistics"] == {"min": 10.0, "max": 30.0, "mean": 20.0, "median": 20.0}


def test_conta_faltantes_e_linhas_irregulares(module: ModuleType, tmp_path: Path) -> None:
    path = _csv(tmp_path, "a,b\n1,\n2\n\n3,x\n")

    summary = module.summarize_csv(path)

    coluna_b = summary["column_summaries"][1]
    assert summary["rows"] == 3
    assert summary["ragged_rows"] == 1
    assert coluna_b["missing"] == 2
    assert coluna_b["filled"] == 1


def test_respeita_delimitador_e_limite_de_valores(module: ModuleType, tmp_path: Path) -> None:
    path = _csv(tmp_path, "a;b\nx;1\ny;2\nz;3\n")

    summary = module.summarize_csv(path, delimiter=";", max_values=2)

    assert summary["delimiter"] == ";"
    assert len(summary["column_summaries"][0]["top_values"]) == 2


def test_arquivo_sem_linhas_de_dados(module: ModuleType, tmp_path: Path) -> None:
    path = _csv(tmp_path, "a,b\n")

    summary = module.summarize_csv(path)

    assert summary["rows"] == 0
    assert summary["column_summaries"][0]["type"] == "text"
    assert summary["column_summaries"][0]["top_values"] == []


def test_cabecalho_sem_nome_recebe_rotulo(module: ModuleType, tmp_path: Path) -> None:
    path = _csv(tmp_path, "a,,c\n1,2,3\n")

    summary = module.summarize_csv(path)

    assert [column["name"] for column in summary["column_summaries"]] == ["a", "coluna_2", "c"]


def test_arquivo_vazio_e_recusado(module: ModuleType, tmp_path: Path) -> None:
    path = _csv(tmp_path, "")

    with pytest.raises(ValueError, match="está vazio"):
        module.summarize_csv(path)


def test_cabecalho_em_branco_e_recusado(module: ModuleType, tmp_path: Path) -> None:
    path = _csv(tmp_path, ",,\n1,2,3\n")

    with pytest.raises(ValueError, match="nomes de coluna"):
        module.summarize_csv(path)


def test_max_values_invalido(module: ModuleType, tmp_path: Path) -> None:
    path = _csv(tmp_path, "a\n1\n")

    with pytest.raises(ValueError, match="maior que zero"):
        module.summarize_csv(path, max_values=0)


def test_cli_grava_json(
    module: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = _csv(tmp_path, "a\n1\n2\n")
    output = tmp_path / "resumo.json"
    monkeypatch.setattr(
        "sys.argv", ["summarize_csv.py", "--input", str(path), "--output", str(output)]
    )

    assert module.main() == 0
    assert json.loads(output.read_text(encoding="utf-8"))["rows"] == 2
    assert "Resumo gravado" in capsys.readouterr().out


def test_cli_imprime_na_saida_padrao(
    module: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = _csv(tmp_path, "a\n1\n")
    monkeypatch.setattr("sys.argv", ["summarize_csv.py", "--input", str(path)])

    assert module.main() == 0
    assert json.loads(capsys.readouterr().out)["file"] == "dados.csv"


def test_cli_reporta_arquivo_inexistente(
    module: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("sys.argv", ["summarize_csv.py", "--input", str(tmp_path / "nao.csv")])

    assert module.main() == 1
    assert "não encontrado" in capsys.readouterr().err


def test_cli_reporta_arquivo_invalido(
    module: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = _csv(tmp_path, "")
    monkeypatch.setattr("sys.argv", ["summarize_csv.py", "--input", str(path)])

    assert module.main() == 1
    assert "Não foi possível resumir" in capsys.readouterr().err
