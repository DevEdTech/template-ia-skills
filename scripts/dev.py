#!/usr/bin/env python3
"""Runner de tarefas de desenvolvimento — cross-platform (Windows, macOS, Linux).

Equivalente ao `npm run <script>`, porém em Python puro (stdlib). Funciona
identicamente nos três sistemas operacionais: usa apenas subprocess e o mesmo
interpretador em execução — sem shell, sem Makefile obrigatório.

Uso:
    python scripts/dev.py <tarefa> [args...]
    python scripts/dev.py validate
    python scripts/dev.py new-skill --name resumir-planilha --with scripts

Se o `uv` estiver instalado, as ferramentas rodam via `uv run` (no ambiente do
projeto). Caso contrário, caem para `python -m <ferramenta>`, assumindo que as
dependências de dev já foram instaladas (veja o README).

Rode `python scripts/dev.py help` para ver todas as tarefas.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# uv disponível? Define como as ferramentas serão invocadas.
_HAS_UV = shutil.which("uv") is not None


def _tool(tool: str, *args: str) -> list[str]:
    """Monta o comando para rodar uma ferramenta Python (ruff, mypy, pytest...)."""
    if _HAS_UV:
        return ["uv", "run", tool, *args]
    return [sys.executable, "-m", tool, *args]


def _script(name: str, *args: str) -> list[str]:
    """Monta o comando para rodar outro script do próprio template."""
    return [sys.executable, str(SCRIPTS_DIR / name), *args]


def _run(cmd: Sequence[str]) -> int:
    """Executa um comando exibindo-o, retornando o código de saída."""
    print(f"$ {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, check=False)
    return result.returncode


def _run_all(commands: Sequence[Sequence[str]]) -> int:
    """Executa comandos em sequência; para no primeiro que falhar."""
    for cmd in commands:
        code = _run(cmd)
        if code != 0:
            print(f"\nFALHOU (codigo {code}): {' '.join(cmd)}", file=sys.stderr)
            return code
    return 0


def task_format(args: list[str]) -> int:
    return _run(_tool("ruff", "format", *args))


def task_format_check(args: list[str]) -> int:
    return _run(_tool("ruff", "format", "--check", *args))


def task_lint(args: list[str]) -> int:
    return _run(_tool("ruff", "check", *args))


def task_lint_fix(args: list[str]) -> int:
    return _run(_tool("ruff", "check", "--fix", *args))


def task_typecheck(args: list[str]) -> int:
    return _run(_tool("mypy", *args))


def task_test(args: list[str]) -> int:
    return _run(_tool("pytest", *args))


def task_test_cov(args: list[str]) -> int:
    return _run(_tool("pytest", "--cov", *args))


def task_sync_skills(args: list[str]) -> int:
    return _run(_script("sync_skills.py", *args))


def task_check_skills(args: list[str]) -> int:
    return _run(_script("check_skills.py", *args))


def task_check_evals(args: list[str]) -> int:
    return _run(_script("check_evals.py", *args))


def task_check_docs(args: list[str]) -> int:
    return _run(_script("check_docs.py", *args))


def task_new_skill(args: list[str]) -> int:
    return _run(_script("new_skill.py", *args))


def task_package(args: list[str]) -> int:
    return _run(_script("package_skills.py", *args))


def task_smoke_bundles(args: list[str]) -> int:
    return _run(_script("smoke_bundles.py", *args))


def task_eval_sheet(args: list[str]) -> int:
    """Imprime os prompts de avaliação para rodar contra um agente."""
    skill = ["--skill", args[0]] if args else []
    return _run(_script("check_evals.py", "--sheet", *skill))


def task_check_workflows(args: list[str]) -> int:
    """Valida os workflows do GitHub Actions com o actionlint.

    Um workflow inválido não falha: ele simplesmente não roda. Não adianta
    conferir isso dentro do próprio CI, porque um `ci.yml` quebrado não chega a
    iniciar — a verificação precisa acontecer antes do push, aqui.
    """
    workflows = PROJECT_ROOT / ".github" / "workflows"
    if not workflows.is_dir():
        print("Nenhum workflow para verificar.")
        return 0
    if not _HAS_UV:
        print(
            "A verificação de workflows requer o uv (https://docs.astral.sh/uv/).",
            file=sys.stderr,
        )
        return 1
    files = sorted(str(path) for path in workflows.glob("*.y*ml"))
    if not files:
        print("Nenhum workflow para verificar.")
        return 0
    # `uvx` roda a ferramenta de forma efêmera, sem entrar nas dependências.
    return _run(["uvx", "--from", "actionlint-py", "actionlint", *files, *args])


def task_audit(args: list[str]) -> int:
    """Confere as dependências bloqueadas contra o banco de vulnerabilidades.

    Fica fora do `validate` porque depende de rede: o portão local continua
    funcionando offline. O CI roda esta tarefa a cada PR e semanalmente.
    """
    if not _HAS_UV:
        print(
            "A auditoria requer o uv (https://docs.astral.sh/uv/).\n"
            "Sem uv, rode manualmente: pip-audit",
            file=sys.stderr,
        )
        return 1
    export = [
        "uv",
        "export",
        "--locked",
        "--all-groups",
        "--no-emit-project",
        "--format",
        "requirements-txt",
    ]
    print(f"$ {' '.join(export)}", flush=True)
    result = subprocess.run(export, cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return result.returncode
    with tempfile.TemporaryDirectory(prefix="skills-audit-") as directory:
        requirements = Path(directory) / "requirements.txt"
        requirements.write_text(result.stdout, encoding="utf-8")
        return _run(["uvx", "pip-audit", "--requirement", str(requirements), *args])


def task_validate(args: list[str]) -> int:
    """Porta única de qualidade: roda tudo, na ordem, parando no primeiro erro."""
    return _run_all(
        [
            # As cópias de skills são artefatos gerados e ignorados pelo Git:
            # regenera antes de conferir para que um clone novo já fique verde.
            _script("sync_skills.py"),
            _script("check_skills.py"),
            _script("check_evals.py"),
            _script("check_docs.py"),
            _tool("ruff", "format", "--check"),
            _tool("ruff", "check"),
            _tool("mypy"),
            # Com `--cov` o limite de cobertura do pyproject.toml passa a valer.
            _tool("pytest", "--cov"),
            _script("package_skills.py"),
            _script("smoke_bundles.py"),
        ]
    )


# Registro de tarefas: nome -> (função, descrição).
TASKS = {
    "format": (task_format, "Formata o código com Ruff."),
    "format-check": (task_format_check, "Confere a formatação sem alterar arquivos."),
    "lint": (task_lint, "Verifica problemas de código com Ruff."),
    "lint-fix": (task_lint_fix, "Corrige automaticamente o que o Ruff conseguir."),
    "typecheck": (task_typecheck, "Verifica os tipos com mypy (modo estrito)."),
    "test": (task_test, "Roda os testes com pytest."),
    "test-cov": (task_test_cov, "Roda os testes medindo cobertura."),
    "sync-skills": (task_sync_skills, "Sincroniza as skills para .claude e .agents."),
    "check-skills": (task_check_skills, "Valida metadados, estrutura e cópias das skills."),
    "check-evals": (task_check_evals, "Valida os cenários de avaliação das skills."),
    "check-docs": (task_check_docs, "Valida links, tarefas e catálogo da documentação."),
    "new-skill": (task_new_skill, "Cria o esqueleto de uma skill nova."),
    "package": (task_package, "Empacota cada skill em um .zip distribuível."),
    "smoke-bundles": (task_smoke_bundles, "Testa os pacotes fora do repositório."),
    "eval-sheet": (task_eval_sheet, "Imprime a folha de avaliação para rodar com um agente."),
    "check-workflows": (task_check_workflows, "Valida os workflows do GitHub Actions."),
    "audit": (task_audit, "Audita as dependências em busca de vulnerabilidades."),
    "validate": (task_validate, "Roda skills, docs, qualidade, testes e pacotes."),
}


def print_help() -> None:
    print("Tarefas disponiveis (python scripts/dev.py <tarefa>):\n")
    width = max(len(name) for name in TASKS)
    for name, (_func, desc) in TASKS.items():
        print(f"  {name.ljust(width)}  {desc}")
    print(
        f"\nRunner: {'uv run' if _HAS_UV else 'python -m'} (uv "
        f"{'detectado' if _HAS_UV else 'nao encontrado'})."
    )


def main(argv: list[str] | None = None) -> int:
    try:
        args = list(sys.argv[1:] if argv is None else argv)
        if not args or args[0] in {"help", "-h", "--help"}:
            print_help()
            return 0

        task_name, *rest = args
        entry = TASKS.get(task_name)
        if entry is None:
            print(f"Tarefa desconhecida: {task_name!r}\n", file=sys.stderr)
            print_help()
            return 2

        func, _desc = entry
        return func(rest)
    except KeyboardInterrupt:
        print("\nCancelado pelo usuário.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
