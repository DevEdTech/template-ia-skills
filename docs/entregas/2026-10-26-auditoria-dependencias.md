# Correção da auditoria de dependências

- **Data**: 2026-10-26
- **Branch**: `fix/dependency-audit-2026-10-26`
- **Especificação**: correção restrita autorizada na conversa.

## Objetivo

Eliminar os achados da [auditoria de origem](https://github.com/DevEdTech/template-ia-skills/actions/runs/40317436157), preservando os gates e o conteúdo das skills.

## Skills entregues e avaliação

Nenhuma skill alterada. Não se aplica reavaliar gatilhos ou execução por agente; a mudança limita-se às dependências das ferramentas de desenvolvimento.

## Critérios de aceite

- [x] Lock resolvido e instalação com `uv sync --locked`.
- [x] Validação completa e auditoria local sem achados.
- [x] Diff restrito às dependências afetadas e à evidência da entrega.

## Arquivos alterados

- `uv.lock`: filelock 3.32.2 → 4.2.1 e virtualenv 21.7.13 → 21.14.10. Virtualenv passa a depender de packaging, já bloqueado em 26.3 neste template.
- Este registro.

## Validações executadas

Windows, Python 3.13.14. Comandos: `uv sync --locked`, `uv run --locked python scripts/dev.py validate` e `uv run --locked python scripts/dev.py audit`; todos com código de saída 0.

```text
Required test coverage of 80.0% reached. Total coverage: 83.67%
103 passed
Smoke dos pacotes OK: 12 pacote(s) válidos fora do repositório.
No known vulnerabilities found
```

A validação também conferiu skills, cenários, documentação, formato, lint, tipos e empacotamento. Nenhum teste novo: não houve mudança de comportamento. A primeira candidata virtualenv 21.14.9 ainda apresentou CVE-2026-113713; 21.14.10 eliminou o achado na nova auditoria.

## Pacotes gerados

As 12 skills foram empacotadas em `dist/`, com manifesto, e passaram pelo smoke fora do repositório. Artefatos locais de validação, sem instalação ou publicação de release.

## Fora do escopo

Conteúdo das skills, cenários, workflows, permissões, segredos, outros repositórios e atualizações Ruff/pre-commit do PR Dependabot #8.

## Limitações e pendências conhecidas

Os resultados acima são locais. Os checks Linux/Windows, hooks e Security do PR devem passar no SHA final antes do merge. CI e Security da branch principal devem ser conferidos após o merge. A auditoria reflete o banco consultado nesta data.

## Como verificar manualmente

1. Execute `uv sync --locked`.
2. Execute `uv run --locked python scripts/dev.py validate`.
3. Execute `uv run --locked python scripts/dev.py audit`; espere ausência de vulnerabilidades conhecidas.
