#!/usr/bin/env python3
"""Confere se o `uv.lock` corresponde ao `pyproject.toml`.

Por que isto existe: o CI instala com `uv sync --locked`, que recusa lockfile
desatualizado. Quem mexe no `pyproject.toml` e valida pelo ambiente ja criado
(`.venv` montado com pip, por exemplo) nunca consulta o lockfile — e descobre a
divergencia so no CI, varios minutos depois, em todos os jobs da matriz ao
mesmo tempo.

Sem `uv` instalado nao da para conferir. Nesse caso o script avisa e sai com
zero: o `validate` nao deve reprovar por uma ferramenta ausente, e o perfil ja
decide o peso do aviso.

A mesma distincao vale quando o `uv` existe mas nao consegue rodar (um
interpretador quebrado no PATH da maquina, por exemplo). "Nao consegui
conferir" nao e "esta divergente": reprovar nos dois casos daria uma mensagem
que aponta a causa errada. So a divergencia de fato reprova.

Uso: `python scripts/dev.py check-lockfile`.

Cross-platform (Windows, macOS, Linux): usa apenas a stdlib.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def find_uv(root: Path = PROJECT_ROOT) -> str | None:
    """Localiza o `uv`: no PATH ou no ambiente virtual do projeto."""
    found = shutil.which("uv")
    if found:
        return found
    for candidate in (root / ".venv" / "bin" / "uv", root / ".venv" / "Scripts" / "uv.exe"):
        if candidate.is_file():
            return str(candidate)
    return None


#: Marca que o `uv` imprime quando o lockfile de fato divergiu. Qualquer outra
#: falha e "nao consegui conferir", nao "esta divergente".
DIVERGENCE_MARKER = "needs to be updated"


def project_interpreter(root: Path) -> Path | None:
    """O interpretador do ambiente do projeto, quando existir."""
    for candidate in (root / ".venv" / "bin" / "python", root / ".venv" / "Scripts" / "python.exe"):
        if candidate.is_file():
            return candidate
    return None


def check_lockfile(root: Path = PROJECT_ROOT) -> tuple[int, str]:
    """Retorna `(codigo, mensagem)`; codigo diferente de zero so em divergencia."""
    lockfile = root / "uv.lock"
    if not lockfile.is_file():
        return 1, "uv.lock ausente: rode `uv lock` e versione o arquivo."

    uv = find_uv(root)
    if uv is None:
        return 0, (
            "uv nao encontrado: nao foi possivel conferir o uv.lock. "
            "O CI confere com `uv sync --locked`; instale o uv para pegar "
            "a divergencia antes de empurrar."
        )

    environment = dict(os.environ)
    # Aponta o interpretador do projeto: sem isso o uv varre o PATH e um
    # interpretador quebrado na maquina derruba a verificacao por um motivo
    # que nada tem a ver com o lockfile.
    interpreter = project_interpreter(root)
    if interpreter is not None:
        environment.setdefault("UV_PYTHON", str(interpreter))

    result = subprocess.run(
        [uv, "lock", "--check"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )
    if result.returncode == 0:
        return 0, "uv.lock em dia com o pyproject.toml."

    saida = (result.stderr or result.stdout).strip()
    if DIVERGENCE_MARKER in saida:
        return 1, (
            "uv.lock desatualizado em relacao ao pyproject.toml.\n"
            "Rode `uv lock` e versione o arquivo: o CI instala com "
            "`uv sync --locked` e recusa lockfile divergente."
        )
    return 0, (
        "Nao foi possivel conferir o uv.lock (o uv falhou por outro motivo).\n"
        "O CI confere com `uv sync --locked`.\n"
        f"{saida}"
    )


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da CLI."""
    parser = argparse.ArgumentParser(description="Confere o uv.lock contra o pyproject.toml.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args(argv)

    code, message = check_lockfile(args.root.resolve())
    print(message, file=sys.stderr if code else sys.stdout)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
