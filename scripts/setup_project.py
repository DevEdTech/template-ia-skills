#!/usr/bin/env python3
"""Personaliza o template para o seu projeto de skills.

Troca o nome do projeto, a descrição e o repositório nos arquivos versionados,
opcionalmente remove a skill de demonstração e zera o `tasks.md`. Registra o
resultado em `.template-state.json`.

A operação é transacional: os arquivos afetados são lidos antes, e qualquer
falha no meio do caminho restaura o estado anterior. Rodar duas vezes com os
mesmos valores não muda nada além do que já mudou (idempotente).

Uso:
    python scripts/setup_project.py --dry-run
    python scripts/setup_project.py --name="skills-financeiro" \\
        --display-name="Skills Financeiro" --description="Skills do time." \\
        --repository="https://github.com/org/skills-financeiro" --remove-example

Cross-platform (Windows, macOS, Linux): usa apenas a stdlib.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ".template-state.json"
EXAMPLE_SKILL = "summarize-csv"
TEMPLATE_NAME = "skills-project-template"
TEMPLATE_DISPLAY = "Skills Project Template"
TEMPLATE_REPOSITORY = "https://github.com/DevEdTech/template-ia-skills"
TEXT_FILES = ("pyproject.toml", "README.md", "docs/packaging.md", STATE_FILE)
RESET_TASKS = "# Tarefas\n\nNenhuma tarefa em andamento.\n"


def slugify(value: str) -> str:
    """Converte um nome livre em um identificador de projeto."""
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")
    if not slug or not slug[0].isalpha():
        raise ValueError("Informe um nome de projeto começando por letra.")
    return slug


def read_state(root: Path) -> dict[str, object]:
    return dict(json.loads((root / STATE_FILE).read_text(encoding="utf-8")))


def _replacements(state: dict[str, object], plan: dict[str, str]) -> list[tuple[str, str]]:
    """Pares (de, para) aplicados a todos os arquivos de texto."""
    pairs = [
        (str(state["projectName"]), plan["name"]),
        (str(state["displayName"]), plan["display_name"]),
        (str(state["repository"]), plan["repository"]),
        (str(state["description"]), plan["description"]),
    ]
    return [(old, new) for old, new in pairs if old and new and old != new]


def setup_project(
    root: Path,
    *,
    name: str | None = None,
    display_name: str | None = None,
    description: str | None = None,
    repository: str | None = None,
    remove_example: bool = False,
    reset_tasks: bool = False,
    dry_run: bool = False,
) -> list[str]:
    """Aplica a personalização e devolve o resumo das ações."""
    state = read_state(root)
    plan = {
        "name": slugify(name) if name else str(state["projectName"]),
        "display_name": display_name or str(state["displayName"]),
        "description": description or str(state["description"]),
        "repository": repository or str(state["repository"]),
    }
    pairs = _replacements(state, plan)
    example_dir = root / "skills" / EXAMPLE_SKILL
    removes_example = remove_example and example_dir.is_dir()

    actions: list[str] = []
    for old, new in pairs:
        actions.append(f'substituir "{old}" por "{new}"')
    if removes_example:
        actions.append(f"remover a skill de demonstração ({EXAMPLE_SKILL})")
    if reset_tasks:
        actions.append("zerar tasks.md")
    if not actions:
        actions.append("nada a fazer: o projeto já está personalizado")
    if dry_run:
        return actions

    targets = [root / relative for relative in TEXT_FILES if (root / relative).is_file()]
    backup: dict[Path, str] = {path: path.read_text(encoding="utf-8") for path in targets}
    tasks_file = root / "tasks.md"
    if reset_tasks and tasks_file.is_file():
        backup[tasks_file] = tasks_file.read_text(encoding="utf-8")
    quarantine = root / f".{EXAMPLE_SKILL}.bak" if removes_example else None

    try:
        for path in targets:
            content = backup[path]
            for old, new in pairs:
                content = content.replace(old, new)
            path.write_text(content, encoding="utf-8")

        state.update(
            {
                "projectName": plan["name"],
                "displayName": plan["display_name"],
                "description": plan["description"],
                "repository": plan["repository"],
                "exampleRemoved": bool(state["exampleRemoved"]) or removes_example,
            }
        )
        (root / STATE_FILE).write_text(
            json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        if removes_example and quarantine is not None:
            shutil.move(str(example_dir), str(quarantine))
            (root / "evals" / f"{EXAMPLE_SKILL}.json").unlink(missing_ok=True)
            for test in (root / "tests" / "skills").glob("test_summarize_csv.py"):
                test.unlink()
        if reset_tasks:
            tasks_file.write_text(RESET_TASKS, encoding="utf-8")
    except Exception:
        for path, content in backup.items():
            path.write_text(content, encoding="utf-8")
        if quarantine is not None and quarantine.is_dir():
            shutil.move(str(quarantine), str(example_dir))
        raise

    if quarantine is not None and quarantine.is_dir():
        shutil.rmtree(quarantine)
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description="Personaliza o template para o seu projeto.")
    parser.add_argument("--name", help="Identificador do projeto (kebab-case).")
    parser.add_argument("--display-name", help="Nome exibido na documentação.")
    parser.add_argument("--description", help="Descrição curta do conjunto de skills.")
    parser.add_argument("--repository", help="URL do repositório.")
    parser.add_argument("--remove-example", action="store_true", help="Remove a skill de exemplo.")
    parser.add_argument("--reset-tasks", action="store_true", help="Zera o tasks.md.")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o plano sem aplicar.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args()

    try:
        actions = setup_project(
            args.root.resolve(),
            name=args.name,
            display_name=args.display_name,
            description=args.description,
            repository=args.repository,
            remove_example=args.remove_example,
            reset_tasks=args.reset_tasks,
            dry_run=args.dry_run,
        )
    except (ValueError, KeyError) as error:
        print(f"Setup cancelado: {error}", file=sys.stderr)
        return 1

    print("Plano do setup:" if args.dry_run else "Setup aplicado:")
    for action in actions:
        print(f"  - {action}")
    if not args.dry_run:
        print("\nPróximo passo: `python scripts/dev.py validate`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
