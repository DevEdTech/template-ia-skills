#!/usr/bin/env python3
"""Orquestrador do `python scripts/dev.py validate`.

Antes era uma lista fixa de comandos: tudo ou nada, sempre tudo bloqueante, sem
jeito de rodar um pedaco. Agora as suites vem do catalogo em
`project_config.py`, o perfil do projeto decide o que bloqueia e as flags
decidem o que roda.

    dev.py validate                    tudo que o perfil manda
    dev.py validate --list             o que existe, o que bloqueia e por que
    dev.py validate --quick            so as suites rapidas
    dev.py validate --only lint test   so estas
    dev.py validate --skip package     tudo menos estas
    dev.py validate --changed          so o que os arquivos alterados afetam
    dev.py validate --changed main     idem, comparando com outra ref
    dev.py validate --skill resumir-csv
    dev.py validate --strict           aviso passa a falhar
    dev.py validate --no-bail          roda tudo antes de falhar

A unidade de escopo aqui e a **skill**, nao o modulo. Isso nao e uma
simplificacao: skill nao importa skill, por decisao de arquitetura
(ADR 0003), entao nao existe fechamento transitivo a calcular. Mudar uma skill
afeta aquela skill, o eval dela e o pacote dela — e nada mais.

Cross-platform (Windows, macOS, Linux): usa apenas a stdlib.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import replace
from pathlib import Path
from typing import cast

from scripts.project_config import (
    EXTERNAL_SUITES,
    SUITES,
    ProjectConfig,
    Suite,
    Tier,
    read_project_config,
    resolve_suites,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CONFIG_FILES = {
    "pyproject.toml",
    "uv.lock",
    "requirements-dev.txt",
    ".python-version",
    ".template-state.json",
}
DOC_FILES = {"README.md", "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md", "SECURITY.md"}

#: Construtores de comando e executor injetados pelo `dev.py`, que sabe se as
#: ferramentas rodam via `uv run` ou `python -m`.
CommandBuilders = dict[str, Callable[..., object]]


def _classify(paths: Sequence[str]) -> set[str]:
    """Classifica os caminhos nos gatilhos declarados pelo catalogo."""
    triggers: set[str] = set()
    if paths:
        triggers.add("any")
    for path in paths:
        if path in CONFIG_FILES:
            triggers.add("config")
        if path.startswith("skills/") or path.startswith((".claude/", ".agents/")):
            triggers.add("skills")
        if path.startswith("evals/"):
            triggers.add("evals")
        if path.startswith("docs/") or path in DOC_FILES:
            triggers.add("docs")
        if path.startswith(("scripts/", "tests/")):
            triggers.add("scripts")
    return triggers


def skills_in(paths: Sequence[str]) -> list[str]:
    """As skills citadas pelos caminhos, vindas de `skills/` ou de `evals/`."""
    nomes: set[str] = set()
    for path in paths:
        parts = Path(path).parts
        if len(parts) >= 2 and parts[0] == "skills":
            nomes.add(parts[1])
        elif len(parts) == 2 and parts[0] == "evals" and parts[1].endswith(".json"):
            nomes.add(parts[1].removesuffix(".json"))
    return sorted(nomes)


def covering_tests(skills: Sequence[str], root: Path = PROJECT_ROOT) -> list[str]:
    """Arquivos de teste que cobrem as skills informadas, quando existirem.

    O nome evita o prefixo `test` de proposito: o pytest coleta por `test*` e
    tomaria a funcao por um caso de teste.
    """
    encontrados: list[str] = []
    for skill in skills:
        candidato = root / "tests" / "skills" / f"test_{skill.replace('-', '_')}.py"
        if candidato.is_file():
            encontrados.append(candidato.relative_to(root).as_posix())
    return encontrados


def _changed_paths(base: str | None) -> list[str]:
    """Arquivos alterados: indice, working tree e, com base, o diff da branch."""
    commands = [
        ["git", "diff", "--name-only", "--diff-filter=ACMR", "HEAD"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ]
    if base:
        commands.insert(0, ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{base}...HEAD"])

    paths: set[str] = set()
    for command in commands:
        result = subprocess.run(
            command, cwd=PROJECT_ROOT, capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            continue
        paths.update(line.strip() for line in result.stdout.splitlines() if line.strip())
    return sorted(paths)


def _run(command: Sequence[str], dry_run: bool, runner: Callable[[Sequence[str]], int]) -> int:
    """Executa pelo runner injetado.

    A execucao fica com quem chamou (`dev.py`), nao aqui: com um unico ponto de
    execucao, o `--dry-run` e os testes do runner continuam valendo para o
    `validate` como para qualquer outra tarefa.
    """
    if dry_run:
        print(f"\n$ {' '.join(command)}", flush=True)
        return 0
    return runner(command)


def _commands_for(
    suite: Suite,
    config: ProjectConfig,
    build: CommandBuilders,
    *,
    scoped: bool,
    quick: bool,
    skills: Sequence[str],
    target_paths: Sequence[str],
) -> list[list[str]]:
    """Monta os comandos de uma suite, conforme perfil e escopo da execucao."""
    tool = cast("Callable[..., list[str]]", build["tool"])
    script = cast("Callable[..., list[str]]", build["script"])
    estrito = ["--strict"] if config.strict_findings else []

    if suite.name == "sync-skills":
        return [script("sync_skills.py")]
    if suite.name == "check-skills":
        # A verificacao e do repositorio inteiro: ela compara as copias e os
        # nomes de script entre skills, o que exige ver todas.
        return [script("check_skills.py", *estrito)]
    if suite.name == "check-evals":
        return [script("check_evals.py")]
    if suite.name == "check-docs":
        return [script("check_docs.py")]
    if suite.name == "format-check":
        alvos = [p for p in target_paths if p.endswith(".py")] if scoped else []
        return [tool("ruff", "format", "--check", *alvos)] if alvos or not scoped else []
    if suite.name == "lint":
        alvos = [p for p in target_paths if p.endswith(".py")] if scoped else []
        return [tool("ruff", "check", *alvos)] if alvos or not scoped else []
    if suite.name == "typecheck":
        return [tool("mypy")]
    if suite.name == "test":
        if scoped:
            alvos = covering_tests(skills)
            alvos += [p for p in target_paths if p.startswith("tests/") and p.endswith(".py")]
            # Sem `--cov`: o limite e global e um subconjunto nunca o alcanca.
            return [tool("pytest", *sorted(set(alvos)))] if alvos else []
        if quick or config.coverage is None:
            return [tool("pytest")]
        return [tool("pytest", "--cov", f"--cov-fail-under={config.coverage}")]
    if suite.name == "package":
        if scoped and skills:
            return [script("package_skills.py", "--skill", skill) for skill in skills]
        return [script("package_skills.py")]
    if suite.name == "smoke-bundles":
        return [script("smoke_bundles.py")]
    raise AssertionError(f"suite sem comando: {suite.name}")


def _print_list(config: ProjectConfig, resolved: list[tuple[Suite, Tier, str | None]]) -> None:
    width = max(len(suite.name) for suite, _, _ in resolved)
    print(f"\nPerfil: {config.profile}")
    ativas = ", ".join(name for name, on in config.capabilities.items() if on) or "nenhuma"
    print(f"Capacidades: {ativas}")
    print(
        f"Cobertura: minimo de {config.coverage}%"
        if config.coverage is not None
        else "Cobertura: nao aplicada neste perfil"
    )
    print(
        "Achados de skill: aviso reprova"
        if config.strict_findings
        else "Achados de skill: heuristica e dispensa apenas avisam"
    )
    print("\nSuites do validate:")
    rotulos: dict[str, str] = {"blocking": "bloqueia", "advisory": "avisa", "off": "desligada"}
    for suite, tier, reason in resolved:
        sufixo = f" ({reason})" if reason else ""
        print(f"  {suite.name.ljust(width)}  {rotulos[tier]}{sufixo}")
    print("\nFora do validate (gate proprio):")
    for name, label in EXTERNAL_SUITES.items():
        print(f"  {name}  {label}")


def run_validate(args: list[str], build: CommandBuilders) -> int:
    """Executa o `validate` com as flags informadas."""
    parser = argparse.ArgumentParser(prog="dev.py validate", add_help=True)
    parser.add_argument("--list", action="store_true", help="mostra as suites e o que bloqueia")
    parser.add_argument("--quick", action="store_true", help="so as suites rapidas")
    parser.add_argument("--only", nargs="+", default=[], metavar="SUITE")
    parser.add_argument("--skip", nargs="+", default=[], metavar="SUITE")
    parser.add_argument("--changed", nargs="?", const="", default=None, metavar="BASE")
    parser.add_argument("--skill", nargs="+", default=None, metavar="NOME")
    parser.add_argument("--strict", action="store_true", help="aviso passa a falhar")
    parser.add_argument("--no-bail", action="store_true", help="roda tudo antes de falhar")
    parser.add_argument("--dry-run", action="store_true", help="mostra o plano sem executar")
    options = parser.parse_args(args)

    runner = cast("Callable[[Sequence[str]], int]", build["run"])
    config = read_project_config()
    if options.strict:
        config = replace(config, profile="rigoroso")
    resolved = resolve_suites(config)

    if options.list:
        _print_list(config, resolved)
        return 0

    conhecidas = {suite.name for suite in SUITES}
    for name in [*options.only, *options.skip]:
        if name not in conhecidas:
            print(
                f'Suite desconhecida: "{name}". Use --list para ver as disponiveis.',
                file=sys.stderr,
            )
            return 2

    scoped = options.changed is not None or options.skill is not None
    target_paths: list[str] = []
    skills: list[str] = []
    triggers: set[str] | None = None

    if scoped:
        if options.skill is not None:
            existentes = {
                entry.name for entry in (PROJECT_ROOT / "skills").iterdir() if entry.is_dir()
            }
            desconhecidas = [s for s in options.skill if s not in existentes]
            if desconhecidas:
                print(f"Skill inexistente: {', '.join(desconhecidas)}.", file=sys.stderr)
                return 2
            skills = sorted(options.skill)
            # Os arquivos, nao a pasta: `lint` e `format-check` recebem
            # caminhos e precisam ver os scripts da skill.
            target_paths = sorted(
                path.relative_to(PROJECT_ROOT).as_posix()
                for skill in skills
                for path in (PROJECT_ROOT / "skills" / skill).rglob("*")
                if path.is_file() and "__pycache__" not in path.parts
            )
            target_paths += covering_tests(skills)
            triggers = {"any", "skills", "evals"}
        else:
            target_paths = _changed_paths(options.changed or None)
            if not target_paths:
                print("Nenhum arquivo alterado; nada a validar.")
                return 0
            skills = skills_in(target_paths)
            triggers = _classify(target_paths)

            print(f"\nArquivos alterados ({len(target_paths)}):")
            for path in target_paths:
                print(f"  {path}")

        if skills:
            print(f"\nSkills afetadas ({len(skills)}): {', '.join(skills)}")
            cobertura = covering_tests(skills)
            print(
                f"Testes que cobrem essas skills: {', '.join(cobertura)}"
                if cobertura
                else "Nenhum teste cobre essas skills — considere escrever um."
            )
        if triggers is not None and "config" in triggers:
            print("\nMudanca de configuracao detectada: todas as suites entram.")
            triggers = None

    planned: list[tuple[Suite, Tier]] = []
    for suite, tier, _reason in resolved:
        if tier == "off":
            continue
        if options.only and suite.name not in options.only:
            continue
        if suite.name in options.skip:
            continue
        if options.quick and not suite.quick and not options.only:
            continue
        if (
            triggers is not None
            and not options.only
            and not any(trigger in triggers for trigger in suite.triggers)
        ):
            continue
        planned.append((suite, tier))

    if not planned:
        print("Nenhuma suite selecionada.")
        return 0

    print(
        f"\nPerfil {config.profile}: {len(planned)} suite(s) — "
        + ", ".join(suite.name for suite, _ in planned)
    )

    failures: list[str] = []
    warnings: list[str] = []

    for suite, tier in planned:
        commands = _commands_for(
            suite,
            config,
            build,
            scoped=scoped and triggers is not None,
            quick=options.quick,
            skills=skills,
            target_paths=target_paths,
        )
        status = 0
        for command in commands:
            status = _run(command, options.dry_run, runner)
            if status != 0:
                break
        if status == 0:
            continue
        if tier == "blocking":
            failures.append(suite.name)
            if not options.no_bail:
                break
        else:
            warnings.append(suite.name)

    print("")
    for name in warnings:
        print(f"aviso: {name} falhou, mas e consultivo no perfil {config.profile}.")
    if failures:
        for name in failures:
            print(f"falha: {name} (bloqueante).", file=sys.stderr)
        return 1
    print(
        f"Validacao concluida com {len(warnings)} aviso(s)." if warnings else "Validacao concluida."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    """Permite rodar direto, sem passar pelo `dev.py`."""
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from scripts.dev import _run as dev_run
    from scripts.dev import _script, _tool

    builders: CommandBuilders = {"tool": _tool, "script": _script, "run": dev_run}
    return run_validate(list(argv if argv is not None else sys.argv[1:]), builders)


if __name__ == "__main__":
    raise SystemExit(main())
