---
name: document-delivery
description: Registra em docs/entregas a evidência de uma entrega de skills — o que mudou, o placar das avaliações e as validações executadas. Use depois de create-skill e evaluate-skill, com o validate verde, antes de abrir o pull request.
---

# Documentar entrega

## Objetivo

Produzir a evidência da entrega: um arquivo em `docs/entregas` que registra
quais skills foram entregues, como elas se saíram nas avaliações e o
resultado das validações executadas.

## Quando usar

- Depois de criar ou refatorar skills e rodar `evaluate-skill`.
- Antes de abrir o pull request que leva as skills adiante.
- Ao fechar um lote de skills que será distribuído.

## Quando não usar

- Para medir uma skill: use `evaluate-skill`, que escreve o resultado
  detalhado em `docs/evaluations/`.
- Para sincronizar catálogo e README com `skills/`: use `document-skills`.
- Para julgar a qualidade de uma skill: use `review-skill`.
- Enquanto `python scripts/dev.py validate` não estiver verde: sem validação
  não há evidência a registrar.

## Processo

1. Confirme que a entrega terminou e que `python scripts/dev.py validate`
   passou. Se algo estiver falhando, pare e corrija antes de documentar.
2. Recupere a especificação aprovada em `docs/skills/<nome>.md` e os
   critérios de aceite que ela declarou.
3. Liste as skills criadas, alteradas, renomeadas ou removidas, com os
   arquivos de cada uma (`git diff --stat`).
4. Para cada skill, cite o placar de `evaluate-skill` — acerto de gatilho e
   de execução — e **link para o arquivo em `docs/evaluations/`**. Não
   reescreva a tabela caso a caso: ela já está lá.
5. Registre os casos que ainda falham e o que ficou combinado sobre eles.
6. Copie a saída real dos comandos executados. Não invente placar, não
   estime resultado de avaliação e não descreva execução que não aconteceu.
7. Quando houve `package-skill`, registre os pacotes gerados em `dist/` e o
   destino de instalação.
8. Escreva o arquivo em `docs/entregas/AAAA-MM-DD-<slug-da-entrega>.md`, a
   partir de [assets/delivery-template.md](assets/delivery-template.md).
9. Uma entrega por arquivo. Não sobrescreva entregas anteriores; se a mesma
   entrega ganhar um incremento, acrescente uma seção datada ao arquivo.
10. Não altere skills nesta etapa; apenas o documento da entrega.
11. Rode `python scripts/dev.py check-docs`.

## Regras

- A evidência é do que foi observado, não do que se espera que aconteça.
- Skill sem avaliação registrada não é entrega concluída: rode
  `evaluate-skill` antes.
- O documento aponta para `docs/evaluations/` e `docs/skills/` em vez de
  copiá-los; duplicar é garantir divergência.

## Resultado esperado

- Arquivo criado em `docs/entregas`, seguindo o modelo.
- Skills entregues, com placar de gatilho e de execução por skill.
- Arquivos alterados.
- Validações executadas, com a saída real.
- Pacotes gerados, quando houver.
- Fora do escopo, limitações e pendências.
