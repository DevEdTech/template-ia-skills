"""Testes do empacotamento e do smoke dos pacotes."""

from __future__ import annotations

import json
import zipfile
from collections.abc import Callable
from pathlib import Path

import pytest
from scripts.package_skills import build_bundles
from scripts.smoke_bundles import smoke_bundles

SkillFactory = Callable[..., Path]

SCRIPT = '''"""Passo determinístico de exemplo."""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--value", default="")
    parser.parse_args()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _skill_with_script(skill_factory: SkillFactory, root: Path, name: str = "resumir-csv") -> Path:
    return skill_factory(
        name=name,
        root=root,
        body="# Título\n\nRode `scripts/resumir.py --help`.\n",
        files={"scripts/resumir.py": SCRIPT},
    )


def test_pacote_contem_a_skill_na_raiz(tmp_path: Path, skill_factory: SkillFactory) -> None:
    _skill_with_script(skill_factory, tmp_path)

    bundles = build_bundles(tmp_path)

    assert [bundle.name for bundle in bundles] == ["resumir-csv.zip"]
    with zipfile.ZipFile(bundles[0]) as archive:
        assert sorted(archive.namelist()) == [
            "resumir-csv/SKILL.md",
            "resumir-csv/scripts/resumir.py",
        ]


def test_pacote_e_deterministico(tmp_path: Path, skill_factory: SkillFactory) -> None:
    _skill_with_script(skill_factory, tmp_path)

    first = build_bundles(tmp_path)[0].read_bytes()
    second = build_bundles(tmp_path)[0].read_bytes()

    assert first == second


def test_manifesto_registra_metadados(tmp_path: Path, skill_factory: SkillFactory) -> None:
    _skill_with_script(skill_factory, tmp_path)

    build_bundles(tmp_path)

    manifest = json.loads((tmp_path / "dist" / "manifest.json").read_text(encoding="utf-8"))
    entry = manifest["skills"][0]
    assert entry["name"] == "resumir-csv"
    assert entry["description"].startswith("Resume um arquivo CSV")
    assert entry["files"] == ["SKILL.md", "scripts/resumir.py"]
    assert len(entry["sha256"]) == 64


def test_empacotar_uma_skill_preserva_as_demais(
    tmp_path: Path, skill_factory: SkillFactory
) -> None:
    _skill_with_script(skill_factory, tmp_path)
    skill_factory(name="revisar-contrato", root=tmp_path)

    build_bundles(tmp_path)
    build_bundles(tmp_path, "revisar-contrato")

    manifest = json.loads((tmp_path / "dist" / "manifest.json").read_text(encoding="utf-8"))
    assert [entry["name"] for entry in manifest["skills"]] == ["resumir-csv", "revisar-contrato"]


def test_empacotar_skill_inexistente(tmp_path: Path, skill_factory: SkillFactory) -> None:
    skill_factory(root=tmp_path)

    with pytest.raises(FileNotFoundError):
        build_bundles(tmp_path, "nao-existe")


def test_smoke_aprova_pacote_autocontido(tmp_path: Path, skill_factory: SkillFactory) -> None:
    _skill_with_script(skill_factory, tmp_path)
    build_bundles(tmp_path)

    assert smoke_bundles(tmp_path) == []


def test_smoke_reprova_script_que_falha_isolado(
    tmp_path: Path, skill_factory: SkillFactory
) -> None:
    quebrado = SCRIPT.replace("    parser.parse_args()", "    raise SystemExit(3)")
    skill_factory(
        root=tmp_path,
        body="# Título\n\nRode `scripts/resumir.py --help`.\n",
        files={"scripts/resumir.py": quebrado},
    )
    build_bundles(tmp_path)

    assert any("--help` falhou" in error for error in smoke_bundles(tmp_path))


def test_smoke_nao_executa_skill_com_dependencias(
    tmp_path: Path, skill_factory: SkillFactory
) -> None:
    quebrado = SCRIPT.replace("import argparse", "import argparse\nimport pandas")
    skill_factory(
        root=tmp_path,
        body="# Título\n\nRode `scripts/resumir.py --help`.\n",
        files={"scripts/resumir.py": quebrado, "requirements.txt": "pandas>=2.0\n"},
    )
    build_bundles(tmp_path)

    assert smoke_bundles(tmp_path) == []


def test_smoke_sem_pacotes(tmp_path: Path) -> None:
    assert any("Nenhum pacote" in error for error in smoke_bundles(tmp_path))


def test_smoke_reprova_pacote_sem_skill_md(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    with zipfile.ZipFile(dist / "vazia.zip", "w") as archive:
        archive.writestr("vazia/README.md", "sem skill")

    assert any("não contém" in error for error in smoke_bundles(tmp_path))
