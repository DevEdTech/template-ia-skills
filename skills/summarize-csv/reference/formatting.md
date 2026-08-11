# Formatação do relatório

Regras consultadas na hora de escrever o relatório. Não é preciso ler antes.

## Números

- Contagens: número inteiro, sem separador (`1234`).
- Média e mediana: duas casas decimais (`1234.56`).
- Mínimo e máximo: mantenha as casas decimais que aparecem no dado original.
- Percentuais: uma casa decimal com o símbolo (`12.5%`). Calcule sobre o total de linhas.
- Valores muito grandes: escreva por extenso ao lado quando ajudar a leitura
  (`1200000` → `1200000 (1,2 milhão)`).

## Faltantes

- Sempre reporte faltantes como contagem **e** percentual: `312 (12.5%)`.
- Acima de 20% de faltantes, a coluna entra em "Pontos de atenção".
- Coluna com 100% de faltantes é reportada como vazia, não como texto.

## Cardinalidade

- `unique == 1`: coluna constante — provável campo inútil ou erro de export.
- `unique == filled`: identificador — não some, não tire média.
- `unique <= 10` em coluna de texto: trate como categoria e liste os valores.

## Amostras de valores

- No máximo cinco valores por coluna.
- Trunque valores longos em 60 caracteres, terminando com `…`.
- Nunca reproduza no relatório dado que pareça pessoal (documento, telefone,
  e-mail, endereço): escreva `[valor omitido]` e informe o motivo.

## Datas

- Não converta formatos: reproduza como está no arquivo.
- Se a coluna parece data mas veio como texto, registre isso em "Pontos de atenção"
  em vez de tentar interpretar.

## Tom

- Frases curtas e factuais.
- Nada de recomendação sem base no dado ("provavelmente a área comercial...").
- Toda observação cita a coluna e o número que a sustenta.
