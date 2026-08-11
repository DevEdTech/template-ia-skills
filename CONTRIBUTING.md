# Contribuindo com o template

Estas regras valem para quem melhora o próprio template de skills. Para usar o
template em um projeto, veja o [README](README.md).

## Fluxo de trabalho

1. Crie uma branch a partir da principal: `git checkout -b tipo/descricao-curta` (ex.: `feat/skill-revisar-contrato`).
2. Faça as alterações em commits pequenos e com mensagem clara.
3. Rode a validação completa antes de abrir o Pull Request:

```bash
python scripts/dev.py validate
```

4. Abra o Pull Request descrevendo o que mudou e por quê.
5. Aguarde o CI: ele repete o `validate` em Python 3.13, no Linux e no Windows,
   e roda auditoria de dependências e varredura de segredos.
6. Aguarde a revisão e ajuste conforme os comentários.

Para receber o mesmo retorno antes do commit, instale os hooks uma vez:

```bash
uv run pre-commit install
```

## Contribuindo com uma skill

- Skill nova começa por uma especificação aprovada (`plan-skill`) ou por um
  inventário de importação (`import-workflow`).
- Use `python scripts/dev.py new-skill` para o esqueleto: ele já nasce válido.
- `name` e `description` seguem [docs/skill-metadata.md](docs/skill-metadata.md).
- Toda skill precisa de `evals/<nome>.json` com gatilhos positivos, um negativo e
  um cenário de execução.
- Todo script de skill precisa de teste em `tests/skills/`.
- Toda skill entra no catálogo em [docs/agents.md](docs/agents.md).

## Contribuindo com uma regra de verificação

Regras novas em `scripts/check_skills.py` mudam o que é aceito no repositório
inteiro. Antes de adicionar uma:

1. Mostre o problema real que a regra teria evitado.
2. Garanta que a regra é objetiva (passa ou não passa, sem julgamento).
3. Escreva o teste que reprova e o teste que aprova.
4. Documente a regra em `docs/architecture.md` ou `docs/skill-metadata.md`.
5. Registre um ADR quando a regra mudar como as skills são organizadas ou distribuídas.

## Convenção de commits

- `feat:` skill nova ou capacidade nova do template
- `fix:` correção de bug
- `docs:` documentação
- `test:` testes
- `refactor:` melhoria interna sem mudança de comportamento
- `chore:` tarefas de manutenção (configs, dependências)

Exemplos:

```
feat: adiciona skill revisar-contrato
fix: corrige detecção de arquivo órfão em check_skills
docs: explica os destinos de instalação
```

## Documentação e ADRs

Toda mudança de estrutura ou de regra do template atualiza a documentação
afetada em `docs/`. Decisões relevantes viram um ADR em `docs/decisions/`,
seguindo o formato do [0001](docs/decisions/0001-skill-como-unidade-de-entrega.md).

## Política de dependências

O template mantém **zero dependências de runtime**: os scripts das skills usam
apenas a biblioteca padrão, porque rodam no ambiente de quem instalou a skill.
Dependência de terceiros em uma skill exige `skills/<nome>/requirements.txt`,
justificativa no Pull Request e ADR quando virar padrão.

As dependências de desenvolvimento (ruff, mypy, pytest, pre-commit) ficam no
grupo `dev` do `pyproject.toml` e espelhadas em `requirements-dev.txt`. Ao
alterá-las, rode `python scripts/dev.py audit` e versione o `uv.lock`.

## Qualidade de código

- Type hints em todo código novo; mypy estrito precisa passar.
- Ruff cuida de formatação e lint — rode `python scripts/dev.py format` e `lint`.
- Docstrings em módulos e funções públicas.
- Código portável entre Windows, macOS e Linux (use `pathlib`, evite shell).
