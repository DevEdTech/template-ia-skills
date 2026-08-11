# Testes

Uma skill tem dois tipos de prova, e eles não se substituem: **testes
automatizados** garantem que os scripts fazem o que prometem; **avaliações**
garantem que a skill dispara e é executada como esperado por um agente.

## Testes automatizados (pytest)

### O que é testado

- Scripts das skills (`skills/<nome>/scripts/*.py`) — o coração determinístico.
- Ferramentas do template (`scripts/*.py`) — verificações, gerador, empacotamento.

### Localização

```
tests/
├── conftest.py                  # carrega scripts de skill por caminho
├── test_check_skills.py         # regras de metadados e estrutura
├── test_check_evals.py
├── test_check_docs.py
├── test_new_skill.py
├── test_package_skills.py
├── test_setup_project.py
├── test_dev_runner.py
├── test_toolchain.py
└── skills/
    └── test_summarize_csv.py    # um arquivo por script de skill
```

### Como importar um script de skill

As pastas de skill não são pacotes Python (o nome tem hífen, e a skill precisa
ser distribuível). A fixture `skill_script` carrega o módulo pelo caminho:

```python
def test_resume_colunas(skill_script) -> None:
    module = skill_script("summarize-csv", "summarize_csv.py")

    assert module.parse_number("1.234,56") == 1234.56
```

### O que cobrir em cada script

- **Sucesso**: entrada típica produz a saída esperada.
- **Entrada inválida**: arquivo inexistente, formato errado, argumento fora do domínio.
- **Caso vazio**: arquivo sem linhas, coluna sem valores, lista vazia.
- **Contrato de CLI**: `main()` devolve 0 no sucesso e diferente de 0 na falha,
  escrevendo o erro em `stderr`.

Teste o **resultado observável** — arquivo gerado, valor devolvido, código de
saída. Não teste nomes de variáveis nem a ordem interna das chamadas.

### Cobertura

O `validate` roda o pytest com `--cov` e **falha abaixo de 80%**, medindo
`scripts/` e `skills/`. O limite é um piso, não uma meta: cobertura alta com
testes de estado interno é pior do que cobertura menor com testes de comportamento.

### Comandos

```bash
python scripts/dev.py test
python scripts/dev.py test-cov
python scripts/dev.py test -k summarize -v
```

## Avaliações (o que o pytest não alcança)

Nenhum teste unitário responde "o agente vai usar esta skill quando o usuário
pedir X?". Isso é medido com os cenários de `evals/<skill>.json`:

```bash
python scripts/dev.py check-evals              # valida os cenários
python scripts/dev.py eval-sheet summarize-csv # imprime a folha para executar
```

A execução é feita pela skill `evaluate-skill`, em sessões limpas:

- **Gatilho**: cole o prompt sem citar a skill pelo nome e registre qual skill foi
  carregada. Casos negativos importam tanto quanto positivos.
- **Execução**: deixe o agente trabalhar sozinho e confronte o resultado com
  `expect` e `red_flags`.
- **Repetição**: três execuções por caso; a variação entre elas é o dado mais útil.

Os resultados ficam em `docs/evaluations/<skill>-<data>.md`. Os critérios de
qualidade por skill estão em `docs/skills-evaluation.md`.

## Smoke dos pacotes

`python scripts/dev.py smoke-bundles` extrai cada `.zip` de `dist/` em um
diretório temporário, revalida a skill fora do repositório e roda cada script
com `python -I <script> --help`. É a prova de que a skill funciona na máquina de
quem a instalou — um `--help` que só passa aqui dentro reprova nessa etapa.

## Investigar falhas

1. Leia a mensagem e reproduza o menor caso.
2. Rode o teste específico com `-k` e `-v`.
3. Em falha de `check-skills`, o texto do erro nomeia a regra e o arquivo.
4. Atualize o teste somente quando o comportamento mudou de propósito; caso
   contrário, corrija o código.
