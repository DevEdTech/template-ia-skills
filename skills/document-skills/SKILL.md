---
name: document-skills
description: Atualiza catálogo, README e ADRs depois que uma skill é criada, renomeada ou removida, mantendo a documentação coerente com a pasta skills/. Use ao final de qualquer mudança que altere o conjunto de skills do repositório.
---

# Documentar skills

## Objetivo

Manter a documentação sincronizada com o que existe em `skills/`, para que
quem chega ao repositório encontre a skill certa sem abrir os arquivos.

## Quando usar

- Depois de criar, renomear ou remover uma skill.
- Depois de mudar a `description` de uma skill (o catálogo repete o gatilho).
- Antes de abrir pull request que mexe no conjunto de skills.

## Quando não usar

- Mudança apenas interna a uma skill, sem efeito no gatilho nem no resultado.
- Reescrita do `README.md` inteiro, quando ele perdeu a estrutura ou ainda
  descreve o template: isso é `update-readme`. Aqui você ajusta apenas os
  trechos que citam skills por nome.
- Mudança nas **regras** do repositório: isso é `update-agents`, que cuida do
  `AGENTS.md` da raiz. Aqui você cuida do catálogo em `docs/agents.md`.

## Processo

1. Liste o que existe: pastas em `skills/`, entradas no catálogo `docs/agents.md`,
   menções no `README.md` e arquivos em `evals/`.
2. Atualize `docs/agents.md` mantendo o formato exato de cada linha —
   `- **nome-da-skill** — o que faz e quando é acionada.` —, que é o formato
   verificado por `python scripts/dev.py check-docs`.
3. Ordene o catálogo pelo fluxo de trabalho, não por ordem alfabética: planejar,
   criar, avaliar, revisar, refatorar, empacotar.
4. Ajuste no `README.md` os trechos que citam skills por nome.
5. Registre em `docs/decisions/` um ADR quando a mudança alterar como as skills
   são organizadas, validadas ou distribuídas — não para skill nova rotineira.
6. Se uma skill foi removida, apague também `evals/<nome>.json`, os testes dos
   scripts dela e as menções na documentação.
7. Rode `python scripts/dev.py validate`.

## Regras

- O catálogo descreve **o que a skill faz e quando dispara**, em uma linha; detalhe fica no `SKILL.md`.
- Não copie o `SKILL.md` para a documentação: duplicar é garantir divergência.
- Skill que não está no catálogo reprova na verificação; catálogo com skill inexistente também.

## Resultado esperado

- Catálogo, README e ADRs coerentes com `skills/`.
- Lista dos documentos alterados, com o resumo de cada mudança.
- Saída de `python scripts/dev.py validate`.
