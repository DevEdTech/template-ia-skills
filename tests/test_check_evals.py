"""Testes da validação dos cenários de avaliação."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from scripts.check_evals import check_evals, render_sheet

SkillFactory = Callable[..., Path]
EvalFactory = Callable[..., Path]


def test_cenarios_completos_passam(
    tmp_path: Path, skill_factory: SkillFactory, eval_factory: EvalFactory
) -> None:
    skill_factory(root=tmp_path)
    eval_factory(root=tmp_path)

    assert check_evals(tmp_path) == []


def test_skill_sem_arquivo_de_avaliacao(tmp_path: Path, skill_factory: SkillFactory) -> None:
    skill_factory(root=tmp_path)

    assert any("ausente" in error for error in check_evals(tmp_path))


def test_arquivo_de_avaliacao_orfao(tmp_path: Path, eval_factory: EvalFactory) -> None:
    eval_factory(name="inexistente", root=tmp_path)

    assert any("não existe skill" in error for error in check_evals(tmp_path))


def test_json_invalido(tmp_path: Path, skill_factory: SkillFactory) -> None:
    skill_factory(root=tmp_path)
    evals = tmp_path / "evals"
    evals.mkdir()
    (evals / "resumir-csv.json").write_text("{quebrado", encoding="utf-8")

    assert any("JSON inválido" in error for error in check_evals(tmp_path))


def test_chaves_de_topo_erradas(tmp_path: Path, skill_factory: SkillFactory) -> None:
    skill_factory(root=tmp_path)
    evals = tmp_path / "evals"
    evals.mkdir()
    (evals / "resumir-csv.json").write_text(json.dumps({"skill": "resumir-csv"}), encoding="utf-8")

    assert any("chaves" in error for error in check_evals(tmp_path))


def test_campo_skill_divergente(
    tmp_path: Path, skill_factory: SkillFactory, eval_factory: EvalFactory
) -> None:
    skill_factory(root=tmp_path)
    eval_factory(root=tmp_path, skill="outra")

    assert any("difere do arquivo" in error for error in check_evals(tmp_path))


def test_gatilhos_insuficientes(
    tmp_path: Path, skill_factory: SkillFactory, eval_factory: EvalFactory
) -> None:
    skill_factory(root=tmp_path)
    eval_factory(root=tmp_path, trigger=[{"prompt": "Resume.", "should_trigger": True}])

    assert any("ao menos 3 casos" in error for error in check_evals(tmp_path))


def test_falta_caso_negativo(
    tmp_path: Path, skill_factory: SkillFactory, eval_factory: EvalFactory
) -> None:
    skill_factory(root=tmp_path)
    eval_factory(
        root=tmp_path,
        trigger=[{"prompt": f"Pedido {i}", "should_trigger": True} for i in range(3)],
    )

    assert any("caso negativo" in error for error in check_evals(tmp_path))


def test_falta_caso_positivo(
    tmp_path: Path, skill_factory: SkillFactory, eval_factory: EvalFactory
) -> None:
    skill_factory(root=tmp_path)
    eval_factory(
        root=tmp_path,
        trigger=[{"prompt": f"Pedido {i}", "should_trigger": False} for i in range(3)],
    )

    assert any("caso positivo" in error for error in check_evals(tmp_path))


def test_caso_de_gatilho_malformado(
    tmp_path: Path, skill_factory: SkillFactory, eval_factory: EvalFactory
) -> None:
    skill_factory(root=tmp_path)
    eval_factory(
        root=tmp_path,
        trigger=[
            {"prompt": "", "should_trigger": True},
            {"prompt": "ok", "should_trigger": "sim"},
            {"prompt": "ok", "extra": 1},
        ],
    )

    errors = check_evals(tmp_path)
    assert any("`prompt` vazio" in error for error in errors)
    assert any("true ou false" in error for error in errors)
    assert any("exatamente as chaves" in error for error in errors)


def test_execucao_incompleta(
    tmp_path: Path, skill_factory: SkillFactory, eval_factory: EvalFactory
) -> None:
    skill_factory(root=tmp_path)
    eval_factory(
        root=tmp_path,
        execution=[{"prompt": "Resuma.", "expect": ["um só"], "red_flags": []}],
    )

    errors = check_evals(tmp_path)
    assert any("`expect` precisa" in error for error in errors)
    assert any("`red_flags` precisa" in error for error in errors)


def test_execucao_ausente(
    tmp_path: Path, skill_factory: SkillFactory, eval_factory: EvalFactory
) -> None:
    skill_factory(root=tmp_path)
    eval_factory(root=tmp_path, execution=[])

    assert any("ao menos um cenário" in error for error in check_evals(tmp_path))


def test_folha_de_avaliacao_lista_prompts(
    tmp_path: Path, skill_factory: SkillFactory, eval_factory: EvalFactory
) -> None:
    skill_factory(root=tmp_path)
    eval_factory(root=tmp_path)

    sheet = render_sheet(tmp_path)
    assert "## resumir-csv" in sheet
    assert "(deve acionar) Resume essa planilha." in sheet
    assert "(NÃO deve acionar) Converta o CSV para JSON." in sheet
    assert "esperado: Rodou o script." in sheet
    assert render_sheet(tmp_path, "resumir-csv") == sheet


def test_repositorio_atual_tem_cenarios_completos(project_root: Path) -> None:
    assert check_evals(project_root) == []
