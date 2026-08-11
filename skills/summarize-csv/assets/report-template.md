<!--
Modelo de relatório da skill summarize-csv.
Preencha os campos entre colchetes com os números do resumo.json.
Não invente valores: todo número vem do arquivo gerado pelo script.
-->

# Resumo de [nome-do-arquivo.csv]

## Visão geral

- **Linhas**: [rows]
- **Colunas**: [columns]
- **Delimitador**: `[delimiter]`
- **Linhas com número de campos diferente do cabeçalho**: [ragged_rows]

## Colunas

| Coluna | Tipo | Preenchidos | Faltantes | Distintos | Observação |
| ------ | ---- | ----------- | --------- | --------- | ---------- |
| [name] | [numeric/text] | [filled] | [missing] | [unique] | [o que chama atenção] |

## Colunas numéricas

| Coluna | Mínimo | Máximo | Média | Mediana |
| ------ | ------ | ------ | ----- | ------- |
| [name] | [min]  | [max]  | [mean] | [median] |

## Valores mais frequentes

**[coluna]**: [valor] ([count]×), [valor] ([count]×)

## Pontos de atenção

- [Coluna com muitos faltantes e o efeito disso]
- [Coluna constante ou com cardinalidade suspeita]
- [Linhas irregulares, se houver]

## Limitações

- Análise feita sobre o arquivo `[nome-do-arquivo.csv]`, com delimitador `[delimiter]`.
- [Outra limitação relevante, como amostra parcial ou codificação assumida]
