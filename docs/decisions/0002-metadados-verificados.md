# 0002 — Nome e descrição são verificados, não sugeridos

- Status: aceita
- Data: 2026-08-11

## Contexto

O `name` e a `description` decidem se a skill é acionada. Recomendações em
documentação não impedem descrições genéricas, longas demais ou sem indicação de
quando usar — e o efeito só aparece depois, como "o agente ignorou a skill".

## Decisão

As regras de metadados viram verificação executável em `check_skills.py`:
kebab-case, nome igual à pasta, até 5 termos e 64 caracteres; descrição de 40 a
1024 caracteres, em uma linha, com marcador de acionamento e sem enchimento
inicial. Cada skill também precisa de gatilhos positivos e negativos em
`evals/<nome>.json`.

## Consequências

- Uma descrição ruim reprova no `validate`, antes do merge.
- As heurísticas são objetivas e, por isso, aproximadas: elas não julgam se a
  descrição é boa, apenas se cumpre as condições mínimas. A avaliação com agente
  continua necessária.
- Mudar os limites exige mudar o script e registrar aqui.
