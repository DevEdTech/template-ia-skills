---
name: update-readme
description: Reescreve o README.md inteiro na estrutura padrão do repositório — objetivo, pré-requisitos, instalação, validação, comandos, anatomia de skill e fluxo de trabalho. Use depois do setup_project, quando o README ainda descreve o template, ou quando ele perdeu a estrutura; para sincronizar o catálogo de skills, use document-skills.
---

# Atualizar README

## Objetivo

Manter o `README.md` como a porta de entrada do repositório: profissional,
padronizado e fiel ao que ele realmente entrega.

## Quando usar

- Depois do `setup_project.py`, quando o README ainda descreve o template em
  vez do repositório de skills do time.
- Quando comandos, pré-requisitos, anatomia de skill ou fluxo de trabalho
  mudaram.
- Quando o README cresceu sem ordem, ficou incompleto ou perdeu o padrão.

## Quando não usar

- Para acrescentar, renomear ou remover a entrada de uma skill no catálogo e
  nas menções por nome: isso é `document-skills`. Esta skill cuida da
  estrutura do README inteiro, não do conjunto de skills.
- Para registrar a evidência de uma entrega: use `document-delivery`.
- Para revisar uma skill: use `review-skill`.

## Levante os fatos antes de escrever

Não descreva o repositório de memória nem a partir do que o template dizia.
Leia o repositório:

| Fonte                        | O que extrair                            |
| ---------------------------- | ---------------------------------------- |
| `pyproject.toml`             | Nome, descrição, versão mínima do Python |
| `scripts/dev.py` (`TASKS`)   | A tabela de comandos                     |
| `.python-version`            | Versão do Python nos pré-requisitos      |
| `skills/`                    | Skills existentes e a anatomia real      |
| `docs/agents.md`             | Catálogo de skills e fluxo de trabalho   |
| `docs/architecture.md`       | Estrutura de pastas                      |
| `docs/packaging.md`          | Empacotamento e distribuição             |
| `.github/workflows`          | Verificação automática e release         |

## Estrutura padrão

Siga a ordem de [assets/readme-outline.md](assets/readme-outline.md). Omita a
seção que não se aplica; não invente seção nova sem necessidade.

1. Título e um parágrafo dizendo o que o repositório entrega.
2. Objetivo.
3. Quando usar / Quando NÃO usar.
4. Pré-requisitos.
5. Criar um projeto a partir do template (só enquanto for template).
6. Prompts iniciais por cenário.
7. Anatomia de uma skill.
8. Validação.
9. Comandos (tabela).
10. Fluxo de trabalho das skills.
11. Estrutura de pastas.
12. Distribuição.
13. Limitações conhecidas.

## Estilo

- Português do Brasil, tom direto, segunda pessoa. Frases curtas.
- Sem emoji, sem badge decorativo, sem superlativo de marketing.
- Cada comando em bloco ` ```bash `, um comando por linha.
- Listas de comandos em tabela, com a coluna "O que faz" no infinitivo.
- Caminho, arquivo e comando sempre em `crase`.
- Link relativo para os arquivos do repositório.
- Explique também o "porquê" quando a regra não for óbvia, como faz o
  restante da documentação.

## Processo

1. Levante os fatos das fontes acima.
2. Compare com o README atual e preserve o que já estiver correto e
   específico do repositório; reescrever não é recomeçar do zero.
3. Remova o que só valia para o template — "Criar um projeto a partir do
   template" e qualquer menção a `skills-project-template` — quando o
   repositório já passou pelo setup.
4. Escreva as seções na ordem padrão.
5. Cite somente tarefa que existe no registro `TASKS` de `scripts/dev.py` e
   link que aponta para arquivo existente: `python scripts/dev.py check-docs`
   reprova o contrário.
6. Ao citar skills por nome, mantenha o texto igual ao catálogo de
   `docs/agents.md`. Se o conjunto de skills mudou, é `document-skills` que
   atualiza o catálogo — não invente entrada aqui.
7. Registre as limitações reais. Não prometa o que não existe.
8. Rode `python scripts/dev.py check-docs`.

## Resultado esperado

- `README.md` na estrutura padrão, refletindo o repositório atual.
- Lista das seções adicionadas, reescritas e removidas.
- Resultado de `python scripts/dev.py check-docs`.
- Pontos que ficaram em aberto por falta de informação no repositório.
