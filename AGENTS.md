# Instruções do projeto

Este repositório produz **skills para agentes de IA**. O artefato entregue não é
um aplicativo: é um conjunto de skills validadas, avaliadas e empacotadas.

## Leia primeiro

1. README.md
2. docs/architecture.md
3. docs/skill-metadata.md
4. docs/development-process.md
5. docs/testing.md
6. docs/packaging.md

## Processo obrigatório

1. Entenda a solicitação e os critérios de aceite.
2. Inspecione as skills existentes antes de propor uma nova (evite gatilho duplicado).
3. Apresente um plano para mudanças que afetam vários arquivos.
4. Mantenha as alterações dentro do escopo solicitado.
5. Atualize os cenários em `evals/` sempre que o gatilho ou o resultado mudar.
6. Execute `python scripts/dev.py validate`.
7. Revise o diff final.
8. Atualize a documentação afetada (catálogo em `docs/agents.md`).

## Anatomia de uma skill

```
skills/<nome>/
├── SKILL.md          # frontmatter + processo executável (obrigatório)
├── scripts/          # passos determinísticos, em Python
├── assets/           # modelos e arquivos que a skill preenche ou copia
├── reference/        # conhecimento carregado sob demanda
└── requirements.txt  # só quando a skill exigir dependência de terceiros
```

- Nenhuma outra entrada é permitida na raiz da skill.
- Todo arquivo precisa ser citado pelo `SKILL.md` (ou por um arquivo citado por ele).
- Toda skill é autocontida: nada de importar código deste repositório nem
  depender de caminhos fora da própria pasta.

## Nome e descrição

- `name`: kebab-case, verbo + objeto, no máximo 5 termos e 64 caracteres, igual ao nome da pasta.
- `description`: uma linha, de 40 a 1024 caracteres, dizendo **o que a skill faz** e
  **quando acioná-la**, com o vocabulário do usuário; inclua o limite ("não use quando...")
  sempre que houver skill vizinha.
- Sem enchimento: não comece com "Esta skill...".
- Regras completas e exemplos em `docs/skill-metadata.md`.

## Divulgação progressiva

- O `SKILL.md` fica abaixo de 500 linhas e contém o que é usado em **toda** execução.
- Conhecimento extenso ou ocasional vai para `reference/`, citado do passo que precisa dele.
- Modelos e formulários vão para `assets/`.
- Nada de duplicar conteúdo entre corpo e referência.

## Scripts das skills

- Um arquivo por responsabilidade, `snake_case`, com nome único no repositório.
- Docstring de módulo, `argparse` com `--help` funcionando, type hints completos.
- Somente biblioteca padrão. Dependência de terceiros exige `requirements.txt` na
  pasta da skill, justificativa no pull request e ADR quando virar padrão.
- Erros em `stderr` com código de saída diferente de zero.
- O script não escreve fora dos caminhos recebidos por argumento.
- Todo script tem teste em `tests/skills/`, cobrindo sucesso, entrada inválida e caso vazio.

## Fluxos de trabalho complexos

- Escreva o processo em passos verificáveis, cada um com resultado observável.
- Diga o que fazer quando um passo falha.
- Estado intermediário fica em arquivo, não na memória da conversa.
- Ações irreversíveis ou externas exigem confirmação explícita do usuário.
- A skill declara quando parar e devolver a decisão para a pessoa.

## Escopo

- Não expanda o escopo além do solicitado.
- Uma skill por vez.
- Skill nova sem especificação aprovada não começa: use `plan-skill`.

## Qualidade de código

- Todo código novo tem type hints e passa no mypy em modo estrito.
- Formatação e lint são feitos pelo Ruff (`python scripts/dev.py format` / `lint`).
- Prefira `pathlib` a manipulação de strings de caminho.
- Escreva código portável entre Windows, macOS e Linux.

## Segurança

- Nunca faça commit de segredos, tokens, credenciais ou dados de cliente.
- Nenhuma skill instrui o agente a contornar regras do projeto ou a agir sem confirmação.
- Pacotes em `dist/` são conteúdo que roda na máquina de outra pessoa: confira o
  manifesto antes de distribuir.

## Avaliação

- Toda skill tem `evals/<nome>.json` com gatilhos positivos, ao menos um negativo
  e um cenário de execução com resultados esperados e sinais de alerta.
- Mudou a descrição? Reavalie o gatilho.

## Documentação

- Toda skill aparece no catálogo `docs/agents.md`, em uma linha.
- Decisões relevantes sobre organização, validação ou distribuição viram um ADR
  em `docs/decisions/`.
- Mudança que cria ou revoga uma regra atualiza este `AGENTS.md`.

## Conclusão

Uma tarefa só está concluída quando critérios de aceite, verificações de skills,
avaliações, lint, typecheck, testes, cobertura, empacotamento, documentação e o
CI estiverem satisfeitos.
