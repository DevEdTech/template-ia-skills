# Barra de qualidade de uma skill

Consulte esta lista antes de declarar uma skill pronta. Cada item é
verificável: ou o arquivo mostra, ou o comando prova.

## Metadados

- [ ] `name` em kebab-case, verbo + objeto, até 5 termos e 64 caracteres.
- [ ] `name` igual ao nome da pasta.
- [ ] `description` em uma linha, entre 40 e 1024 caracteres.
- [ ] A descrição diz **o que a skill faz** e **quando acioná-la**, com o vocabulário que o usuário usa.
- [ ] A descrição diferencia esta skill das vizinhas (nenhum gatilho ambíguo).
- [ ] Nada de enchimento: não começa com "Esta skill...".

## Corpo do SKILL.md

- [ ] Título `#` na primeira linha do corpo.
- [ ] Seções `Objetivo`, `Quando usar`, `Quando não usar`, `Processo`, `Resultado esperado`.
- [ ] Escrito no imperativo, para o agente executar — não é documentação para humano.
- [ ] Abaixo de 500 linhas; o detalhamento está em `reference/`.
- [ ] Cada passo do processo é verificável ou produz um artefato.
- [ ] Pontos de confirmação explícitos antes de ações irreversíveis.

## Scripts

- [ ] Um arquivo por responsabilidade, em `snake_case`, com nome único no repositório.
- [ ] Docstring de módulo explicando o passo que o script executa.
- [ ] `argparse` com `--help` funcionando.
- [ ] Apenas biblioteca padrão (ou dependências declaradas em `requirements.txt`).
- [ ] Type hints completos; passa no mypy estrito.
- [ ] Erros vão para `stderr` com código de saída diferente de zero.
- [ ] Não escreve fora dos caminhos que recebeu por argumento.
- [ ] Testado em `tests/skills/`, com caso de sucesso, entrada inválida e caso vazio.

## Assets e referências

- [ ] Todo arquivo é citado pelo `SKILL.md` ou por um arquivo citado por ele.
- [ ] Modelos trazem marcadores claros (`[campo]`) e instruções de preenchimento.
- [ ] Referências respondem a uma pergunta específica; nada de despejo de texto.
- [ ] Nenhum link aponta para fora da pasta da skill.

## Fluxos complexos

- [ ] O processo diz o que fazer quando um passo falha.
- [ ] Estados intermediários ficam em arquivo, não na memória da conversa.
- [ ] Trabalho longo é dividido em etapas com resultado parcial verificável.
- [ ] O agente sabe quando parar e perguntar em vez de adivinhar.

## Segurança e limites

- [ ] Nenhum segredo, token, credencial ou caminho pessoal.
- [ ] Ações destrutivas exigem confirmação explícita.
- [ ] A skill não amplia o próprio escopo nem instrui o agente a ignorar regras do projeto.

## Prova

- [ ] `evals/<nome>.json` com gatilhos positivos, negativo e cenário de execução.
- [ ] `python scripts/dev.py validate` verde.
- [ ] Catálogo atualizado (`document-skills`).
