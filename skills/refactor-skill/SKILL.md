---
name: refactor-skill
description: Corrige uma skill existente sem mudar o que ela entrega — reescreve nome e descrição para disparar melhor, encurta o SKILL.md, move detalhe para reference/ e transforma passo instável em script. Use quando a skill não dispara, dispara demais, está longa ou dá resultado irregular.
---

# Refatorar skill

## Objetivo

Melhorar gatilho, clareza e estabilidade de uma skill já existente, preservando
o resultado que ela entrega.

## Quando usar

- A skill não é acionada nos pedidos em que deveria.
- A skill rouba o gatilho de outra, ou duas skills competem pelo mesmo pedido.
- O `SKILL.md` cresceu e ficou caro de carregar.
- A avaliação (`evaluate-skill`) apontou resultado irregular.

## Quando não usar

- Skill nova: use `plan-skill` e `create-skill`.
- Só encontrar problemas, sem corrigir: use `review-skill`.

## Processo

1. Reúna a evidência: achados de `review-skill`, resultados de `evaluate-skill`
   ou o pedido concreto que falhou. Sem evidência, pergunte antes de mexer.
2. Declare o que **não** vai mudar: o resultado que a skill entrega.
3. Aplique uma correção por vez, na ordem de impacto:
   - **Gatilho** — reescreva a `description` seguindo [reference/metadata-patterns.md](reference/metadata-patterns.md).
   - **Fronteira** — acrescente o limite ("não use quando...") e o gatilho negativo nos evals.
   - **Tamanho** — mova para `reference/` o que não é usado em toda execução.
   - **Estabilidade** — transforme em script o passo determinístico que varia entre execuções.
   - **Ordem** — reescreva passos vagos como ações verificáveis.
4. Renomear a skill é mudança de contrato: renomeie a pasta, o `name` do
   frontmatter, o arquivo em `evals/`, as citações no catálogo e avise que
   instalações anteriores continuam com o nome antigo.
5. Atualize `evals/<nome>.json` sempre que o gatilho mudar.
6. Rode `python scripts/dev.py validate`.
7. Reavalie com `evaluate-skill` e compare o placar com o anterior.

## Regras

- Uma correção por commit, com a evidência no corpo da mensagem.
- Não aproveite a refatoração para adicionar capacidades novas.
- Não remova limites de segurança nem pontos de confirmação.
- Se o resultado da skill precisar mudar, isso é escopo novo: volte para `plan-skill`.

## Resultado esperado

- Antes e depois do `name` e da `description`, quando houver mudança.
- Lista de arquivos alterados e a evidência que motivou cada mudança.
- Confirmação de que o resultado entregue permanece o mesmo.
- Novo placar de avaliação comparado ao anterior.
