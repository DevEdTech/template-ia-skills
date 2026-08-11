#!/usr/bin/env python3
"""Cria o esqueleto de uma skill nova, já válido para o `validate`.

Gera a pasta `skills/<nome>/` com o `SKILL.md` mínimo, as partes opcionais
pedidas (`scripts`, `assets`, `reference`) e o arquivo de avaliação
`evals/<nome>.json`. O conteúdo é um ponto de partida: quem escreve a skill
substitui os textos-marcador. O gerador não registra nada no catálogo — isso é
tarefa da skill `document-skills`.

Uso:
    python scripts/dev.py new-skill --name resumir-planilha
    python scripts/dev.py new-skill --name resumir-planilha --with scripts,assets --dry-run

Cross-platform (Windows, macOS, Linux): usa apenas a stdlib.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
import unicodedata
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PARTS = ("scripts", "assets", "reference")


def slugify(value: str) -> str:
    """Converte um nome livre em kebab-case ASCII."""
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")
    if not slug or not slug[0].isalpha():
        raise ValueError("Informe um nome de skill começando por letra (ex.: resumir-planilha).")
    if len(slug.split("-")) > 5:
        raise ValueError("Use no máximo 5 termos no nome da skill (verbo + objeto).")
    return slug


def _skill_md(slug: str, parts: set[str]) -> str:
    title = slug.replace("-", " ").capitalize()
    lines = [
        "---",
        f"name: {slug}",
        (
            "description: Descreva em uma linha o que a skill entrega. Use quando "
            "[situação observável que dispara a skill]; não use quando [limite]."
        ),
        "---",
        "",
        f"# {title}",
        "",
        "## Objetivo",
        "",
        "Descreva o resultado que a skill produz, em uma ou duas frases.",
        "",
        "## Quando usar",
        "",
        "- Situação concreta 1.",
        "- Situação concreta 2.",
        "",
        "## Quando não usar",
        "",
        "- Situação vizinha que pertence a outra skill.",
        "",
        "## Processo",
        "",
        "1. Reúna as entradas necessárias e confirme o que estiver ambíguo.",
    ]
    step = 2
    if "scripts" in parts:
        script = slug.replace("-", "_")
        lines.append(
            f"{step}. Execute `python scripts/{script}.py --help` e rode o passo determinístico "
            "com o script, em vez de fazer o trabalho manualmente."
        )
        step += 1
    if "assets" in parts:
        lines.append(
            f"{step}. Preencha o modelo [assets/output-template.md](assets/output-template.md)."
        )
        step += 1
    if "reference" in parts:
        lines.append(
            f"{step}. Consulte [reference/details.md](reference/details.md) somente quando o "
            "caso exigir as regras detalhadas."
        )
        step += 1
    lines.extend(
        [
            f"{step}. Verifique o resultado contra os critérios abaixo antes de responder.",
            "",
            "## Resultado esperado",
            "",
            "- Artefato produzido e onde ele fica.",
            "- Como conferir que está correto.",
            "",
        ]
    )
    return "\n".join(lines)


def _script(slug: str) -> str:
    title = slug.replace("-", " ")
    return (
        f'"""Passo determinístico da skill {slug}: {title}.\n\n'
        "Só use a stdlib: a skill precisa rodar em qualquer ambiente onde o agente\n"
        "estiver, sem instalação prévia.\n"
        '"""\n\n'
        "from __future__ import annotations\n\n"
        "import argparse\n\n\n"
        "def run(value: str) -> str:\n"
        '    """Implemente aqui a transformação determinística."""\n'
        "    return value.strip()\n\n\n"
        "def main() -> int:\n"
        "    parser = argparse.ArgumentParser(description=__doc__)\n"
        '    parser.add_argument("--value", required=True, help="Entrada a processar.")\n'
        "    args = parser.parse_args()\n"
        "    print(run(args.value))\n"
        "    return 0\n\n\n"
        'if __name__ == "__main__":\n'
        "    raise SystemExit(main())\n"
    )


def _eval_file(slug: str) -> str:
    data = {
        "skill": slug,
        "trigger": [
            {"prompt": "Pedido típico, sem citar a skill pelo nome.", "should_trigger": True},
            {"prompt": "Outro pedido típico, com vocabulário diferente.", "should_trigger": True},
            {"prompt": "Pedido vizinho que pertence a outra skill.", "should_trigger": False},
        ],
        "execution": [
            {
                "prompt": "Pedido completo, com os dados necessários.",
                "expect": [
                    "Artefato esperado foi produzido no caminho combinado.",
                    "O agente seguiu o processo do SKILL.md sem pular etapas.",
                ],
                "red_flags": [
                    "Reimplementou à mão o que o script da skill já faz.",
                ],
            }
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def create_skill(root: Path, raw_name: str, parts: set[str], dry_run: bool = False) -> list[Path]:
    """Cria a skill e devolve os arquivos planejados ou criados."""
    slug = slugify(raw_name)
    unknown = parts - set(PARTS)
    if unknown:
        raise ValueError(f"Partes desconhecidas: {', '.join(sorted(unknown))}.")

    skill_dir = root / "skills" / slug
    eval_file = root / "evals" / f"{slug}.json"
    if skill_dir.exists():
        raise FileExistsError(f'A skill "{slug}" já existe.')
    if eval_file.exists():
        raise FileExistsError(f'O arquivo de avaliação "{eval_file.name}" já existe.')

    files: dict[str, str] = {"SKILL.md": _skill_md(slug, parts)}
    if "scripts" in parts:
        files[f"scripts/{slug.replace('-', '_')}.py"] = _script(slug)
    if "assets" in parts:
        files["assets/output-template.md"] = (
            f"<!-- Modelo de saída da skill {slug}. Substitua os campos entre colchetes. -->\n\n"
            "# [Título]\n\n## Resumo\n\n[Uma frase]\n\n## Detalhes\n\n- [Item]\n"
        )
    if "reference" in parts:
        files["reference/details.md"] = (
            f"# Detalhes de {slug}\n\n"
            "Regras, tabelas e casos de exceção que não cabem no SKILL.md.\n"
            "Este arquivo só é lido quando o processo apontar para ele.\n"
        )

    planned = [skill_dir / name for name in sorted(files)] + [eval_file]
    if dry_run:
        return planned

    skill_dir.parent.mkdir(parents=True, exist_ok=True)
    eval_file.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f"{slug}-", dir=skill_dir.parent))
    try:
        for relative, content in files.items():
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
        staging.rename(skill_dir)
        eval_file.write_text(_eval_file(slug), encoding="utf-8")
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        shutil.rmtree(skill_dir, ignore_errors=True)
        eval_file.unlink(missing_ok=True)
        raise
    return planned


def main() -> int:
    parser = argparse.ArgumentParser(description="Cria o esqueleto de uma skill nova.")
    parser.add_argument("--name", required=True, help="Nome da skill (verbo + objeto).")
    parser.add_argument(
        "--with",
        dest="parts",
        default="",
        help=f"Partes opcionais separadas por vírgula: {', '.join(PARTS)}.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args()

    parts = {part.strip() for part in args.parts.split(",") if part.strip()}
    root = args.root.resolve()
    files = create_skill(root, args.name, parts, args.dry_run)
    print("Arquivos planejados:" if args.dry_run else "Skill criada:")
    for file in files:
        print(f"  - {file.relative_to(root).as_posix()}")
    if not args.dry_run:
        print("\nPróximo passo: escreva a descrição real e rode `python scripts/dev.py validate`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
