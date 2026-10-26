"""Testes do orquestrador de validacao e do escopo por skill.

O `--dry-run` imprime o plano sem executar nada: e assim que se verifica a
selecao de suites sem pagar o custo de empacotar e rodar o smoke.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

from scripts.project_config import (
    COVERAGE_THRESHOLDS,
    DEFAULT_PROFILE,
    PROFILES,
    ProjectConfig,
    read_project_config,
    resolve_suites,
)
from scripts.validate import covering_tests, skills_in

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_validate(*args: str) -> subprocess.CompletedProcess[str]:
    """Executa o validate pelo runner, como uma pessoa faria."""
    return subprocess.run(  # noqa: S603
        [sys.executable, "scripts/dev.py", "validate", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_skills_in_reconhece_skill_pela_pasta_e_pelo_eval() -> None:
    alterados = [
        "skills/resumir-csv/SKILL.md",
        "skills/resumir-csv/scripts/resumir.py",
        "evals/revisar-skill.json",
        "docs/architecture.md",
        "scripts/dev.py",
    ]

    assert skills_in(alterados) == ["resumir-csv", "revisar-skill"]


def test_skills_in_ignora_caminho_que_nao_e_de_skill() -> None:
    assert skills_in(["README.md", "evals/", "skills/"]) == []


def test_cobertura_so_devolve_arquivo_existente() -> None:
    # A skill de exemplo tem teste; uma inventada nao.
    assert covering_tests(["summarize-csv"]) == ["tests/skills/test_summarize_csv.py"]
    assert covering_tests(["skill-que-nao-existe"]) == []


def test_cada_perfil_decide_o_que_bloqueia() -> None:
    config = ProjectConfig(capabilities={"packaging": True, "evals": True})

    def tier(profile: str, name: str) -> str:
        resolved = resolve_suites(replace(config, profile=profile))
        return str(next(t for suite, t, _ in resolved if suite.name == name))

    assert tier("prototipo", "package") == "advisory"
    assert tier("padrao", "package") == "blocking"
    assert tier("prototipo", "check-skills") == "blocking", "skills bloqueiam em todo perfil"
    assert tier("prototipo", "check-docs") == "advisory"
    assert tier("rigoroso", "check-docs") == "blocking"


def test_capacidade_desligada_desliga_a_suite() -> None:
    resolved = resolve_suites(
        ProjectConfig(profile="rigoroso", capabilities={"packaging": False, "evals": False})
    )
    por_nome = {suite.name: (tier, reason) for suite, tier, reason in resolved}

    assert por_nome["package"][0] == "off"
    assert "packaging" in (por_nome["package"][1] or "")
    assert por_nome["check-evals"][0] == "off"


def test_perfil_rigoroso_trata_aviso_de_skill_como_falha() -> None:
    assert ProjectConfig(profile="rigoroso").strict_findings
    assert not ProjectConfig(profile="padrao").strict_findings
    assert not ProjectConfig(profile="prototipo").strict_findings


def test_prototipo_nao_impoe_limite_de_cobertura() -> None:
    assert COVERAGE_THRESHOLDS["prototipo"] is None
    padrao = COVERAGE_THRESHOLDS["padrao"]
    rigoroso = COVERAGE_THRESHOLDS["rigoroso"]
    assert padrao is not None and rigoroso is not None and padrao < rigoroso


def test_estado_ausente_ou_invalido_cai_no_padrao(tmp_path: Path) -> None:
    assert read_project_config(tmp_path).profile == DEFAULT_PROFILE

    (tmp_path / ".template-state.json").write_text(
        json.dumps({"profile": "turbo"}), encoding="utf-8"
    )
    assert read_project_config(tmp_path).profile == DEFAULT_PROFILE
    assert DEFAULT_PROFILE in PROFILES


def test_list_descreve_perfil_capacidades_e_portoes() -> None:
    result = run_validate("--list")

    assert result.returncode == 0, result.stderr
    assert "Perfil:" in result.stdout
    assert "Capacidades:" in result.stdout
    assert "check-skills" in result.stdout


def test_quick_seleciona_somente_as_suites_rapidas() -> None:
    result = run_validate("--quick", "--dry-run")

    assert result.returncode == 0, result.stderr
    assert "pytest" in result.stdout
    assert "--cov" not in result.stdout, "caminho rapido nao mede cobertura"
    assert "smoke_bundles" not in result.stdout


def test_only_e_skip_restringem_a_selecao() -> None:
    only = run_validate("--only", "lint", "--dry-run")
    assert only.returncode == 0, only.stderr
    assert "1 suite(s) — lint" in only.stdout

    skip = run_validate("--skip", "package", "smoke-bundles", "--dry-run")
    assert skip.returncode == 0, skip.stderr
    assert "smoke_bundles" not in skip.stdout


def test_suite_desconhecida_falha_dizendo_como_descobrir() -> None:
    result = run_validate("--only", "inexistente")

    assert result.returncode == 2
    assert "Suite desconhecida" in result.stderr
    assert "--list" in result.stderr


def test_skill_inexistente_falha_em_vez_de_validar_nada() -> None:
    result = run_validate("--skill", "skill-que-nao-existe")

    assert result.returncode == 2
    assert "Skill inexistente" in result.stderr


def test_escopo_por_skill_restringe_pacote_testes_e_lint() -> None:
    result = run_validate("--skill", "summarize-csv", "--dry-run")

    assert result.returncode == 0, result.stderr
    assert "Skills afetadas (1): summarize-csv" in result.stdout
    assert "--skill summarize-csv" in result.stdout, "empacota so a skill pedida"
    assert "tests/skills/test_summarize_csv.py" in result.stdout
    # Execucao parcial nao aplica cobertura global.
    assert "--cov" not in result.stdout
