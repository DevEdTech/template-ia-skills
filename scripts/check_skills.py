#!/usr/bin/env python3
"""Verifica a integridade das skills: metadados, estrutura, links e cópias.

Executado dentro de `python scripts/dev.py validate`. Sai com código != 0 em erro.
Uso: `python scripts/dev.py check-skills` (ou `python scripts/check_skills.py`).

Regras verificadas (detalhadas em docs/architecture.md e docs/skill-metadata.md):

Metadados
 1. Cada skill em `skills/` possui um `SKILL.md` com frontmatter YAML válido.
 2. O frontmatter só usa chaves reconhecidas por quem carrega a skill.
 3. `name` bate com a pasta, é kebab-case, tem no máximo 64 caracteres e 5 termos.
 4. `description` é uma linha, tem de 40 a 1024 caracteres, diz o que a skill faz
    e quando deve ser acionada, e não começa com enchimento ("Esta skill...").
 5. O corpo começa com um título `#` e cabe em 500 linhas (divulgação progressiva).

Estrutura
 6. A pasta da skill só contém `SKILL.md`, `reference/`, `scripts/`, `assets/`
    e, quando houver dependências, `requirements.txt`.
 7. Todo arquivo da skill é alcançável a partir do `SKILL.md` (sem órfãos).
 8. Todo link relativo existe e aponta para dentro da própria skill.
 9. Os scripts têm nome `snake_case` único no repositório e docstring de módulo.
10. Os scripts importam apenas a biblioteca padrão, scripts irmãos ou pacotes
    declarados no `requirements.txt` da skill (a skill precisa ser autocontida).
11. A skill inteira cabe no limite de tamanho de um pacote distribuível.

Sincronização
12. As cópias em `.claude/skills` e `.agents/skills` existem e são idênticas.

Cross-platform (Windows, macOS, Linux): usa apenas a stdlib.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from urllib.parse import unquote

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIRNAME = "skills"
COPY_DIRS = (".claude/skills", ".agents/skills")

ALLOWED_TOP_LEVEL = {"SKILL.md", "reference", "scripts", "assets", "requirements.txt"}
CONTENT_DIRS = ("reference", "scripts", "assets")
ALLOWED_FRONTMATTER = {"name", "description", "license", "allowed-tools", "metadata"}

NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
MAX_NAME_CHARS = 64
MAX_NAME_TERMS = 5

MIN_DESCRIPTION_CHARS = 40
MAX_DESCRIPTION_CHARS = 1024
# Uma descrição sem marcador de acionamento não ensina o agente *quando* usar
# a skill — e uma skill que não dispara é uma skill que não existe.
TRIGGER_MARKERS = ("quando", "use ", "usar", "ao ", "antes de", "depois de", "when", "for ")
FILLER_PREFIXES = ("esta skill", "essa skill", "uma skill", "a skill", "this skill", "skill que")

MAX_BODY_LINES = 500
MAX_SKILL_BYTES = 5 * 1024 * 1024

SCRIPT_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*\.py$")
REQUIREMENT_PATTERN = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")

# Artefatos de execução (bytecode) nascem dentro de `scripts/` quando os testes
# importam o script. Não são conteúdo da skill e não entram no pacote.
IGNORED_DIRS = {"__pycache__"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}

_MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_INLINE_PATH = re.compile(r"(?:reference|scripts|assets)/[\w./-]+")
_EXTERNAL = re.compile(r"^(?:https?:|mailto:|tel:|#)")


def list_skill_dirs(directory: Path) -> list[str]:
    """Lista as pastas de skill (arquivos soltos na raiz são ignorados)."""
    if not directory.is_dir():
        return []
    return sorted(entry.name for entry in directory.iterdir() if entry.is_dir())


def is_content(path: Path) -> bool:
    """Um arquivo é conteúdo da skill quando não é artefato de execução."""
    return (
        path.is_file()
        and path.suffix not in IGNORED_SUFFIXES
        and not IGNORED_DIRS.intersection(path.parts)
    )


def list_files_recursive(directory: Path) -> list[str]:
    """Lista caminhos de arquivo relativos a `directory`, com "/" normalizado."""
    if not directory.exists():
        return []
    return sorted(
        p.relative_to(directory).as_posix() for p in directory.rglob("*") if is_content(p)
    )


def parse_frontmatter(content: str) -> dict[str, str] | None:
    """Parser mínimo de frontmatter YAML (pares `chave: valor` entre `---`).

    Só lê as chaves de primeiro nível: linhas indentadas pertencem ao valor
    anterior (por exemplo, um bloco `metadata:`) e não viram chaves novas.
    """
    lines = content.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return None

    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), -1)
    if end == -1:
        return None

    data: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.startswith((" ", "\t", "#", "-")):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        data[key.strip()] = value
    return data


def body_after_frontmatter(content: str) -> list[str]:
    """Retorna as linhas do corpo do SKILL.md, sem o frontmatter."""
    lines = content.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return lines
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), -1)
    return lines if end == -1 else lines[end + 1 :]


def _check_name(skill: str, name: str | None) -> list[str]:
    if not name:
        return [f'{skill}: campo "name" ausente ou vazio no frontmatter.']
    errors: list[str] = []
    if name != skill:
        errors.append(f'{skill}: "name" ("{name}") difere do nome da pasta.')
    if not NAME_PATTERN.match(name):
        errors.append(f'{skill}: "name" deve ser kebab-case (letras minúsculas, dígitos e "-").')
    if len(name) > MAX_NAME_CHARS:
        errors.append(f'{skill}: "name" passa de {MAX_NAME_CHARS} caracteres.')
    if len(name.split("-")) > MAX_NAME_TERMS:
        errors.append(
            f'{skill}: "name" tem mais de {MAX_NAME_TERMS} termos; prefira verbo + objeto.'
        )
    return errors


def _check_description(skill: str, description: str | None) -> list[str]:
    if not description:
        return [f'{skill}: campo "description" ausente ou vazio no frontmatter.']
    errors: list[str] = []
    normalized = description.strip().lower()
    if len(description) < MIN_DESCRIPTION_CHARS:
        errors.append(
            f'{skill}: "description" tem menos de {MIN_DESCRIPTION_CHARS} caracteres; '
            "diga o que a skill faz e quando usá-la."
        )
    if len(description) > MAX_DESCRIPTION_CHARS:
        errors.append(
            f'{skill}: "description" passa de {MAX_DESCRIPTION_CHARS} caracteres '
            "(limite de quem carrega a skill)."
        )
    if "\n" in description:
        errors.append(f'{skill}: "description" deve ocupar uma única linha.')
    if not any(marker in normalized for marker in TRIGGER_MARKERS):
        errors.append(
            f'{skill}: "description" não indica o acionamento; inclua "use quando ..." '
            "com as situações que disparam a skill."
        )
    if normalized.startswith(FILLER_PREFIXES):
        errors.append(f'{skill}: "description" começa com enchimento; comece pelo que a skill faz.')
    return errors


def _check_frontmatter(skill: str, skill_md: Path) -> list[str]:
    content = skill_md.read_text(encoding="utf-8")
    meta = parse_frontmatter(content)
    if meta is None:
        return [
            f"{skill}: frontmatter YAML ausente ou malformado em SKILL.md "
            '(esperado bloco entre linhas "---").'
        ]

    errors: list[str] = []
    unknown = sorted(set(meta) - ALLOWED_FRONTMATTER)
    if unknown:
        errors.append(
            f"{skill}: chave(s) desconhecida(s) no frontmatter: {', '.join(unknown)}. "
            f"Permitidas: {', '.join(sorted(ALLOWED_FRONTMATTER))}."
        )
    errors.extend(_check_name(skill, meta.get("name")))
    errors.extend(_check_description(skill, meta.get("description")))

    body = body_after_frontmatter(content)
    heading = next((line for line in body if line.strip()), "")
    if not heading.startswith("# "):
        errors.append(f"{skill}: o corpo do SKILL.md deve começar com um título `# `.")
    if len(body) > MAX_BODY_LINES:
        errors.append(
            f"{skill}: SKILL.md tem {len(body)} linhas (máximo {MAX_BODY_LINES}). "
            "Mova o detalhamento para `reference/` e carregue sob demanda."
        )
    return errors


def _referenced_targets(text: str) -> tuple[set[str], set[str]]:
    """Separa os caminhos citados por um documento da skill.

    Devolve `(links, menções)`. Os links markdown são um compromisso: precisam
    existir dentro da skill. As menções em texto corrido (`scripts/x.py`) só
    contam para saber que o arquivo é usado — uma skill também cita comandos do
    repositório, como `scripts/dev.py`, que não vivem dentro dela.
    """
    links: set[str] = set()
    for raw in _MARKDOWN_LINK.findall(text):
        link = raw.strip().strip("<>").split(" ")[0]
        if link and not _EXTERNAL.match(link):
            links.add(unquote(link.split("#")[0]))
    return links, set(_INLINE_PATH.findall(text))


def _check_layout(skill: str, skill_dir: Path) -> list[str]:
    errors: list[str] = []
    for entry in sorted(skill_dir.iterdir()):
        if entry.name in IGNORED_DIRS:
            continue
        if entry.name not in ALLOWED_TOP_LEVEL:
            errors.append(
                f"{skill}: entrada não prevista `{entry.name}`. "
                f"Use apenas {', '.join(sorted(ALLOWED_TOP_LEVEL))}."
            )
    total = sum(path.stat().st_size for path in skill_dir.rglob("*") if is_content(path))
    if total > MAX_SKILL_BYTES:
        errors.append(
            f"{skill}: a skill ocupa {total // 1024} KiB "
            f"(máximo {MAX_SKILL_BYTES // 1024} KiB); mantenha os assets enxutos."
        )
    return errors


def _check_references(skill: str, skill_dir: Path) -> list[str]:
    """Confere links quebrados, fugas da pasta e arquivos órfãos."""
    errors: list[str] = []
    reached: set[str] = set()
    queue = [Path("SKILL.md")]
    visited: set[str] = set()

    while queue:
        current = queue.pop()
        key = current.as_posix()
        if key in visited:
            continue
        visited.add(key)
        document = skill_dir / current
        if document.suffix != ".md" or not document.is_file():
            continue
        links, mentions = _referenced_targets(document.read_text(encoding="utf-8"))
        for target in sorted(links):
            if target.startswith("/") or Path(target).is_absolute():
                errors.append(f"{skill}: {key} usa caminho absoluto `{target}`.")
                continue
            resolved = (document.parent / target).resolve()
            try:
                relative = resolved.relative_to(skill_dir.resolve())
            except ValueError:
                errors.append(f"{skill}: {key} aponta para fora da skill: `{target}`.")
                continue
            if not resolved.exists():
                errors.append(f"{skill}: {key} referencia arquivo inexistente `{target}`.")
                continue
            reached.add(relative.as_posix())
            queue.append(relative)
        for target in sorted(mentions):
            resolved = (skill_dir / target).resolve()
            if resolved.is_file() and resolved.is_relative_to(skill_dir.resolve()):
                relative = resolved.relative_to(skill_dir.resolve())
                reached.add(relative.as_posix())
                queue.append(relative)

    for directory in CONTENT_DIRS:
        for filename in list_files_recursive(skill_dir / directory):
            path = f"{directory}/{filename}"
            if path not in reached:
                errors.append(
                    f"{skill}: `{path}` não é citado pelo SKILL.md nem por um arquivo citado. "
                    "Referencie-o ou remova-o."
                )
    return errors


def _declared_requirements(skill_dir: Path) -> set[str]:
    requirements = skill_dir / "requirements.txt"
    if not requirements.is_file():
        return set()
    names: set[str] = set()
    for line in requirements.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("#"):
            continue
        match = REQUIREMENT_PATTERN.match(line)
        if match:
            names.add(match.group(1).replace("-", "_").lower())
    return names


def _imported_roots(tree: ast.Module) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def _check_scripts(skill: str, skill_dir: Path) -> list[str]:
    errors: list[str] = []
    script_dir = skill_dir / "scripts"
    if not script_dir.is_dir():
        return errors

    siblings = {path.stem for path in script_dir.glob("*.py")}
    allowed = set(sys.stdlib_module_names) | siblings | _declared_requirements(skill_dir)

    for script in sorted(script_dir.iterdir()):
        if script.name in IGNORED_DIRS or script.suffix in IGNORED_SUFFIXES:
            continue
        if script.is_dir():
            errors.append(f"{skill}: `scripts/{script.name}` — use arquivos, não subpastas.")
            continue
        if script.suffix != ".py":
            errors.append(f"{skill}: `scripts/{script.name}` não é um script Python.")
            continue
        if not SCRIPT_NAME_PATTERN.match(script.name):
            errors.append(f"{skill}: `scripts/{script.name}` deve usar snake_case.")
        source = script.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError as error:
            errors.append(f"{skill}: `scripts/{script.name}` não compila ({error.msg}).")
            continue
        if not ast.get_docstring(tree):
            errors.append(f"{skill}: `scripts/{script.name}` está sem docstring de módulo.")
        for root in sorted(_imported_roots(tree)):
            if root not in allowed:
                errors.append(
                    f"{skill}: `scripts/{script.name}` importa `{root}`, que não é da stdlib "
                    "nem está no requirements.txt da skill."
                )
    return errors


def validate_skill(skill_dir: Path) -> list[str]:
    """Valida uma skill isolada (também usada sobre o pacote extraído)."""
    skill = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"{skill}: arquivo SKILL.md ausente."]
    return [
        *_check_frontmatter(skill, skill_md),
        *_check_layout(skill, skill_dir),
        *_check_references(skill, skill_dir),
        *_check_scripts(skill, skill_dir),
    ]


def _check_unique_scripts(root: Path, skills: list[str]) -> list[str]:
    """Nomes de script se repetindo quebram o typecheck e confundem a documentação."""
    owners: dict[str, list[str]] = {}
    for skill in skills:
        for script in sorted((root / SOURCE_DIRNAME / skill / "scripts").glob("*.py")):
            owners.setdefault(script.name, []).append(skill)
    return [
        f"Nome de script repetido `{name}` em {', '.join(users)}; use nomes descritivos e únicos."
        for name, users in sorted(owners.items())
        if len(users) > 1
    ]


def _compare_copies(root: Path, skills: list[str]) -> list[str]:
    errors: list[str] = []
    source_root = root / SOURCE_DIRNAME
    for relative in COPY_DIRS:
        dest_root = root / relative
        if not dest_root.exists():
            errors.append(
                f'Cópia ausente: "{relative}" não existe. Rode "python scripts/dev.py sync-skills".'
            )
            continue

        dest_skills = list_skill_dirs(dest_root)
        missing = [s for s in skills if s not in dest_skills]
        extra = [s for s in dest_skills if s not in skills]
        if missing:
            errors.append(f'"{relative}": skill(s) faltando: {", ".join(missing)}.')
        if extra:
            errors.append(f'"{relative}": skill(s) extra(s): {", ".join(extra)}.')

        for skill in skills:
            source_files = list_files_recursive(source_root / skill)
            dest_files = list_files_recursive(dest_root / skill)
            for file in source_files:
                if file not in set(dest_files):
                    errors.append(f'"{relative}/{skill}": arquivo faltando na cópia: {file}.')
                    continue
                if (source_root / skill / file).read_bytes() != (
                    dest_root / skill / file
                ).read_bytes():
                    errors.append(f'"{relative}/{skill}": conteúdo divergente em {file}.')
            for file in dest_files:
                if file not in set(source_files):
                    errors.append(f'"{relative}/{skill}": arquivo extra na cópia: {file}.')
    return errors


def check_skills(root: Path = PROJECT_ROOT, *, compare_copies: bool = True) -> list[str]:
    """Valida todas as skills do repositório e devolve a lista de problemas."""
    source_root = root / SOURCE_DIRNAME
    skills = list_skill_dirs(source_root)
    if not skills:
        return [f'Nenhuma skill encontrada em "{source_root}".']

    errors: list[str] = []
    for skill in skills:
        errors.extend(validate_skill(source_root / skill))
    errors.extend(_check_unique_scripts(root, skills))
    if compare_copies:
        errors.extend(_compare_copies(root, skills))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifica metadados, estrutura e cópias das skills."
    )
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--skip-copies",
        action="store_true",
        help="Não compara as cópias geradas em .claude/skills e .agents/skills.",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    errors = check_skills(root, compare_copies=not args.skip_copies)

    if errors:
        print("Verificação de skills FALHOU:\n", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print(f"\nTotal de problemas: {len(errors)}.", file=sys.stderr)
        return 1

    skills = list_skill_dirs(root / SOURCE_DIRNAME)
    print(f"Verificação de skills OK: {len(skills)} skill(s) validada(s) e sincronizada(s).")
    for skill in skills:
        print(f"  - {skill}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
