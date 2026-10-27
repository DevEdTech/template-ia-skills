# Limites com dispensa, heurística como aviso e validate com flags

- **Data**: 2026-10-26
- **Branch**: `main` (commits `fdd5208`, `2f5b898` e `a82e2e8`)
- **Plano de origem**: revisão crítica dos três templates, aprovada na conversa
- **Jira**: PD-912, PD-913, PD-914

## Objetivo

Parar de reprovar por regras que não sustentam o julgamento — heurística de
redação e limites de tamanho sem válvula —, sem afrouxar o que de fato protege
a skill.

## Funcionalidades entregues

- **Heurística avisa, não reprova** — as verificações de redação da
  `description` (marcador de acionamento e prefixo de enchimento) aparecem no
  relatório sem derrubar o comando. Eram varredura de substring: reprovavam
  descrição boa sem as palavras esperadas e aprovavam descrição ruim que as
  continha.
- **Limites com dispensa justificada** — a skill declara em
  `metadata.waivers` o limite que precisa dispensar, com o motivo, e ele
  aparece no relatório ao lado do achado. Antes, um fluxo de trabalho
  legitimamente longo só tinha duas saídas: quebrar a skill ou burlar o
  número.
- **Dispensa verificada** — só vale para regra dispensável e com motivo
  escrito. Dispensar regra essencial, dispensar sem motivo e declarar dispensa
  que nunca foi acionada são erros: o frontmatter não pode mentir sobre a
  skill.
- **Teste junto da skill** — `tests/` passou a ser entrada prevista na raiz e
  fica fora do pacote distribuído. Resolve a contradição de skill
  "autocontida" cujos testes não viajavam com ela.
- **Perfil de rigor** — `prototipo` bloqueia só o essencial, `padrao` mantém o
  comportamento atual, e `rigoroso` — o perfil de quem publica para a máquina
  de outra pessoa — trata aviso e dispensa como falha.
- **Validação sob medida** — `python scripts/dev.py validate --skill <nome>`
  roda a verificação, o eval, o teste, o lint e o pacote daquela skill.
  `--changed`, `--quick`, `--only`, `--skip`, `--strict`, `--no-bail`,
  `--list` e `show-profile` completam o conjunto.
- **Conferência do lockfile** — `check-lockfile` pega a divergência entre
  `pyproject.toml` e `uv.lock` antes de empurrar.

## Critérios de aceite

- [x] Descrição sem marcador de acionamento avisa e não reprova.
- [x] Dispensa justificada rebaixa o limite a aviso, com o motivo no relatório.
- [x] Dispensa sem motivo não vale, e o limite continua reprovando.
- [x] Regra essencial recusa dispensa, com erro próprio.
- [x] Dispensa declarada sem a regra ter sido acionada é apontada.
- [x] `tests/` na raiz da skill não vira entrada não prevista nem arquivo órfão.
- [x] `tests/` não entra no pacote distribuído.
- [x] Perfil `rigoroso` trata aviso e dispensa como falha.
- [x] `--skill` restringe verificação, eval, teste, lint e pacote.
- [x] Execução parcial não aplica cobertura global.
- [x] O empacotamento não é cancelado por aviso, só por erro.

## Arquivos alterados

| Arquivo                       | Mudança                                                           |
| ----------------------------- | ----------------------------------------------------------------- |
| `scripts/check_skills.py`     | Achados com regra e severidade, parser e aplicação de dispensas, `tests/` permitida, `is_packaged`. |
| `scripts/project_config.py`   | Catálogo de suítes, perfis e cobertura.                           |
| `scripts/validate.py`         | Orquestrador do `validate`, com as flags e o escopo por skill.    |
| `scripts/check_lockfile.py`   | Confere o `uv.lock` contra o `pyproject.toml`.                    |
| `scripts/package_skills.py`   | Só erro cancela o empacotamento; `tests/` fora do pacote.         |
| `scripts/smoke_bundles.py`    | Filtra achados por severidade.                                    |
| `scripts/dev.py`              | Delega o `validate`; tarefas `show-profile` e `check-lockfile`.   |
| `pyproject.toml`              | `fail_under` deixa de ser o valor efetivo; pisos elevados.        |
| `AGENTS.md`, `CLAUDE.md`, `README.md` | Perfil, limites, dispensas e as flags.                    |
| `docs/architecture.md`        | `tests/` no layout e a distinção entre erro e aviso.              |
| `docs/decisions/0005-limites-com-dispensa.md` | ADR da decisão.                                   |
| `.github/workflows/ci.yml`    | Matriz passa a cobrir Python 3.13 e 3.14.                         |
| `uv.lock`                     | Regenerado após os pisos subirem.                                 |

Volume: 25 arquivos no commit da feature (1643 inserções, 449 remoções) e 7 no
commit da correção.

## Testes

| Teste                          | Tipo     | O que cobre                                                                 |
| ------------------------------ | -------- | --------------------------------------------------------------------------- |
| `tests/test_check_skills.py`   | contrato | Parser do bloco `waivers`; dispensa justificada rebaixando a aviso; dispensa sem motivo; regra essencial recusando dispensa; dispensa ociosa; `tests/` não virando órfã; heurísticas como aviso. |
| `tests/test_validate.py`       | contrato | `skills_in` por pasta e por eval; cobertura por skill; níveis por perfil; capacidade desligada; `rigoroso` tratando aviso como falha; skill inexistente; cada flag. |
| `tests/test_check_lockfile.py` | contrato | Lockfile ausente, `uv` ausente, em dia, divergência, e outra falha do `uv` **não** virando divergência. |
| `tests/test_dev_runner.py`     | contrato | Toda tarefa monta um comando; `validate` continua no runner.                |

Saída da suíte:

```text
TOTAL                        1473    311    606     54    78%
Required test coverage of 70% reached. Total coverage: 77.83%
============================= 129 passed in 0.75s ==============================
```

## Validações executadas

| Comando                              | Resultado |
| ------------------------------------ | --------- |
| `python scripts/dev.py validate`     | Verde     |
| CI (4 jobs da matriz + pre-commit)   | Verde     |
| CI (Security)                        | Verde     |

```text
$ python scripts/dev.py validate
Perfil padrao: 11 suite(s) — sync-skills, check-skills, check-evals,
check-docs, check-lockfile, format-check, lint, typecheck, test, package,
smoke-bundles
Verificação de skills OK: 12 skill(s) validada(s) e sincronizada(s).
Validação das avaliações OK: 12 skill(s) com cenários.
Validação da documentação OK.
uv.lock em dia com o pyproject.toml.
All checks passed!
Smoke dos pacotes OK: 12 pacote(s) válidos fora do repositório.
Validacao concluida.
```

CI, em `a82e2e8`:

```text
pre-commit                            success
validate (ubuntu-latest, py3.13)      success
validate (ubuntu-latest, py3.14)      success
validate (windows-latest, py3.13)     success
validate (windows-latest, py3.14)     success
```

## Fora do escopo

- Rodar o smoke de skills com dependência de terceiros: a instalação passa a
  ser responsabilidade do destino, e o smoke continua pulando esses pacotes.
- Extrair as skills compartilhadas pelos três templates para uma fonte única:
  a divergência entre as cópias foi levantada na revisão e continua aberta.
- Tornar o `audit` parte do `validate`: depende de rede.

## Limitações e pendências conhecidas

- O parser de `metadata.waivers` é deliberadamente estreito: um bloco
  `waivers:` dentro de `metadata:`, com uma linha `regra: motivo` por
  dispensa. Sem libs externas, como o resto do repositório.
- O motivo da dispensa é verificado pelo tamanho (30 caracteres), não pelo
  conteúdo. Cabe à revisão julgar se ele diz algo — o valor aparece no
  relatório justamente para isso.
- `check-lockfile` depende do `uv`. Sem ele, avisa e não reprova.

## Como verificar manualmente

1. `python scripts/dev.py show-profile` — mostra o perfil e o que bloqueia.
2. `python scripts/dev.py validate --skill summarize-csv --dry-run` — mostra
   a skill afetada, o teste que a cobre e o empacotamento restrito a ela.
3. Acrescente 600 linhas ao corpo de uma skill: `check-skills` reprova por
   `body-lines`. Declare a dispensa com motivo em `metadata.waivers` e ela
   passa, com o motivo no relatório. Encurte o motivo para menos de 30
   caracteres e volta a reprovar.
4. `python scripts/dev.py validate --strict --only check-skills` — no perfil
   rigoroso, aviso e dispensa passam a reprovar.
