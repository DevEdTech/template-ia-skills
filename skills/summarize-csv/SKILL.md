---
name: summarize-csv
description: Resume um arquivo CSV com estatísticas por coluna e escreve um relatório em Markdown a partir do modelo da skill. Use quando o pedido envolver entender, resumir, conferir ou reportar o conteúdo de um CSV ou planilha exportada; não use para transformar ou editar os dados.
---

# Resumir CSV

> Skill de demonstração do template: mostra o formato completo — script,
> asset e referência. Remova-a com `python scripts/setup_project.py --remove-example`.

## Objetivo

Produzir, a partir de um CSV, um resumo confiável por coluna (contagens, faltantes,
estatísticas numéricas, valores mais frequentes) e um relatório em Markdown
pronto para leitura humana.

## Quando usar

- "O que tem nesse CSV?", "resume essa planilha", "quantas linhas vieram no export?"
- Conferência rápida de um arquivo recebido, antes de usá-lo.
- Relatório de qualidade de dados: colunas vazias, valores faltantes, cardinalidade.

## Quando não usar

- Transformar, filtrar ou corrigir os dados: isso é trabalho de código sob medida.
- Arquivos que não são tabulares (JSON aninhado, XML, PDF).

## Processo

1. Confirme o caminho do arquivo com o usuário. Não adivinhe qual CSV é.
2. Rode o script da skill — ele faz a contagem, e não o julgamento:

   ```bash
   python scripts/summarize_csv.py --input <arquivo.csv> --output resumo.json
   ```

   Use `--delimiter ";"` quando o arquivo vier com ponto e vírgula, e
   `--max-values N` para mudar quantos valores frequentes aparecem por coluna.
3. Se o script falhar, leia a mensagem em `stderr`: arquivo inexistente,
   arquivo vazio ou cabeçalho ausente são erros do dado, não da skill. Relate ao
   usuário em vez de contornar.
4. Leia o `resumo.json` e escreva o relatório usando o modelo
   [assets/report-template.md](assets/report-template.md).
5. Formate números e datas conforme [reference/formatting.md](reference/formatting.md).
6. Destaque o que o usuário precisa decidir: colunas com muitos faltantes,
   colunas constantes, cardinalidade suspeita.
7. Entregue o relatório e diga onde o `resumo.json` ficou.

## Regras

- Nunca invente estatística: todo número do relatório sai do `resumo.json`.
- Não abra o CSV inteiro no contexto da conversa; o script existe para isso.
- Não altere o arquivo de entrada.
- Amostras de valores no relatório: no máximo cinco por coluna, sem dados pessoais.

## Resultado esperado

- `resumo.json` com as estatísticas por coluna.
- Relatório em Markdown seguindo o modelo, com os pontos de atenção destacados.
- Menção explícita das limitações do que foi analisado (tamanho da amostra, delimitador usado).
