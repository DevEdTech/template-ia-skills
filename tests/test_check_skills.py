"""Testes das regras de metadados, estrutura e sincronização das skills."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from scripts.check_skills import (
    body_after_frontmatter,
    check_skills,
    parse_frontmatter,
    validate_skill,
)

SkillFactory = Callable[..., Path]


def test_skill_minima_e_valida(skill_factory: SkillFactory) -> None:
    skill = skill_factory()

    assert validate_skill(skill) == []


def test_frontmatter_ignora_chaves_indentadas() -> None:
    meta = parse_frontmatter('---\nname: x\nmetadata:\n  autor: "time"\n---\n# T\n')

    assert meta == {"name": "x", "metadata": ""}


def test_frontmatter_ausente_ou_incompleto() -> None:
    assert parse_frontmatter("# Sem frontmatter\n") is None
    assert parse_frontmatter("---\nname: x\n# nunca fecha\n") is None
    assert body_after_frontmatter("# Sem frontmatter\n") == ["# Sem frontmatter", ""]


def test_nome_precisa_bater_com_a_pasta(skill_factory: SkillFactory) -> None:
    skill = skill_factory()
    content = (skill / "SKILL.md").read_text(encoding="utf-8")
    (skill / "SKILL.md").write_text(content.replace("name: resumir-csv", "name: outro"), "utf-8")

    assert any("difere do nome da pasta" in error for error in validate_skill(skill))


def test_nome_fora_do_padrao(skill_factory: SkillFactory) -> None:
    skill = skill_factory(name="Resumir_CSV")

    errors = validate_skill(skill)
    assert any("kebab-case" in error for error in errors)


def test_nome_com_termos_demais(skill_factory: SkillFactory) -> None:
    skill = skill_factory(name="resumir-csv-do-time-financeiro-mensal")

    assert any("mais de 5 termos" in error for error in validate_skill(skill))


def test_descricao_curta_demais(skill_factory: SkillFactory) -> None:
    skill = skill_factory(description="Resume CSV.")

    errors = validate_skill(skill)
    assert any("menos de 40 caracteres" in error for error in errors)


def test_descricao_longa_demais(skill_factory: SkillFactory) -> None:
    skill = skill_factory(description="Resume planilhas. Use quando " + "x" * 1100)

    assert any("passa de 1024 caracteres" in error for error in validate_skill(skill))


def test_descricao_sem_gatilho(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        description="Resume arquivos tabulares e produz estatísticas por coluna do arquivo."
    )

    assert any("não indica o acionamento" in error for error in validate_skill(skill))


def test_descricao_com_enchimento(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        description="Esta skill resume planilhas exportadas. Use quando o pedido citar CSV."
    )

    assert any("enchimento" in error for error in validate_skill(skill))


def test_corpo_precisa_de_titulo(skill_factory: SkillFactory) -> None:
    skill = skill_factory(body="Sem título nenhum.\n")

    assert any("título" in error for error in validate_skill(skill))


def test_corpo_longo_demais(skill_factory: SkillFactory) -> None:
    skill = skill_factory(body="# Título\n" + "linha\n" * 600)

    assert any("máximo 500" in error for error in validate_skill(skill))


def test_frontmatter_com_chave_desconhecida(skill_factory: SkillFactory) -> None:
    skill = skill_factory()
    content = (skill / "SKILL.md").read_text(encoding="utf-8")
    (skill / "SKILL.md").write_text(content.replace("---\n\n", "versao: 2\n---\n\n", 1), "utf-8")

    assert any("desconhecida" in error for error in validate_skill(skill))


def test_entrada_nao_prevista_na_raiz(skill_factory: SkillFactory) -> None:
    skill = skill_factory(files={"notas.txt": "rascunho"})

    assert any("não prevista" in error for error in validate_skill(skill))


def test_link_quebrado_e_caminho_absoluto(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body="# Título\n\n[falta](reference/ausente.md) e [raiz](/etc/passwd)\n",
    )

    errors = validate_skill(skill)
    assert any("inexistente" in error for error in errors)
    assert any("absoluto" in error for error in errors)


def test_link_para_fora_da_skill(skill_factory: SkillFactory) -> None:
    skill = skill_factory(body="# Título\n\n[fora](../outra/SKILL.md)\n")

    assert any("fora da skill" in error for error in validate_skill(skill))


def test_arquivo_orfao(skill_factory: SkillFactory) -> None:
    skill = skill_factory(files={"reference/detalhes.md": "# Detalhes\n"})

    assert any("não é citado" in error for error in validate_skill(skill))


def test_referencia_transitiva_alcanca_arquivo(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body="# Título\n\nVeja [detalhes](reference/detalhes.md).\n",
        files={
            "reference/detalhes.md": "# Detalhes\n\nModelo em [saida](../assets/saida.md).\n",
            "assets/saida.md": "# Saída\n",
        },
    )

    assert validate_skill(skill) == []


def test_mencao_em_texto_conta_como_uso(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body=(
            "# Título\n\nRode `python scripts/resumir.py --help`; "
            "o runner do repositório é `scripts/dev.py`.\n"
        ),
        files={"scripts/resumir.py": '"""Doc."""\n\nimport json\n\nprint(json)\n'},
    )

    assert validate_skill(skill) == []


def test_script_precisa_de_docstring_e_snake_case(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body="# Título\n\nRode `scripts/ResumirCSV.py`.\n",
        files={"scripts/ResumirCSV.py": "import json\n"},
    )

    errors = validate_skill(skill)
    assert any("snake_case" in error for error in errors)
    assert any("docstring" in error for error in errors)


def test_script_nao_pode_importar_pacote_nao_declarado(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body="# Título\n\nRode `scripts/resumir.py`.\n",
        files={"scripts/resumir.py": '"""Doc."""\n\nimport pandas\n'},
    )

    assert any("importa `pandas`" in error for error in validate_skill(skill))


def test_requirements_libera_import_de_terceiro(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body="# Título\n\nRode `scripts/resumir.py`.\n",
        files={
            "scripts/resumir.py": '"""Doc."""\n\nimport pandas\n\nprint(pandas)\n',
            "requirements.txt": "# dependência justificada\npandas>=2.0\n",
        },
    )

    assert validate_skill(skill) == []


def test_script_com_erro_de_sintaxe(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body="# Título\n\nRode `scripts/resumir.py`.\n",
        files={"scripts/resumir.py": '"""Doc."""\n\ndef quebrado(\n'},
    )

    assert any("não compila" in error for error in validate_skill(skill))


def test_scripts_nao_aceitam_subpasta_nem_outro_formato(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body="# Título\n\nVeja `scripts/aninhado/interno.py` e `scripts/notas.txt`.\n",
        files={"scripts/aninhado/interno.py": '"""Doc."""\n', "scripts/notas.txt": "x"},
    )

    errors = validate_skill(skill)
    assert any("subpastas" in error for error in errors)
    assert any("não é um script Python" in error for error in errors)


def test_skill_sem_skill_md(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "vazia"
    skill.mkdir(parents=True)

    assert validate_skill(skill) == ["vazia: arquivo SKILL.md ausente."]


def test_check_skills_exige_copias_sincronizadas(
    tmp_path: Path, skill_factory: SkillFactory
) -> None:
    skill_factory(root=tmp_path)

    errors = check_skills(tmp_path)
    assert any(".claude" in error for error in errors)
    assert check_skills(tmp_path, compare_copies=False) == []


def test_check_skills_detecta_divergencia_e_extras(
    tmp_path: Path, skill_factory: SkillFactory
) -> None:
    skill_factory(root=tmp_path)
    for relative in (".claude/skills", ".agents/skills"):
        destination = tmp_path / relative / "resumir-csv"
        destination.mkdir(parents=True)
        (destination / "SKILL.md").write_text("divergente", encoding="utf-8")
        (destination / "extra.md").write_text("sobra", encoding="utf-8")

    errors = check_skills(tmp_path)
    assert any("conteúdo divergente" in error for error in errors)
    assert any("arquivo extra" in error for error in errors)


def test_check_skills_reprova_nome_de_script_repetido(
    tmp_path: Path, skill_factory: SkillFactory
) -> None:
    for name in ("resumir-csv", "resumir-xlsx"):
        skill_factory(
            name=name,
            root=tmp_path,
            body="# Título\n\nRode `scripts/resumir.py`.\n",
            files={"scripts/resumir.py": '"""Doc."""\n'},
        )

    assert any("repetido" in error for error in check_skills(tmp_path, compare_copies=False))


def test_check_skills_sem_skills(tmp_path: Path) -> None:
    assert any("Nenhuma skill" in error for error in check_skills(tmp_path))


def test_repositorio_atual_passa_nas_regras(project_root: Path) -> None:
    assert check_skills(project_root, compare_copies=False) == []
