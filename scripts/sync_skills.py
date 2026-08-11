#!/usr/bin/env python3
"""Sincroniza as skills canônicas de `skills/` para as cópias geradas.

As cópias vivem em `.claude/skills` e `.agents/skills`: é de lá que o agente
carrega as skills durante o desenvolvimento do próprio template. NÃO edite as
cópias manualmente — elas são recriadas por este script.

Uso: `python scripts/dev.py sync-skills` (ou `python scripts/sync_skills.py`).

Cross-platform (Windows, macOS, Linux): usa apenas a stdlib (pathlib, shutil).
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIRNAME = "skills"
COPY_DIRS = (".claude/skills", ".agents/skills")
# Bytecode gerado pelos testes não é conteúdo da skill.
IGNORED = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")


def list_skill_dirs(directory: Path) -> list[str]:
    """Lista as pastas de skill (arquivos soltos na raiz são ignorados)."""
    if not directory.is_dir():
        return []
    return sorted(entry.name for entry in directory.iterdir() if entry.is_dir())


def sync_skills(root: Path = PROJECT_ROOT) -> list[str]:
    """Recria as cópias das skills e devolve os nomes sincronizados."""
    source_root = root / SOURCE_DIRNAME
    skills = list_skill_dirs(source_root)
    if not skills:
        print(f'Nenhuma skill encontrada em "{source_root}". Nada a sincronizar.')
        return []

    for relative in COPY_DIRS:
        dest_root = root / relative
        # Remove a pasta antiga inteira e recria do zero: assim uma skill
        # renomeada não deixa a versão anterior para trás.
        if dest_root.exists():
            shutil.rmtree(dest_root)
        dest_root.mkdir(parents=True, exist_ok=True)
        for skill in skills:
            shutil.copytree(source_root / skill, dest_root / skill, ignore=IGNORED)
        print(f'Sincronizadas {len(skills)} skill(s) para "{relative}":')
        for skill in skills:
            print(f"  - {skill}")

    print("\nSincronização concluída com sucesso.")
    return skills


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincroniza as skills para as cópias geradas.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args()
    sync_skills(args.root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
