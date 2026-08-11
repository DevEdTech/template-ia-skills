#!/usr/bin/env python3
"""Extrai cada pacote gerado e prova que a skill funciona sozinha.

O que o `check-skills` verifica no repositório, este script verifica no
artefato: o zip é extraído em um diretório temporário e a skill é validada de
novo, longe do projeto. Depois, cada script é executado com `--help` em modo
isolado (`python -I`), sem acesso a variáveis de ambiente do usuário nem ao
diretório do repositório — se o script depender de algo que só existe aqui, ele
falha agora, e não na máquina de quem instalou a skill.

Scripts de skills com `requirements.txt` são validados, mas não executados: as
dependências declaradas não estão instaladas neste ambiente.

Uso: `python scripts/dev.py smoke-bundles`.

Cross-platform (Windows, macOS, Linux): usa apenas a stdlib.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.check_skills import validate_skill  # noqa: E402

DIST_DIRNAME = "dist"
HELP_TIMEOUT_SECONDS = 60


def _run_help(script: Path, workdir: Path) -> str | None:
    """Executa `python -I <script> --help`; devolve a mensagem de erro, se houver."""
    result = subprocess.run(
        [sys.executable, "-I", str(script), "--help"],
        cwd=workdir,
        capture_output=True,
        text=True,
        timeout=HELP_TIMEOUT_SECONDS,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()
        tail = detail[-1] if detail else f"código {result.returncode}"
        return f"`{script.name} --help` falhou fora do repositório: {tail}"
    return None


def smoke_bundles(root: Path = PROJECT_ROOT) -> list[str]:
    """Valida todos os pacotes de `dist/` e devolve a lista de problemas."""
    dist_dir = root / DIST_DIRNAME
    bundles = sorted(dist_dir.glob("*.zip")) if dist_dir.is_dir() else []
    if not bundles:
        return [f'Nenhum pacote em "{dist_dir}". Rode "python scripts/dev.py package" antes.']

    errors: list[str] = []
    for bundle in bundles:
        with tempfile.TemporaryDirectory(prefix="skill-smoke-") as directory:
            workdir = Path(directory)
            with zipfile.ZipFile(bundle) as archive:
                archive.extractall(workdir)
            extracted = workdir / bundle.stem
            if not (extracted / "SKILL.md").is_file():
                errors.append(f"{bundle.name}: o pacote não contém `{bundle.stem}/SKILL.md`.")
                continue

            errors.extend(f"{bundle.name}: {error}" for error in validate_skill(extracted))

            if (extracted / "requirements.txt").is_file():
                continue
            for script in sorted((extracted / "scripts").glob("*.py")):
                failure = _run_help(script, workdir)
                if failure:
                    errors.append(f"{bundle.name}: {failure}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Testa os pacotes gerados fora do repositório.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args()
    root = args.root.resolve()

    errors = smoke_bundles(root)
    if errors:
        print("Smoke dos pacotes FALHOU:\n", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    bundles = sorted((root / DIST_DIRNAME).glob("*.zip"))
    print(f"Smoke dos pacotes OK: {len(bundles)} pacote(s) válidos fora do repositório.")
    for bundle in bundles:
        print(f"  - {bundle.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
