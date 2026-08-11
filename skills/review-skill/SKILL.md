---
name: review-skill
description: Revisa uma skill contra os critérios do projeto — metadados, gatilho, processo, scripts, segurança e divulgação progressiva — e devolve achados priorizados sem alterar arquivos. Use antes de empacotar, abrir pull request ou publicar uma skill.
---

# Revisar skill

## Objetivo

Encontrar, antes da distribuição, o que faria a skill não disparar, disparar no
caso errado, quebrar fora deste repositório ou desviar o agente do escopo.

## Quando usar

- Antes de abrir pull request de uma skill nova ou alterada.
- Antes de `package-skill`.
- Quando uma skill em uso está produzindo resultados irregulares.

## Quando não usar

- Para aplicar as correções encontradas: isso é `refactor-skill`.

## Processo

1. Leia o `SKILL.md` inteiro, depois os arquivos de `reference/`, `assets/` e `scripts/`.
2. Rode `python scripts/dev.py check-skills` e `python scripts/dev.py check-evals`
   e trate cada erro como bloqueador.
3. Percorra o rubrico em [reference/criteria.md](reference/criteria.md), item a item.
4. Para o gatilho, faça o teste da sessão limpa: leia só a `description` e
   pergunte se ela decide sozinha entre acionar e não acionar a skill.
5. Compare a descrição com as das skills vizinhas e aponte sobreposição.
6. Verifique se os scripts rodam isolados: `python -I skills/<nome>/scripts/<script>.py --help`.
7. Confirme que nenhum passo do processo depende de contexto que só existe nesta conversa.
8. Não altere arquivos; proponha a correção mínima de cada achado.

## Classificação dos achados

- **Bloqueador** — impede a skill de disparar, de rodar fora do repositório, ou expõe risco de segurança.
- **Importante** — degrada o resultado ou o gatilho em casos comuns.
- **Melhoria** — deixa a skill mais curta, mais clara ou mais barata em contexto.
- **Observação** — registro para decisão futura, sem ação agora.

## Resultado esperado

- Achados agrupados por prioridade, cada um com arquivo, trecho e correção proposta.
- Veredito explícito: pronta para empacotar, ou lista do que falta.
- Nenhum arquivo alterado.
