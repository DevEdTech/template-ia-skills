# Entregas

Esta pasta guarda a evidência das entregas concluídas. Enquanto
[tasks](../tasks/README.md) descreve o que **será** feito e
`docs/evaluations/` guarda a medição de **uma** skill, cada arquivo aqui
registra o que **foi entregue** em conjunto: quais skills mudaram, como elas
se saíram e o que foi validado.

Serve para consultar depois o que um lote de skills entregou, sem precisar
reconstruir a história a partir do Git.

## Como usar

- Um arquivo por entrega, nomeado `AAAA-MM-DD-slug-da-entrega.md`
  (ex.: `2026-08-17-skills-de-fechamento.md`).
- O agente cria o arquivo com a skill `document-delivery`, depois de
  `create-skill` e `evaluate-skill`, com o validate verde.
- O documento aponta para `docs/skills/` e `docs/evaluations/` em vez de
  copiá-los.
- Não sobrescreva entregas anteriores. Se a mesma entrega ganhar um
  incremento, acrescente uma seção datada ao arquivo existente.
- Registre apenas resultado real de comando executado; não estime placar de
  avaliação.

## Modelo

O modelo fica em `skills/document-delivery/assets/delivery-template.md` e tem
as seções: objetivo, skills entregues, critérios de aceite, avaliação,
arquivos alterados, validações executadas, pacotes gerados, fora do escopo,
limitações e pendências, e como verificar manualmente.
