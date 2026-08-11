# Atualizando o template

Este projeto nasceu de um template. Quando o template evolui, traga as melhorias
sem perder as suas skills.

## O que é seu e o que é do template

| Seu | Do template |
| --- | ----------- |
| `skills/` (exceto a demonstração) | `scripts/` (runner e verificações) |
| `evals/` das suas skills | `pyproject.toml`, workflows, hooks |
| `docs/skills/`, `docs/evaluations/` | `docs/` estrutural, `AGENTS.md`, `CLAUDE.md` |
| `tests/skills/` das suas skills | `tests/` das ferramentas |

## Fluxo

1. Crie uma branch: `git checkout -b chore/atualiza-template`.
2. Compare com o template de origem e traga apenas os arquivos da coluna direita.
3. Releia `AGENTS.md` e `docs/architecture.md`: regras novas podem exigir ajuste
   nas suas skills (por exemplo, um limite novo verificado pelo `check-skills`).
4. Rode `python scripts/dev.py validate`.
5. Corrija o que a verificação apontar, uma skill por vez.
6. Reavalie as skills cujo gatilho ou processo mudou.
7. Registre em `docs/decisions/` qualquer regra nova que você adotou ou dispensou.

## Regras que costumam mudar

- Limites de tamanho do `SKILL.md` e da skill.
- Formato do frontmatter aceito por quem carrega a skill.
- Destinos de instalação suportados.

Quando uma regra do template não servir ao seu contexto, não a apague em
silêncio: registre a decisão e ajuste a verificação correspondente.
