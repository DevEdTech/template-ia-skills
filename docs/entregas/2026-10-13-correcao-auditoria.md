# Correção da auditoria de dependências

- **Data**: 2026-10-13
- **Branch**: `fix/ci-security-lockfile`
- **Plano de origem**: plano autorizado na conversa

## Objetivo

Restaurar o gate Security sem ignorar vulnerabilidades ou reduzir verificações.
O pip-audit apontou virtualenv 21.7.4 com os avisos PYSEC-2026-4011,
PYSEC-2026-4012, PYSEC-2026-4013 e PYSEC-2026-4014.

## Alterações e critérios de aceite

- [x] Atualizar virtualenv para 21.7.13 no uv.lock.
- [x] Atualizar python-discovery para 1.6.2, conforme exigido pela resolução.
- [x] Preservar dependências diretas, workflows, auditoria e limites de cobertura.
- [x] Validar e auditar localmente com Python 3.13.2 no Windows.
- [ ] Confirmar CI e Security no SHA publicado antes do merge.

## Testes e validações

Nenhuma skill ou cenário de avaliação foi alterado; a suíte existente foi executada.

| Comando | Resultado observado |
| --- | --- |
| `uv run --locked python scripts/dev.py validate` | Passou: skills, evals, docs, Ruff, mypy, testes, pacotes e smoke |
| `uv run --locked python scripts/dev.py audit` | Passou, sem vulnerabilidades conhecidas |

```text
Success: no issues found in 23 source files
103 passed in 9.11s
Required test coverage of 80.0% reached. Total coverage: 83.67%
Smoke dos pacotes OK: 12 pacote(s) válidos fora do repositório.
No known vulnerabilities found
```

## Limitações

Linux e os checks remotos precisam ser confirmados no PR. A publicação e o
merge não são comprovados por esta evidência local. Atualizações diretas do
Dependabot são revisadas separadamente.
