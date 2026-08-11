# Padrões de nome e descrição

O nome e a descrição são a única parte da skill que o agente lê **antes** de
decidir usá-la. Eles não são rótulo: são o classificador que separa "esta skill
resolve o pedido" de "esta não".

## Nome

Fórmula: **verbo + objeto**, kebab-case, até 5 termos e 64 caracteres.

| Evite | Prefira | Motivo |
| ----- | ------- | ------ |
| `helper` | `resumir-csv` | diz o que faz |
| `skill-de-relatorio-financeiro-mensal` | `gerar-relatorio-mensal` | curto e específico |
| `csv` | `converter-csv` | substantivo sozinho não indica ação |
| `processar-dados` | `validar-planilha-fiscal` | genérico demais compete com tudo |

Não use prefixos como `skill-`, numeração ou nome de time. O nome viaja com a
skill para outros repositórios.

## Descrição

Uma linha, de 40 a 1024 caracteres, com três partes:

1. **O que a skill entrega** — comece por verbo no presente.
2. **Quando acionar** — "Use quando ..." com as situações e o vocabulário do usuário.
3. **Onde termina** — "não use quando ..." apontando a skill vizinha, quando houver ambiguidade.

### Fórmula

```
<Verbo> <resultado concreto> a partir de <entrada>. Use quando <situação real>;
não use quando <caso vizinho>.
```

### Antes e depois

**Antes** — genérica, sem gatilho:

```yaml
description: Esta skill ajuda com relatórios.
```

**Depois** — o que faz, quando dispara, onde termina:

```yaml
description: Gera o relatório mensal de vendas em Markdown a partir dos CSVs de fechamento. Use quando o pedido citar fechamento, relatório mensal ou consolidação de vendas; não use para análises exploratórias de dados avulsos.
```

## Vocabulário de gatilho

Inclua as palavras que o usuário usa, não as internas do projeto:

- nomes de arquivo e extensões (`.csv`, `.docx`, `planilha`, `fechamento`);
- verbos do pedido (`resumir`, `converter`, `revisar`, `publicar`);
- nomes de sistemas e artefatos citados no dia a dia;
- sinônimos regionais quando existirem ("planilha" e "spreadsheet").

## Erros que fazem a skill não disparar

- Descrição que só fala do processo interno ("segue o fluxo de quatro etapas").
- Descrição em terceira pessoa sobre a própria skill ("Esta skill foi criada para...").
- Só o que faz, sem quando usar.
- Jargão que o usuário nunca escreveria.

## Erros que fazem a skill disparar demais

- Termos amplos: "arquivos", "dados", "documentos", "qualquer".
- Nenhum limite explícito quando existe skill vizinha.
- Vários assuntos em uma skill só — sinal de que são duas skills.

## Teste rápido

Leia **apenas** o nome e a descrição e responda:

1. Que pedido concreto aciona isso?
2. Que pedido parecido **não** aciona?
3. Que artefato eu recebo no final?

Se alguma resposta exigir abrir o `SKILL.md`, a descrição ainda não está pronta.
