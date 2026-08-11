#!/usr/bin/env python3
"""Empacota cada skill em um `.zip` distribuível e gera o manifesto.

O pacote é o artefato de entrega do projeto: é ele que se envia para outro
repositório, para a API, para o Agent SDK ou para o diretório de skills de um
agente. O zip é determinístico (ordem e timestamps fixos), então dois builds do
mesmo conteúdo produzem bytes idênticos — o `sha256` do manifesto vira uma
identidade estável da skill.

Uso:
    python scripts/dev.py package
    python scripts/dev.py package --skill resumir-planilha

Cross-platform (Windows, macOS, Linux): usa apenas a stdlib.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Permite tanto `python scripts/package_skills.py` quanto `import scripts.package_skills`.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.check_skills import check_skills, is_content, parse_frontmatter  # noqa: E402

DIST_DIRNAME = "dist"
# Data fixa exigida pelo formato zip (o campo não aceita anos anteriores a 1980).
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def _skill_dirs(root: Path, only: str | None) -> list[Path]:
    source = root / "skills"
    directories = sorted(entry for entry in source.iterdir() if entry.is_dir())
    if only is None:
        return directories
    selected = [entry for entry in directories if entry.name == only]
    if not selected:
        raise FileNotFoundError(f'Skill "{only}" não encontrada em {source}.')
    return selected


def _description(skill_dir: Path) -> str:
    meta = parse_frontmatter((skill_dir / "SKILL.md").read_text(encoding="utf-8")) or {}
    return meta.get("description", "")


def build_bundle(skill_dir: Path, dist_dir: Path) -> Path:
    """Gera `dist/<skill>.zip` com a pasta da skill na raiz do arquivo."""
    dist_dir.mkdir(parents=True, exist_ok=True)
    bundle = dist_dir / f"{skill_dir.name}.zip"
    files = sorted(path for path in skill_dir.rglob("*") if is_content(path))

    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            arcname = f"{skill_dir.name}/{path.relative_to(skill_dir).as_posix()}"
            info = zipfile.ZipInfo(arcname, date_time=FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return bundle


def build_bundles(root: Path = PROJECT_ROOT, only: str | None = None) -> list[Path]:
    """Empacota as skills selecionadas e escreve `dist/manifest.json`."""
    dist_dir = root / DIST_DIRNAME
    if dist_dir.exists() and only is None:
        shutil.rmtree(dist_dir)

    bundles: list[Path] = []
    entries: list[dict[str, object]] = []
    for skill_dir in _skill_dirs(root, only):
        bundle = build_bundle(skill_dir, dist_dir)
        payload = bundle.read_bytes()
        entries.append(
            {
                "name": skill_dir.name,
                "description": _description(skill_dir),
                "bundle": bundle.name,
                "files": sorted(
                    path.relative_to(skill_dir).as_posix()
                    for path in skill_dir.rglob("*")
                    if is_content(path)
                ),
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
        bundles.append(bundle)

    manifest = dist_dir / "manifest.json"
    if only is not None and manifest.is_file():
        previous = json.loads(manifest.read_text(encoding="utf-8"))
        kept = [e for e in previous["skills"] if e["name"] != only]
        entries = sorted([*kept, *entries], key=lambda entry: str(entry["name"]))
    manifest.write_text(
        json.dumps({"skills": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return bundles


def main() -> int:
    parser = argparse.ArgumentParser(description="Empacota as skills em arquivos distribuíveis.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--skill", help="Empacota apenas a skill informada.")
    args = parser.parse_args()
    root = args.root.resolve()

    errors = check_skills(root, compare_copies=False)
    if errors:
        print("Empacotamento cancelado: as skills não passaram na verificação.\n", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    bundles = build_bundles(root, args.skill)
    print(f"Pacotes gerados em {(root / DIST_DIRNAME).name}/:")
    for bundle in bundles:
        print(f"  - {bundle.name} ({bundle.stat().st_size} bytes)")
    print(f"  - manifest.json ({len(bundles)} skill(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
