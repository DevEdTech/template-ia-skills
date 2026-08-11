# Nome e descrição

O `name` e a `description` de uma skill ficam carregados o tempo todo e são a
única informação que o agente tem **antes** de decidir usá-la. Uma skill
excelente com descrição ruim nunca é acionada; uma descrição ampla demais rouba
o gatilho das vizinhas. Este documento é a regra do projeto; a verificação
correspondente está em `python scripts/dev.py check-skills`.

## Regras verificadas

| Campo | Regra | Motivo |
| ----- | ----- | ------ |
| `name` | kebab-case (`^[a-z][a-z0-9]*(-[a-z0-9]+)*$`) | formato aceito por quem carrega a skill |
| `name` | igual ao nome da pasta | a pasta é a identidade instalada |
| `name` | até 64 caracteres | limite de quem carrega |
| `name` | até 5 termos | nome longo é sinal de escopo largo demais |
| `description` | 40 a 1024 caracteres | curta demais não decide; longa demais custa contexto |
| `description` | uma única linha | o frontmatter é lido linha a linha |
| `description` | contém indicação de acionamento ("use quando...", "ao...", "antes de...") | é o que ensina o agente a disparar |
| `description` | não começa com "Esta skill...", "Uma skill..." | enchimento gasta o começo, que é o trecho mais lido |

## Fórmula do nome

**verbo + objeto**, em kebab-case:

- `resumir-csv`, `revisar-contrato`, `gerar-relatorio-mensal`, `publicar-release`.

Evite:

- substantivo solto (`csv`, `relatorio`) — não diz o que a skill faz;
- genéricos (`processar-dados`, `helper`, `utils`) — competem com todo pedido;
- prefixos de organização (`skill-`, `time-x-`) — o nome viaja com a skill;
- nomes acima de 5 termos — quase sempre são duas skills disfarçadas de uma.

## Fórmula da descrição

```
<Verbo> <resultado concreto> a partir de <entrada>. Use quando <situações reais>;
não use quando <caso vizinho>.
```

Três perguntas que a descrição precisa responder sozinha:

1. Que artefato eu recebo no final?
2. Que pedido concreto aciona isso?
3. Que pedido parecido **não** aciona?

## Exemplos

**Ruim** — não diz quando usar:

```yaml
description: Ferramenta de análise de planilhas do time financeiro.
```

**Ruim** — ampla demais, dispara em tudo:

```yaml
description: Processa arquivos e dados de qualquer tipo. Use quando precisar tratar dados.
```

**Boa** — o que faz, quando dispara, onde termina:

```yaml
description: Resume um arquivo CSV com estatísticas por coluna e escreve um relatório em Markdown a partir do modelo da skill. Use quando o pedido envolver entender, resumir, conferir ou reportar o conteúdo de um CSV ou planilha exportada; não use para transformar ou editar os dados.
```

## Vocabulário de gatilho

Escreva com as palavras do usuário, não com as internas do projeto:

- extensões e nomes de arquivo (`.csv`, `planilha`, `export`, `fechamento`);
- verbos do pedido (`resumir`, `revisar`, `converter`, `publicar`);
- nomes de sistemas e artefatos citados no dia a dia;
- sinônimos que o time usa de fato.

## Fronteira entre skills vizinhas

Quando duas skills podem reivindicar o mesmo pedido, cada descrição precisa
declarar o limite, e os cenários em `evals/<nome>.json` precisam de um gatilho
negativo apontando para a vizinha. Exemplo neste repositório:

- `review-skill` — encontra problemas, **não** corrige;
- `refactor-skill` — corrige, a partir de evidência;
- `evaluate-skill` — mede gatilho e execução, **não** altera a skill.

## Quando a descrição não resolve

Se você não consegue escrever uma descrição de uma linha que separe esta skill
das demais, o problema não é o texto: é o escopo. Divida em duas skills ou
volte para `plan-skill`.
