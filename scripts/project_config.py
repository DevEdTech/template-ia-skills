#!/usr/bin/env python3
"""Perfil do projeto: a unica fonte da verdade sobre quanto rigor vale aqui.

Um repositorio de skills em exploracao e um que distribui pacotes para outras
pessoas nao merecem o mesmo portao. Em vez de espalhar condicionais pelos
scripts, o estado fica em `.template-state.json` e todo mundo le daqui.

    profile  prototipo | padrao | rigoroso

`profile` decide o que e bloqueante. No `rigoroso`, aviso de heuristica e
dispensa justificada tambem reprovam: e o perfil de quem publica.

Cross-platform (Windows, macOS, Linux): usa apenas a stdlib.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

PROJECT_ROOT = Path(__file__).resolve().parent.parent

Profile = Literal["prototipo", "padrao", "rigoroso"]
Tier = Literal["blocking", "advisory", "off"]

PROFILES: tuple[str, ...] = ("prototipo", "padrao", "rigoroso")
DEFAULT_PROFILE: Profile = "padrao"

#: Limites de cobertura por perfil dos scripts do template e das skills.
COVERAGE_THRESHOLDS: dict[str, int | None] = {
    "prototipo": None,
    "padrao": 70,
    "rigoroso": 80,
}

DEFAULT_CAPABILITIES: dict[str, bool] = {
    #: Empacotamento em `dist/` e smoke do pacote fora do repositorio.
    "packaging": True,
    #: Cenarios de gatilho e execucao em `evals/`.
    "evals": True,
}


@dataclass(frozen=True)
class Suite:
    """Uma suite do `validate`, com o que ela exige e o que a aciona."""

    name: str
    label: str
    tier: dict[str, Tier]
    requires: str | None = None
    quick: bool = False
    triggers: tuple[str, ...] = ()
    accepts_paths: bool = False


ALL_BLOCKING: dict[str, Tier] = {
    "prototipo": "blocking",
    "padrao": "blocking",
    "rigoroso": "blocking",
}
ADVISORY_IN_DRAFT: dict[str, Tier] = {
    "prototipo": "advisory",
    "padrao": "blocking",
    "rigoroso": "blocking",
}

SUITES: tuple[Suite, ...] = (
    Suite("sync-skills", "Sincronizar copias", ADVISORY_IN_DRAFT, triggers=("skills",)),
    Suite("check-skills", "Skills", ALL_BLOCKING, quick=True, triggers=("skills",)),
    Suite(
        "check-evals",
        "Avaliacoes",
        ADVISORY_IN_DRAFT,
        requires="evals",
        triggers=("skills", "evals"),
    ),
    Suite("check-docs", "Documentacao", ADVISORY_IN_DRAFT, triggers=("docs",)),
    Suite(
        "format-check",
        "Formatacao",
        ADVISORY_IN_DRAFT,
        triggers=("any",),
        accepts_paths=True,
    ),
    Suite(
        "lint",
        "Lint",
        ALL_BLOCKING,
        quick=True,
        triggers=("skills", "scripts"),
        accepts_paths=True,
    ),
    Suite("typecheck", "Tipos", ALL_BLOCKING, quick=True, triggers=("skills", "scripts", "config")),
    Suite("test", "Testes", ALL_BLOCKING, quick=True, triggers=("skills", "scripts")),
    Suite(
        "package",
        "Empacotar",
        ADVISORY_IN_DRAFT,
        requires="packaging",
        triggers=("skills", "config"),
    ),
    Suite(
        "smoke-bundles",
        "Smoke dos pacotes",
        ADVISORY_IN_DRAFT,
        requires="packaging",
        triggers=("skills", "config"),
    ),
)

EXTERNAL_SUITES: dict[str, str] = {
    "eval-sheet": "Planilha de avaliacao manual de uma skill",
    "audit": "Auditoria de dependencias (depende de rede)",
}


@dataclass(frozen=True)
class ProjectConfig:
    """Estado efetivo do projeto."""

    profile: str = DEFAULT_PROFILE
    capabilities: dict[str, bool] = field(default_factory=lambda: dict(DEFAULT_CAPABILITIES))

    @property
    def coverage(self) -> int | None:
        """Limite minimo de cobertura do perfil, ou None quando nao se aplica."""
        return COVERAGE_THRESHOLDS[self.profile]

    @property
    def strict_findings(self) -> bool:
        """No perfil de publicacao, aviso de skill tambem reprova."""
        return self.profile == "rigoroso"

    def has(self, capability: str) -> bool:
        """Se o projeto usa a capacidade informada."""
        return self.capabilities.get(capability, False)


def read_project_config(root: Path = PROJECT_ROOT) -> ProjectConfig:
    """Le perfil e capacidades efetivos do projeto."""
    state_file = root / ".template-state.json"
    state: dict[str, object] = {}
    if state_file.is_file():
        try:
            loaded = json.loads(state_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise SystemExit(f".template-state.json invalido: {error}") from error
        if isinstance(loaded, dict):
            state = loaded

    raw_profile = state.get("profile")
    profile = (
        raw_profile if isinstance(raw_profile, str) and raw_profile in PROFILES else DEFAULT_PROFILE
    )

    capabilities = dict(DEFAULT_CAPABILITIES)
    declared = state.get("capabilities")
    if isinstance(declared, dict):
        for key, value in declared.items():
            if isinstance(key, str) and isinstance(value, bool):
                capabilities[key] = value

    return ProjectConfig(profile=profile, capabilities=capabilities)


def has_capability(name: str, root: Path = PROJECT_ROOT) -> bool:
    """Atalho para consultar uma capacidade."""
    return read_project_config(root).has(name)


def resolve_suites(config: ProjectConfig) -> list[tuple[Suite, Tier, str | None]]:
    """Resolve o nivel de cada suite para o perfil e as capacidades atuais."""
    resolved: list[tuple[Suite, Tier, str | None]] = []
    for suite in SUITES:
        if suite.requires is not None and not config.has(suite.requires):
            resolved.append((suite, "off", f'capacidade "{suite.requires}" desligada'))
            continue
        resolved.append((suite, suite.tier.get(config.profile, "blocking"), None))
    return resolved


def main() -> int:
    """Imprime o estado atual, para inspecao rapida."""
    config = read_project_config()
    print(f"Perfil: {config.profile}")
    ativas = ", ".join(name for name, on in config.capabilities.items() if on) or "nenhuma"
    print(f"Capacidades: {ativas}")
    print(
        f"Cobertura: minimo de {config.coverage}%"
        if config.coverage is not None
        else "Cobertura: nao aplicada neste perfil"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
