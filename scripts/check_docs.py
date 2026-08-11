#!/usr/bin/env python3
"""Valida links, comandos e o catálogo de skills da documentação."""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from urllib.parse import unquote

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG = "docs/agents.md"
CATALOG_ENTRY = re.compile(r"^- \*\*([a-z0-9-]+)\*\* —", flags=re.MULTILINE)


def _task_names(root: Path) -> set[str]:
    """Lê o registro TASKS do `dev.py` sem importar o módulo."""
    dev_script = root / "scripts" / "dev.py"
    if not dev_script.exists():
        dev_script = PROJECT_ROOT / "scripts" / "dev.py"
    tree = ast.parse(dev_script.read_text(encoding="utf-8"))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "TASKS" for target in node.targets
            )
            and isinstance(node.value, ast.Dict)
        ):
            return {
                key.value
                for key in node.value.keys
                if isinstance(key, ast.Constant) and isinstance(key.value, str)
            }
    raise ValueError("Registro TASKS não encontrado em scripts/dev.py.")


def _local_target(root: Path, file: Path, raw_link: str) -> Path | None:
    link = raw_link.strip().strip("<>")
    if not link or link.startswith("#") or re.match(r"^(?:https?:|mailto:|tel:)", link):
        return None
    path = unquote(re.split(r"[?#]", link, maxsplit=1)[0])
    return root / path.lstrip("/") if path.startswith("/") else file.parent / path


def _skill_names(root: Path) -> list[str]:
    directory = root / "skills"
    if not directory.is_dir():
        return []
    return sorted(entry.name for entry in directory.iterdir() if entry.is_dir())


def check_docs(root: Path = PROJECT_ROOT) -> list[str]:
    """Confere links locais, tarefas citadas e o catálogo de skills."""
    errors: list[str] = []
    tasks = _task_names(root)

    files = [root / "README.md", root / "AGENTS.md", *(root / "docs").rglob("*.md")]
    for file in files:
        if not file.exists():
            continue
        content = file.read_text(encoding="utf-8")
        label = file.relative_to(root).as_posix()
        for raw_link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content):
            target = _local_target(root, file, raw_link)
            if target is not None and not target.exists():
                errors.append(f'{label}: link inexistente "{raw_link}".')
        for task in re.findall(r"python scripts/dev\.py ([a-zA-Z0-9_-]+)", content):
            if task not in tasks:
                errors.append(f'{label}: tarefa local inexistente "{task}".')

    catalog_file = root / CATALOG
    if catalog_file.exists():
        listed = set(CATALOG_ENTRY.findall(catalog_file.read_text(encoding="utf-8")))
        available = set(_skill_names(root))
        for skill in sorted(listed - available):
            errors.append(f'{CATALOG}: skill inexistente "{skill}".')
        for skill in sorted(available - listed):
            errors.append(f'{CATALOG}: skill "{skill}" não está no catálogo.')

    state_file = root / ".template-state.json"
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))
        if state["projectName"] != "skills-project-template":
            for stale_file in ("pyproject.toml", "README.md"):
                path = root / stale_file
                if path.exists() and "skills-project-template" in path.read_text(encoding="utf-8"):
                    errors.append(
                        f"{stale_file}: identificador original ainda presente após o setup."
                    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args()
    errors = check_docs(args.root.resolve())
    if errors:
        print("Validação da documentação FALHOU:\n")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Validação da documentação OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
