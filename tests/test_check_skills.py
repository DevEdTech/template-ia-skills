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


def mensagens(skill_dir: Path, *, incluir_avisos: bool = False) -> list[str]:
    """Mensagens dos achados de uma skill.

    Por padrao so os que reprovam: a maioria dos testes afirma o que falha, e
    heuristica agora avisa em vez de reprovar. `incluir_avisos` cobre os testes
    que falam das heuristicas e das dispensas.
    """
    return [
        finding.message
        for finding in validate_skill(skill_dir)
        if incluir_avisos or finding.is_error
    ]


def achados(skill_dir: Path) -> dict[str, str | None]:
    """Regra -> motivo da dispensa (ou None), para afirmar severidade."""
    return {finding.rule: finding.waiver for finding in validate_skill(skill_dir)}


def test_skill_minima_e_valida(skill_factory: SkillFactory) -> None:
    skill = skill_factory()

    assert mensagens(skill) == []


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

    assert any("difere do nome da pasta" in m for m in mensagens(skill, incluir_avisos=True))


def test_nome_fora_do_padrao(skill_factory: SkillFactory) -> None:
    skill = skill_factory(name="Resumir_CSV")

    errors = mensagens(skill, incluir_avisos=True)
    assert any("kebab-case" in error for error in errors)


def test_nome_com_termos_demais(skill_factory: SkillFactory) -> None:
    skill = skill_factory(name="resumir-csv-do-time-financeiro-mensal")

    assert any("mais de 5 termos" in m for m in mensagens(skill, incluir_avisos=True))


def test_descricao_curta_demais(skill_factory: SkillFactory) -> None:
    skill = skill_factory(description="Resume CSV.")

    errors = mensagens(skill, incluir_avisos=True)
    assert any("menos de 40 caracteres" in error for error in errors)


def test_descricao_longa_demais(skill_factory: SkillFactory) -> None:
    skill = skill_factory(description="Resume planilhas. Use quando " + "x" * 1100)

    assert any("passa de 1024 caracteres" in m for m in mensagens(skill, incluir_avisos=True))


def test_descricao_sem_gatilho(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        description="Resume arquivos tabulares e produz estatísticas por coluna do arquivo."
    )

    # Heuristica: avisa, nao reprova. Uma varredura de substring nao sabe se o
    # texto ensina o acionamento.
    assert any("não indique o acionamento" in m for m in mensagens(skill, incluir_avisos=True))
    assert mensagens(skill) == []
    assert "description-trigger" in achados(skill)


def test_descricao_com_enchimento(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        description="Esta skill resume planilhas exportadas. Use quando o pedido citar CSV."
    )

    assert any("enchimento" in m for m in mensagens(skill, incluir_avisos=True))
    # Tambem heuristica: o prefixo e um indicio, nao uma prova.
    assert mensagens(skill) == []


def test_corpo_precisa_de_titulo(skill_factory: SkillFactory) -> None:
    skill = skill_factory(body="Sem título nenhum.\n")

    assert any("título" in m for m in mensagens(skill, incluir_avisos=True))


def test_corpo_longo_demais(skill_factory: SkillFactory) -> None:
    skill = skill_factory(body="# Título\n" + "linha\n" * 600)

    assert any("máximo 500" in m for m in mensagens(skill, incluir_avisos=True))


def test_frontmatter_com_chave_desconhecida(skill_factory: SkillFactory) -> None:
    skill = skill_factory()
    content = (skill / "SKILL.md").read_text(encoding="utf-8")
    (skill / "SKILL.md").write_text(content.replace("---\n\n", "versao: 2\n---\n\n", 1), "utf-8")

    assert any("desconhecida" in m for m in mensagens(skill, incluir_avisos=True))


def test_entrada_nao_prevista_na_raiz(skill_factory: SkillFactory) -> None:
    skill = skill_factory(files={"notas.txt": "rascunho"})

    assert any("não prevista" in m for m in mensagens(skill, incluir_avisos=True))


def test_link_quebrado_e_caminho_absoluto(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body="# Título\n\n[falta](reference/ausente.md) e [raiz](/etc/passwd)\n",
    )

    errors = mensagens(skill, incluir_avisos=True)
    assert any("inexistente" in error for error in errors)
    assert any("absoluto" in error for error in errors)


def test_link_para_fora_da_skill(skill_factory: SkillFactory) -> None:
    skill = skill_factory(body="# Título\n\n[fora](../outra/SKILL.md)\n")

    assert any("fora da skill" in m for m in mensagens(skill, incluir_avisos=True))


def test_arquivo_orfao(skill_factory: SkillFactory) -> None:
    skill = skill_factory(files={"reference/detalhes.md": "# Detalhes\n"})

    assert any("não é citado" in m for m in mensagens(skill, incluir_avisos=True))


def test_referencia_transitiva_alcanca_arquivo(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body="# Título\n\nVeja [detalhes](reference/detalhes.md).\n",
        files={
            "reference/detalhes.md": "# Detalhes\n\nModelo em [saida](../assets/saida.md).\n",
            "assets/saida.md": "# Saída\n",
        },
    )

    assert mensagens(skill) == []


def test_mencao_em_texto_conta_como_uso(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body=(
            "# Título\n\nRode `python scripts/resumir.py --help`; "
            "o runner do repositório é `scripts/dev.py`.\n"
        ),
        files={"scripts/resumir.py": '"""Doc."""\n\nimport json\n\nprint(json)\n'},
    )

    assert mensagens(skill) == []


def test_script_precisa_de_docstring_e_snake_case(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body="# Título\n\nRode `scripts/ResumirCSV.py`.\n",
        files={"scripts/ResumirCSV.py": "import json\n"},
    )

    errors = mensagens(skill, incluir_avisos=True)
    assert any("snake_case" in error for error in errors)
    assert any("docstring" in error for error in errors)


def test_script_nao_pode_importar_pacote_nao_declarado(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body="# Título\n\nRode `scripts/resumir.py`.\n",
        files={"scripts/resumir.py": '"""Doc."""\n\nimport pandas\n'},
    )

    assert any("importa `pandas`" in m for m in mensagens(skill, incluir_avisos=True))


def test_requirements_libera_import_de_terceiro(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body="# Título\n\nRode `scripts/resumir.py`.\n",
        files={
            "scripts/resumir.py": '"""Doc."""\n\nimport pandas\n\nprint(pandas)\n',
            "requirements.txt": "# dependência justificada\npandas>=2.0\n",
        },
    )

    assert mensagens(skill) == []


def test_script_com_erro_de_sintaxe(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body="# Título\n\nRode `scripts/resumir.py`.\n",
        files={"scripts/resumir.py": '"""Doc."""\n\ndef quebrado(\n'},
    )

    assert any("não compila" in m for m in mensagens(skill, incluir_avisos=True))


def test_scripts_nao_aceitam_subpasta_nem_outro_formato(skill_factory: SkillFactory) -> None:
    skill = skill_factory(
        body="# Título\n\nVeja `scripts/aninhado/interno.py` e `scripts/notas.txt`.\n",
        files={"scripts/aninhado/interno.py": '"""Doc."""\n', "scripts/notas.txt": "x"},
    )

    errors = mensagens(skill, incluir_avisos=True)
    assert any("subpastas" in error for error in errors)
    assert any("não é um script Python" in error for error in errors)


def test_skill_sem_skill_md(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "vazia"
    skill.mkdir(parents=True)

    assert mensagens(skill) == ["vazia: arquivo SKILL.md ausente."]


def test_check_skills_exige_copias_sincronizadas(
    tmp_path: Path, skill_factory: SkillFactory
) -> None:
    skill_factory(root=tmp_path)

    errors = [finding.message for finding in check_skills(tmp_path)]
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

    errors = [finding.message for finding in check_skills(tmp_path)]
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

    assert any(
        "repetido" in finding.message for finding in check_skills(tmp_path, compare_copies=False)
    )


def test_check_skills_sem_skills(tmp_path: Path) -> None:
    assert any("Nenhuma skill" in finding.message for finding in check_skills(tmp_path))


def test_repositorio_atual_passa_nas_regras(project_root: Path) -> None:
    assert check_skills(project_root, compare_copies=False) == []


# ---------------------------------------------------------------------------
# Dispensas: um limite duro sem valvula de escape obriga a burlar o numero.
# A dispensa registra a decisao no frontmatter, com motivo, e aparece no
# relatorio como aviso — nunca desliga a regra em silencio.
# ---------------------------------------------------------------------------

MOTIVO = "O processo tem sete etapas verificaveis e quebrar perderia o estado entre elas."
DESCRICAO = "Resume CSV. Use quando pedirem conferência de planilha exportada."


def _com_dispensa(skill_dir: Path, regra: str, motivo: str = MOTIVO) -> None:
    """Acrescenta `metadata.waivers` ao frontmatter de uma skill existente."""
    skill_md = skill_dir / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")
    cabeca, _, corpo = content.partition("---\n")[2].partition("---\n")
    novo = f"---\n{cabeca}metadata:\n  waivers:\n    {regra}: {motivo}\n---\n{corpo}"
    skill_md.write_text(novo, encoding="utf-8")


def test_parse_waivers_le_o_bloco_aninhado() -> None:
    from scripts.check_skills import parse_waivers

    frontmatter = (
        "---\n"
        "name: x\n"
        "description: y\n"
        "metadata:\n"
        "  autor: time\n"
        "  waivers:\n"
        f'    body-lines: "{MOTIVO}"\n'
        "---\n"
        "# T\n"
    )

    assert parse_waivers(frontmatter) == {"body-lines": MOTIVO}


def test_dispensa_justificada_rebaixa_o_limite_a_aviso(skill_factory: SkillFactory) -> None:
    corpo = "# Longa\n\n" + "linha\n" * 600
    skill = skill_factory(body=corpo)
    assert any("máximo 500" in m for m in mensagens(skill)), "sem dispensa, reprova"

    _com_dispensa(skill, "body-lines")

    assert mensagens(skill) == [], "com dispensa justificada, não reprova"
    assert achados(skill)["body-lines"] == MOTIVO


def test_dispensa_sem_motivo_nao_vale(skill_factory: SkillFactory) -> None:
    skill = skill_factory(body="# Longa\n\n" + "linha\n" * 600)
    _com_dispensa(skill, "body-lines", motivo="porque sim")

    textos = mensagens(skill)
    assert any("máximo 500" in m for m in textos), "o limite continua reprovando"
    assert any("caracteres explicando o motivo" in m for m in textos)


def test_regra_essencial_nao_admite_dispensa(skill_factory: SkillFactory) -> None:
    # Dispensar divergência de nome seria desligar a verificação: o nome é o
    # que faz a skill ser encontrada.
    skill = skill_factory(name="resumir-csv")
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: outro-nome\n"
        f"description: {DESCRICAO}\n"
        "metadata:\n"
        "  waivers:\n"
        f"    name-divergente: {MOTIVO}\n"
        "---\n"
        "\n"
        "# T\n",
        encoding="utf-8",
    )

    textos = mensagens(skill)
    assert any("difere do nome da pasta" in m for m in textos)
    assert any("não admite dispensa" in m for m in textos)


def test_dispensa_ociosa_e_apontada(skill_factory: SkillFactory) -> None:
    skill = skill_factory()
    _com_dispensa(skill, "body-lines")

    assert any("sem a regra ter sido" in m for m in mensagens(skill))


def test_pasta_tests_e_prevista_e_nao_vira_orfa(skill_factory: SkillFactory) -> None:
    teste = '"""Teste da skill."""\n\n\ndef test_ok() -> None:\n    assert True\n'
    skill = skill_factory(files={"tests/test_resumo.py": teste})

    assert mensagens(skill) == []
