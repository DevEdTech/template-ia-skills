# Processo de desenvolvimento

Fluxo recomendado para levar uma ideia até uma skill distribuível.

## Fluxo

1. **Descoberta**: se a ideia ainda está vaga, use `plan-skill`. Responda às
   perguntas até aprovar a especificação em `docs/skills/<nome>.md`.
   Se o processo já existe escrito, comece por `import-workflow`.
2. **Esqueleto**: `python scripts/dev.py new-skill --name <nome> --with scripts,assets,reference`.
3. **Implementação**: use `create-skill`. Escreva o `SKILL.md`, os scripts, os
   assets e os testes.
4. **Cenários**: preencha `evals/<nome>.json` com gatilhos positivos, negativos e
   um cenário de execução.
5. **Validação local**: `python scripts/dev.py validate` até ficar tudo verde.
6. **Avaliação**: `evaluate-skill` — rode os cenários em sessões limpas e registre
   o placar em `docs/evaluations/`.
7. **Revisão**: `review-skill` — achados priorizados; corrija com `refactor-skill`.
8. **Documentação**: `document-skills` — catálogo, README e ADR quando couber.
9. **Branch e commit**: `git checkout -b feat/<nome-da-skill>`, um incremento por commit.
10. **Pull Request**: descreva o que a skill faz, quando dispara e o placar da avaliação.
11. **Verificação automática**: aguarde o CI, que repete o `validate` no Linux e no Windows.
12. **Distribuição**: `package-skill` quando a skill for para outro projeto ou time.

## Ambiente

- Crie o ambiente com `uv sync` (recomendado) ou `python -m venv .venv` + `pip install -r requirements-dev.txt`.
- A versão do Python recomendada está em `.python-version`.
- O `uv.lock` deve ser versionado para builds reproduzíveis.
- Instale os hooks com `uv run pre-commit install` para antecipar o retorno do CI.

## Verificação automática

Dois workflows rodam no GitHub Actions:

| Workflow   | Quando                           | O que faz                                                    |
| ---------- | -------------------------------- | ------------------------------------------------------------ |
| `ci`       | push, Pull Request               | `validate` em Python 3.13 × Linux/Windows, e `pre-commit`     |
| `security` | push, Pull Request, semanalmente | `pip-audit` sobre o `uv.lock` e `gitleaks` sobre o histórico   |

O `validate` é a porta local e permanece **offline**. Duas verificações dependem
de rede e por isso ficam fora dele:

- `python scripts/dev.py audit` — vulnerabilidades nas dependências de desenvolvimento.
- `python scripts/dev.py check-workflows` — validade dos workflows do GitHub Actions.

A segunda roda automaticamente no pre-commit quando você toca em
`.github/workflows/`. Ela precisa acontecer **antes do push**: um workflow
inválido não falha no CI, ele simplesmente não chega a iniciar.

## O que o `validate` roda, na ordem

1. `sync-skills` — regenera as cópias lidas pelo agente.
2. `check-skills` — metadados, estrutura, links, órfãos, scripts e sincronização.
3. `check-evals` — cenários de gatilho e execução de cada skill.
4. `check-docs` — links, tarefas citadas e catálogo.
5. `ruff format --check` e `ruff check` — formatação e lint.
6. `mypy` — tipos em modo estrito, inclusive nos scripts das skills.
7. `pytest --cov` — testes com cobertura mínima de 80%.
8. `package` — empacota cada skill em `dist/`.
9. `smoke-bundles` — extrai os pacotes e prova que funcionam fora do repositório.

## Proteções recomendadas no GitHub

Depois de criar um repositório a partir do template:

1. Em **Settings > Rules > Rulesets**, proteja a branch padrão.
2. Exija pull request, ao menos uma aprovação e resolução das conversas.
3. Exija os checks dos workflows `CI` e `Security` antes do merge.
4. Impeça force push e exclusão da branch padrão.
5. Em **Settings > Security**, habilite dependency graph, Dependabot alerts,
   Dependabot security updates e private vulnerability reporting.

## Mensagens de commit

```
feat: adiciona skill revisar-contrato
fix: corrige gatilho da skill summarize-csv
docs: documenta destinos de instalação
test: cobre entrada vazia no summarize_csv
```

Outros prefixos úteis: `refactor:`, `chore:`.

## Definição de concluído

- Os critérios de aceite da especificação foram atendidos.
- `python scripts/dev.py validate` está verde.
- A skill foi avaliada e o placar registrado.
- O catálogo e a documentação estão coerentes.
- As alterações estão registradas no Git.
