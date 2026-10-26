"""Testes da conferência do lockfile.

O ponto destes testes é a distinção que o script faz: divergência de verdade
reprova, e qualquer outra falha do `uv` é "não consegui conferir". Reprovar nos
dois casos daria uma mensagem apontando a causa errada — foi o que aconteceu
quando a verificação foi escrita.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from scripts.check_lockfile import DIVERGENCE_MARKER, check_lockfile, find_uv


def test_lockfile_ausente_reprova(tmp_path: Path) -> None:
    code, message = check_lockfile(tmp_path)

    assert code == 1
    assert "uv.lock ausente" in message


def test_sem_uv_avisa_em_vez_de_reprovar(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "uv.lock").write_text("", encoding="utf-8")
    monkeypatch.setattr("scripts.check_lockfile.find_uv", lambda root: None)

    code, message = check_lockfile(tmp_path)

    # Ferramenta ausente não é projeto quebrado.
    assert code == 0
    assert "uv nao encontrado" in message


def _fake_uv(
    monkeypatch: pytest.MonkeyPatch, *, returncode: int, stderr: str = "", stdout: str = ""
) -> None:
    monkeypatch.setattr("scripts.check_lockfile.find_uv", lambda root: "uv")

    def fake_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(["uv"], returncode, stdout, stderr)

    monkeypatch.setattr(subprocess, "run", fake_run)


def test_lockfile_em_dia_passa(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "uv.lock").write_text("", encoding="utf-8")
    _fake_uv(monkeypatch, returncode=0)

    code, message = check_lockfile(tmp_path)

    assert code == 0
    assert "em dia" in message


def test_divergencia_reprova_com_instrucao(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "uv.lock").write_text("", encoding="utf-8")
    _fake_uv(
        monkeypatch,
        returncode=1,
        stderr=(
            f"error: The lockfile at `uv.lock` {DIVERGENCE_MARKER}, but `--locked` was provided."
        ),
    )

    code, message = check_lockfile(tmp_path)

    assert code == 1
    assert "uv lock" in message, "a mensagem diz o que fazer"
    assert "sync --locked" in message, "e por que o CI reprova"


def test_outra_falha_do_uv_nao_vira_divergencia(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "uv.lock").write_text("", encoding="utf-8")
    # Caso real: um interpretador quebrado no PATH da máquina.
    _fake_uv(
        monkeypatch,
        returncode=2,
        stderr="error: Failed to inspect Python interpreter from search path",
    )

    code, message = check_lockfile(tmp_path)

    assert code == 0, "nao consegui conferir nao e esta divergente"
    assert "Nao foi possivel conferir" in message
    assert "Failed to inspect" in message, "a causa real aparece"


def test_find_uv_encontra_o_do_ambiente_do_projeto(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("shutil.which", lambda _name: None)
    binario = tmp_path / ".venv" / "bin" / "uv"
    binario.parent.mkdir(parents=True)
    binario.write_text("", encoding="utf-8")

    assert find_uv(tmp_path) == str(binario)
