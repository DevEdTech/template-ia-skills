---
name: create-skill
description: Escreve uma skill completa a partir da especificação aprovada — SKILL.md, scripts Python, assets, referências e cenários de avaliação — e deixa o validate verde. Use quando a especificação estiver aprovada e for hora de gerar os arquivos.
---

# Criar skill

## Objetivo

Transformar uma especificação aprovada em uma skill que passa em
`python scripts/dev.py validate` e funciona fora deste repositório.

## Quando usar

- Depois de `plan-skill`, com a especificação em `docs/skills/<nome>.md` aprovada.
- Depois de `import-workflow`, com o inventário aprovado.

## Quando não usar

- Sem especificação aprovada: volte para `plan-skill`.
- Para mexer em skill existente: use `refactor-skill`.

## Processo

1. Leia a especificação aprovada, o `AGENTS.md` e `docs/skill-metadata.md`.
2. Gere o esqueleto: `python scripts/dev.py new-skill --name <nome> --with scripts,assets,reference`
   (inclua só as partes que a especificação pediu).
3. Escreva o frontmatter definitivo:
   - `name` igual ao nome da pasta, kebab-case, verbo + objeto, até 5 termos;
   - `description` em uma linha, com o que a skill faz e as situações que a disparam.
4. Escreva o corpo do `SKILL.md` no imperativo, para o agente: `Objetivo`,
   `Quando usar`, `Quando não usar`, `Processo`, `Resultado esperado`.
5. Mantenha o `SKILL.md` abaixo de 500 linhas. Detalhe extenso vai para
   `reference/` e é citado no passo que precisa dele.
6. Implemente em `scripts/` cada passo determinístico da especificação:
   um arquivo por responsabilidade, `snake_case`, nome único no repositório,
   docstring de módulo, `argparse` com `--help` e apenas biblioteca padrão.
7. Coloque em `assets/` os modelos e dados que a skill preenche ou copia.
8. Cite no `SKILL.md` todos os arquivos criados — arquivo não citado é arquivo morto e reprova na verificação.
9. Preencha `evals/<nome>.json`: pelo menos dois gatilhos positivos, um negativo
   e um cenário de execução com resultados esperados e sinais de alerta.
10. Escreva os testes dos scripts em `tests/skills/test_<script>.py`, cobrindo
    sucesso, entrada inválida e caso vazio.
11. Rode `python scripts/dev.py validate` até ficar verde.
12. Atualize o catálogo com `document-skills`.

Consulte [reference/quality-bar.md](reference/quality-bar.md) antes de declarar a skill pronta.

## Regras invioláveis

- A skill precisa ser autocontida: nada de importar módulos deste repositório
  nem depender de caminhos fora da própria pasta.
- Dependência de terceiros só com `requirements.txt` na pasta da skill e
  justificativa no pull request; o padrão é stdlib.
- Nenhum segredo, credencial, token ou caminho pessoal nos arquivos da skill.
- Nada de instrução que amplie o escopo do agente ("faça também...", "se sobrar tempo...").

## Resultado esperado

- Lista dos arquivos criados.
- Resumo do que a skill faz e de quando ela dispara.
- Saída de `python scripts/dev.py validate`.
- Limitações conhecidas e próximo passo (`evaluate-skill`).
