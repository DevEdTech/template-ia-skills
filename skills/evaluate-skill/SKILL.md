---
name: evaluate-skill
description: Roda os cenários de evals/<skill>.json em sessões limpas, mede acerto de gatilho e de execução e registra o resultado com as correções sugeridas. Use quando precisar de evidência de que a skill dispara na hora certa e entrega o resultado esperado.
---

# Avaliar skill

## Objetivo

Substituir a impressão de que "a skill parece boa" por medida: em quantos casos
ela disparou quando devia, deixou de disparar quando não devia, e produziu o
resultado combinado.

## Quando usar

- Depois de criar ou alterar uma skill, antes de distribuir.
- Quando a skill dispara demais, de menos, ou o resultado varia entre execuções.
- Ao trocar de modelo, de agente ou de configuração.

## Quando não usar

- Para conferir estrutura e metadados: isso é `check-skills` e `review-skill`.

## Processo

1. Confira os cenários: `python scripts/dev.py check-evals`.
2. Se a skill ainda não tem cenários suficientes, escreva-os a partir de
   [assets/eval-template.json](assets/eval-template.json): dois gatilhos positivos com vocabulários
   diferentes, um negativo apontando para a skill vizinha, e um cenário de
   execução com resultados esperados e sinais de alerta.
3. Gere a folha de execução: `python scripts/dev.py eval-sheet <nome-da-skill>`.
4. **Gatilho** — para cada caso, abra uma sessão limpa e cole o prompt **sem citar
   a skill pelo nome**. Registre qual skill o agente carregou.
5. **Execução** — em outra sessão, cole o prompt do cenário e deixe o agente
   trabalhar sem ajuda. Registre o artefato produzido.
6. Confronte o resultado com `expect` e `red_flags`. Um sinal de alerta observado
   vale como falha, mesmo que o resultado final pareça correto.
7. Repita cada caso três vezes: a variação entre execuções é o dado mais útil.
8. Escreva o resultado em `docs/evaluations/<nome>-<data>.md`: caso, esperado,
   observado, veredito.
9. Para cada falha, aponte a causa provável e o alvo da correção:
   - não disparou → `description` (vocabulário e situação de uso);
   - disparou no caso errado → limite explícito na `description` e gatilho negativo;
   - resultado errado → passo ausente ou ambíguo no `Processo`;
   - resultado instável → passo determinístico que deveria ser script.
10. Encaminhe as correções para `refactor-skill`. Não altere a skill aqui.

## Resultado esperado

- Tabela por caso: prompt, esperado, observado, veredito.
- Placar: acertos de gatilho e de execução sobre o total.
- Lista de correções priorizadas, cada uma ligada ao arquivo que precisa mudar.
- Arquivo de resultado salvo em `docs/evaluations/`.
