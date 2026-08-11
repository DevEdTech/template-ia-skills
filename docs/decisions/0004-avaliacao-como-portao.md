# 0004 — Avaliação de gatilho faz parte do portão de qualidade

- Status: aceita
- Data: 2026-08-11

## Contexto

Testes automatizados provam que os scripts funcionam, mas não respondem à
pergunta que decide o valor de uma skill: ela é acionada quando o usuário pede,
e não é acionada quando o pedido é de outra? Sem isso, o repositório acumula
skills corretas e inúteis.

## Decisão

Toda skill tem `evals/<nome>.json` com pelo menos dois gatilhos positivos, um
negativo e um cenário de execução com resultados esperados e sinais de alerta. O
`check-evals` entra no `validate`. A execução dos cenários com um agente é feita
pela skill `evaluate-skill`, com resultado registrado em `docs/evaluations/`.

## Consequências

- O `validate` garante que os cenários existem e estão completos, mas não os executa:
  rodar um agente exige rede, credenciais e tempo, incompatíveis com um portão local offline.
- A execução fica sob responsabilidade explícita de quem entrega a skill.
- Descrição alterada obriga reavaliação do gatilho.
