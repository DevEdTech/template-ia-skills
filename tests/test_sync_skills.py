"""Testes da sincronização das cópias de skills."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from scripts.check_skills import check_skills
from scripts.sync_skills import COPY_DIRS, sync_skills

SkillFactory = Callable[..., Path]


def test_sincroniza_para_as_duas_copias(tmp_path: Path, skill_factory: SkillFactory) -> None:
    skill_factory(root=tmp_path)

    assert sync_skills(tmp_path) == ["resumir-csv"]
    for relative in COPY_DIRS:
        assert (tmp_path / relative / "resumir-csv" / "SKILL.md").is_file()
    assert check_skills(tmp_path) == []


def test_remove_skill_que_deixou_de_existir(tmp_path: Path, skill_factory: SkillFactory) -> None:
    skill_factory(root=tmp_path)
    sync_skills(tmp_path)
    obsoleta = tmp_path / COPY_DIRS[0] / "antiga"
    obsoleta.mkdir()
    (obsoleta / "SKILL.md").write_text("# Antiga\n", encoding="utf-8")

    sync_skills(tmp_path)

    assert not obsoleta.exists()


def test_ignora_bytecode(tmp_path: Path, skill_factory: SkillFactory) -> None:
    skill_factory(
        root=tmp_path,
        body="# Título\n\nRode `scripts/resumir.py`.\n",
        files={"scripts/resumir.py": '"""Doc."""\n', "scripts/__pycache__/resumir.pyc": "bin"},
    )

    sync_skills(tmp_path)

    assert not (tmp_path / COPY_DIRS[0] / "resumir-csv" / "scripts" / "__pycache__").exists()
    assert check_skills(tmp_path) == []


def test_repositorio_sem_skills(tmp_path: Path) -> None:
    assert sync_skills(tmp_path) == []
