# skills-project-template

Template de repositório para **criar, validar, avaliar, empacotar e distribuir
skills de agentes de IA**. Vem com a anatomia de skill definida, verificações
executáveis de metadados e estrutura, gerador de esqueleto, cenários de
avaliação, empacotamento determinístico e um conjunto de skills que conduzem
todo o ciclo — do planejamento à entrega.

## Objetivo

Dar um ponto de partida seguro para times que querem transformar processos
repetitivos em skills completas: com scripts Python, assets, referências
carregadas sob demanda e fluxos de trabalho de várias etapas. Você descreve o
processo, o agente constrói a skill seguindo as regras deste template, e você
valida com um único comando.

## Quando usar

- Skills de domínio para o time (relatórios, conferências, revisões, publicações).
- Conversão de prompts longos e runbooks em skills versionadas e testáveis.
- Skills com passos determinísticos que precisam de script Python.
- Skills que preenchem documentos a partir de modelos.
- Distribuição de skills para outros repositórios, times ou produtos.

## Quando NÃO usar

- Desenvolvimento de uma aplicação Python (use um template de aplicação).
- Skills que dependem de infraestrutura interna indisponível no destino.
- Conteúdo que é documentação para pessoas, não instrução para agente.

## Pré-requisitos

- Python 3.13 (a mesma versão em `.python-version`, no `requires-python` e no CI)
- [uv](https://docs.astral.sh/uv/) (recomendado) — ou `pip` + `venv` como alternativa
- git
- Um agente de código (ex.: Claude Code)

## Criar um projeto a partir do template

```bash
uv sync                        # cria o .venv e instala as ferramentas
python scripts/setup_project.py --dry-run
python scripts/setup_project.py --name="skills-financeiro" \
    --display-name="Skills Financeiro" \
    --description="Skills do time financeiro." \
    --repository="https://github.com/org/skills-financeiro" \
    --remove-example --reset-tasks
```

Com `pip`, em vez de `uv sync`:

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements-dev.txt
```

O `setup_project.py` é transacional (falha restaura o estado anterior) e
idempotente. `--remove-example` remove a skill de demonstração `summarize-csv`,
seus testes e seus cenários.

## Prompts iniciais (copie, preencha e cole no agente)

**Cenário A — "Tenho um processo repetitivo e quero virar skill"**

```text
Use a skill plan-skill para me ajudar a definir uma skill que [descreva o processo].
Quero aprovar a especificação antes de qualquer arquivo ser criado.
```

**Cenário B — "O processo já está escrito em algum lugar"**

```text
Use a skill import-workflow. O processo está em [arquivo/prompt/documento].
Converta em uma skill deste repositório.
```

**Cenário C — "A especificação foi aprovada, implemente"**

```text
Use a skill create-skill para implementar a especificação aprovada em docs/skills/[nome].md.
Garanta que `python scripts/dev.py validate` passe limpo.
```

**Cenário D — "Quero saber se a skill funciona de verdade"**

```text
Use a skill evaluate-skill na skill [nome] e me mostre o placar de gatilho e execução.
```

## Anatomia de uma skill

```
skills/summarize-csv/
├── SKILL.md          # frontmatter (name, description) + processo executável
├── scripts/          # passos determinísticos, em Python (stdlib)
├── assets/           # modelos que a skill preenche
└── reference/        # conhecimento carregado sob demanda
```

Regras completas em [docs/architecture.md](docs/architecture.md) e
[docs/skill-metadata.md](docs/skill-metadata.md).

## Validação

Antes de considerar qualquer alteração pronta:

```bash
python scripts/dev.py validate
```

O comando executa, em sequência: sincronização das skills, verificação de
metadados e estrutura, verificação dos cenários de avaliação, verificação da
documentação, formatação, lint, checagem de tipos, testes com cobertura mínima,
empacotamento e smoke dos pacotes fora do repositório. Funciona **offline** e
vale para um clone recém-feito.

### Verificação automática

O GitHub Actions repete o `validate` a cada push e Pull Request, em **Python
3.13**, no **Linux e no Windows**. Um workflow separado audita as dependências
(`pip-audit` sobre o `uv.lock`) e varre o histórico em busca de segredos
(`gitleaks`), também semanalmente. Ao publicar uma GitHub Release, o workflow
`Release` valida e anexa cada `dist/<skill>.zip` e o `dist/manifest.json` à release.

Localmente, instale os hooks:

```bash
uv run pre-commit install
```

A auditoria depende de rede e fica fora do `validate`:

```bash
python scripts/dev.py audit
```

## Comandos

| Comando                                    | O que faz                                                      |
| ------------------------------------------ | -------------------------------------------------------------- |
| `python scripts/dev.py new-skill --name x` | Cria o esqueleto de uma skill nova (com `--with scripts,assets,reference`) |
| `python scripts/dev.py sync-skills`        | Sincroniza as skills para `.claude/skills` e `.agents/skills`   |
| `python scripts/dev.py check-skills`       | Valida metadados, estrutura, links, órfãos e cópias             |
| `python scripts/dev.py check-evals`        | Valida os cenários de avaliação de cada skill                   |
| `python scripts/dev.py check-docs`         | Valida links, tarefas e o catálogo de skills                    |
| `python scripts/dev.py eval-sheet`         | Imprime a folha de avaliação para rodar com um agente           |
| `python scripts/dev.py package`            | Empacota cada skill em um `.zip` determinístico com manifesto   |
| `python scripts/dev.py smoke-bundles`      | Extrai os pacotes e prova que funcionam fora do repositório     |
| `python scripts/dev.py format`             | Formata o código com Ruff                                       |
| `python scripts/dev.py lint`               | Verifica problemas de código com Ruff                           |
| `python scripts/dev.py typecheck`          | Verifica os tipos com mypy (modo estrito)                       |
| `python scripts/dev.py test`               | Roda os testes com pytest                                       |
| `python scripts/dev.py test-cov`           | Roda os testes medindo cobertura                                |
| `python scripts/dev.py check-workflows`    | Valida os workflows do GitHub Actions (actionlint)              |
| `python scripts/dev.py audit`              | Audita as dependências em busca de vulnerabilidades             |
| `python scripts/dev.py validate`           | Roda tudo: skills, docs, qualidade, testes e pacotes            |

> **Atalho Unix (opcional):** no macOS e Linux há um `Makefile` — `make validate`,
> `make test`, etc. No Windows, use `python scripts/dev.py <tarefa>`, que funciona
> em qualquer sistema.

## Ciclo de trabalho

```
plan-skill → create-skill → evaluate-skill → review-skill → package-skill
                  ↑                              |
                  └────────── refactor-skill ────┘
```

`import-workflow` entra antes de `create-skill` quando o processo já existe fora
do repositório; `document-skills` fecha qualquer mudança no conjunto de skills.
Detalhes em [docs/development-process.md](docs/development-process.md) e no
catálogo em [docs/agents.md](docs/agents.md).

## Distribuição

`python scripts/dev.py package` gera `dist/<skill>.zip` (determinístico, com
`sha256` no `dist/manifest.json`) e `smoke-bundles` prova que a skill funciona
fora daqui. Ao publicar uma GitHub Release, esses arquivos são gerados a partir
da tag e anexados automaticamente à release. Destinos e checklist de entrega em
[docs/packaging.md](docs/packaging.md).

## Estrutura resumida

```
skills/          # skills canônicas — o produto deste repositório
evals/           # cenários de gatilho e execução, um JSON por skill
scripts/         # runner e verificações do template
tests/           # testes das ferramentas e dos scripts das skills
docs/            # arquitetura, metadados, processo, testes, empacotamento, ADRs
dist/            # pacotes gerados (ignorado pelo Git)
```

## Limitações conhecidas

- As verificações de metadados são objetivas e, por isso, aproximadas: elas
  garantem o mínimo, não a qualidade da descrição. A avaliação com agente
  continua necessária.
- O `validate` não executa os cenários de avaliação (isso exige rede e um
  agente); ele garante que existem e estão completos.
- Skills com dependências de terceiros não têm os scripts executados no smoke.
- O formato de instalação varia entre agentes e versões de API; confirme o
  destino antes de prometer prazo.
