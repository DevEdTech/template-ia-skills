#!/usr/bin/env python3
"""Valida os cenários de avaliação das skills e imprime a folha de execução.

Uma skill só é confiável quando duas coisas foram testadas: se ela **dispara**
nas situações certas (e não dispara nas erradas) e se, ao disparar, produz o
resultado esperado. Este script garante que cada skill tenha esses cenários
declarados em `evals/<skill>.json` e gera a folha para rodá-los com um agente.

Uso:
    python scripts/dev.py check-evals
    python scripts/dev.py eval-sheet [nome-da-skill]

Formato esperado de `evals/<skill>.json`:

    {
      "skill": "plan-skill",
      "trigger": [
        {"prompt": "...", "should_trigger": true},
        {"prompt": "...", "should_trigger": false}
      ],
      "execution": [
        {"prompt": "...", "expect": ["...", "..."], "red_flags": ["..."]}
      ]
    }

Cross-platform (Windows, macOS, Linux): usa apenas a stdlib.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVALS_DIRNAME = "evals"
SKILLS_DIRNAME = "skills"

TOP_LEVEL_KEYS = {"skill", "trigger", "execution"}
TRIGGER_KEYS = {"prompt", "should_trigger"}
EXECUTION_KEYS = {"prompt", "expect", "red_flags"}

MIN_TRIGGER_CASES = 3
MIN_EXPECTATIONS = 2


def _skill_names(root: Path) -> list[str]:
    directory = root / SKILLS_DIRNAME
    if not directory.is_dir():
        return []
    return sorted(entry.name for entry in directory.iterdir() if entry.is_dir())


def _non_empty_strings(values: Any) -> bool:
    return isinstance(values, list) and all(isinstance(v, str) and v.strip() for v in values)


def _check_trigger_cases(label: str, cases: Any) -> list[str]:
    if not isinstance(cases, list) or len(cases) < MIN_TRIGGER_CASES:
        return [f"{label}: informe ao menos {MIN_TRIGGER_CASES} casos em `trigger`."]
    errors: list[str] = []
    positives = negatives = 0
    for index, case in enumerate(cases, start=1):
        where = f"{label}: trigger[{index}]"
        if not isinstance(case, dict) or set(case) != TRIGGER_KEYS:
            errors.append(f"{where}: use exatamente as chaves {sorted(TRIGGER_KEYS)}.")
            continue
        if not isinstance(case["prompt"], str) or not case["prompt"].strip():
            errors.append(f"{where}: `prompt` vazio.")
        if not isinstance(case["should_trigger"], bool):
            errors.append(f"{where}: `should_trigger` deve ser true ou false.")
            continue
        positives += int(case["should_trigger"])
        negatives += int(not case["should_trigger"])
    if not positives:
        errors.append(f"{label}: falta um caso positivo (`should_trigger: true`).")
    if not negatives:
        errors.append(
            f"{label}: falta um caso negativo (`should_trigger: false`) — é ele que detecta "
            "descrição ampla demais, que rouba o gatilho de outras skills."
        )
    return errors


def _check_execution_cases(label: str, cases: Any) -> list[str]:
    if not isinstance(cases, list) or not cases:
        return [f"{label}: informe ao menos um cenário em `execution`."]
    errors: list[str] = []
    for index, case in enumerate(cases, start=1):
        where = f"{label}: execution[{index}]"
        if not isinstance(case, dict) or set(case) != EXECUTION_KEYS:
            errors.append(f"{where}: use exatamente as chaves {sorted(EXECUTION_KEYS)}.")
            continue
        if not isinstance(case["prompt"], str) or not case["prompt"].strip():
            errors.append(f"{where}: `prompt` vazio.")
        if not _non_empty_strings(case["expect"]) or len(case["expect"]) < MIN_EXPECTATIONS:
            errors.append(
                f"{where}: `expect` precisa de ao menos {MIN_EXPECTATIONS} resultados observáveis."
            )
        if not _non_empty_strings(case["red_flags"]) or not case["red_flags"]:
            errors.append(f"{where}: `red_flags` precisa de ao menos um sinal de alerta.")
    return errors


def check_evals(root: Path = PROJECT_ROOT) -> list[str]:
    """Confere se toda skill tem cenários de avaliação completos."""
    skills = _skill_names(root)
    evals_dir = root / EVALS_DIRNAME
    errors: list[str] = []

    existing = sorted(path.stem for path in evals_dir.glob("*.json")) if evals_dir.is_dir() else []
    for orphan in sorted(set(existing) - set(skills)):
        errors.append(f"evals/{orphan}.json: não existe skill correspondente.")

    for skill in skills:
        label = f"evals/{skill}.json"
        path = evals_dir / f"{skill}.json"
        if not path.is_file():
            errors.append(f"{label}: ausente. Toda skill precisa de cenários de avaliação.")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"{label}: JSON inválido ({error.msg}, linha {error.lineno}).")
            continue
        if not isinstance(data, dict) or set(data) != TOP_LEVEL_KEYS:
            errors.append(f"{label}: use exatamente as chaves {sorted(TOP_LEVEL_KEYS)}.")
            continue
        if data["skill"] != skill:
            errors.append(f'{label}: campo "skill" ("{data["skill"]}") difere do arquivo.')
        errors.extend(_check_trigger_cases(label, data["trigger"]))
        errors.extend(_check_execution_cases(label, data["execution"]))
    return errors


def render_sheet(root: Path, skill: str | None = None) -> str:
    """Monta a folha de execução: prompts para colar em um agente limpo."""
    evals_dir = root / EVALS_DIRNAME
    names = [skill] if skill else _skill_names(root)
    blocks: list[str] = ["# Folha de avaliação de skills", ""]
    for name in names:
        path = evals_dir / f"{name}.json"
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        blocks.append(f"## {name}")
        blocks.append("")
        blocks.append("### Gatilho (sessão nova, sem citar a skill)")
        for case in data["trigger"]:
            esperado = "deve acionar" if case["should_trigger"] else "NÃO deve acionar"
            blocks.append(f"- [ ] ({esperado}) {case['prompt']}")
        blocks.append("")
        blocks.append("### Execução")
        for case in data["execution"]:
            blocks.append(f"- [ ] {case['prompt']}")
            for expectation in case["expect"]:
                blocks.append(f"    - esperado: {expectation}")
            for flag in case["red_flags"]:
                blocks.append(f"    - alerta: {flag}")
        blocks.append("")
    return "\n".join(blocks).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida ou imprime os cenários de avaliação.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--sheet", action="store_true", help="Imprime a folha de execução.")
    parser.add_argument("--skill", help="Restringe a folha a uma skill.")
    args = parser.parse_args()
    root = args.root.resolve()

    if args.sheet:
        print(render_sheet(root, args.skill), end="")
        return 0

    errors = check_evals(root)
    if errors:
        print("Validação das avaliações FALHOU:\n", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"Validação das avaliações OK: {len(_skill_names(root))} skill(s) com cenários.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
