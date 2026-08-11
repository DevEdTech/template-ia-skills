---
name: plan-skill
description: Transforma uma ideia em especificação aprovada de skill — nome, descrição, gatilhos, processo, limites e critérios de aceite. Use quando surgir a necessidade de uma skill nova, antes de escrever qualquer arquivo; não use para ajustar skill já existente.
---

# Planejar skill

## Objetivo

Decidir, antes de escrever arquivos, **o que a skill faz, quando ela dispara e
como se prova que funcionou**. A saída é uma especificação aprovada pelo
usuário, em `docs/skills/<nome>.md`.

## Quando usar

- Ideia de skill nova, ainda sem escopo fechado.
- Pedido recorrente que aparece em várias conversas e vale automatizar.
- Antes de `create-skill`, sempre.

## Quando não usar

- Melhorar uma skill que já existe: use `refactor-skill`.
- Converter um runbook ou prompt já escrito: use `import-workflow`.

## Regras de conversa

1. Leia `AGENTS.md`, `docs/architecture.md` e `docs/skill-metadata.md` antes de perguntar.
2. Liste as skills existentes em `skills/` e verifique sobreposição de gatilho antes de propor uma nova.
3. Faça de uma a três perguntas curtas por rodada; priorize a decisão que desbloqueia as demais.
4. Ofereça duas ou três opções concretas com uma recomendação quando isso acelerar a resposta.
5. Não aceite "simples", "inteligente", "completo" ou "etc." como especificação: peça exemplo, limite ou resultado observável.
6. Não invente requisitos; marque cada item como `decidido`, `pendente` ou `fora do escopo`.
7. Não escreva a skill nesta etapa.

## Sequência de descoberta

1. **Tarefa**: qual trabalho repetitivo a skill executa, do gatilho ao resultado.
2. **Dono do pedido**: quem pede, com que vocabulário, em que momento.
3. **Gatilho**: as frases reais que devem acionar a skill — e as frases vizinhas que **não** devem.
4. **Entradas**: arquivos, caminhos, formatos, dados obrigatórios e opcionais.
5. **Saída**: artefato produzido, onde fica, em que formato, com que estrutura.
6. **Processo**: passos na ordem, decisões, pontos de confirmação com o usuário.
7. **Determinismo**: que passos devem virar script Python (contagem, parsing, validação, conversão) em vez de ficar a cargo do julgamento do agente.
8. **Assets**: modelos, tabelas, exemplos e esquemas que a skill precisa carregar.
9. **Divulgação progressiva**: o que fica no `SKILL.md` e o que vai para `reference/`, lido só quando necessário.
10. **Limites**: o que a skill nunca faz, o que exige confirmação e que dados são sensíveis.
11. **Critérios de aceite**: como um revisor confirma, olhando o resultado, que a skill funcionou.

## Regra de decisão: script, referência ou instrução

- **Script** quando o passo é determinístico, repetitivo ou sujeito a erro de contagem/formato.
- **Referência** quando é conhecimento extenso e consultado só em alguns casos.
- **Instrução no `SKILL.md`** quando é julgamento que o agente precisa aplicar sempre.

## Portão de conclusão

Antes de gerar a especificação, confirme que existem decisões explícitas para:
tarefa, gatilhos positivos e negativos, entradas, saída, processo, scripts,
assets, limites e critérios de aceite. Apresente um resumo e peça **aprovação
explícita**. Se houver correção, volte à descoberta.

## Produção da especificação

Crie `docs/skills/<nome>.md` a partir de [assets/skill-spec-template.md](assets/skill-spec-template.md).
Ao preencher:

- proponha `name` em kebab-case, verbo + objeto, no máximo 5 termos;
- escreva a `description` em uma linha, dizendo o que a skill faz **e** quando usá-la, seguindo `docs/skill-metadata.md`;
- registre pelo menos dois gatilhos positivos e um negativo, com as frases reais do usuário;
- deixe cada critério de aceite verificável;
- não use "TBD", "a definir" ou "entre outros".

## Encerramento

Informe: decisões consolidadas, arquivo criado e próximo passo — usar
`create-skill` para gerar a skill a partir da especificação aprovada.
