# Trabalhando com agentes

Este repositório é operado por agentes de código: eles criam, revisam e
empacotam as skills. Aqui está como orientá-los.

## Prompts x arquivos persistentes

- **Prompt**: o que você pede no momento ("crie uma skill para revisar contratos").
- **Arquivos persistentes**: regras que valem sempre, gravadas no repositório:
  - `AGENTS.md` (raiz) — regras gerais para qualquer agente.
  - `CLAUDE.md` (raiz) — instruções específicas para o Claude Code.

O agente lê os arquivos persistentes automaticamente. Use o prompt para a
tarefa; deixe as regras fixas nos arquivos.

## Catálogo de skills

- **plan-skill** — conduz da ideia até uma especificação aprovada, com gatilhos, processo e critérios de aceite, sem escrever a skill.
- **import-workflow** — converte prompt, runbook ou checklist já existente em uma skill estruturada e testável.
- **create-skill** — escreve a skill completa a partir da especificação aprovada e deixa o validate verde.
- **evaluate-skill** — roda os cenários de `evals/` em sessões limpas e mede acerto de gatilho e de execução.
- **review-skill** — revisa uma skill contra o rubrico do projeto e devolve achados priorizados, sem alterar arquivos.
- **refactor-skill** — corrige gatilho, tamanho e estabilidade de uma skill existente, preservando o que ela entrega.
- **package-skill** — empacota skills validadas e entrega as instruções de instalação no destino escolhido.
- **document-skills** — atualiza catálogo, README e ADRs quando o conjunto de skills muda.
- **summarize-csv** — skill de demonstração: resume um CSV com script, modelo e referência (remova-a no setup).

As skills canônicas ficam em `skills/`; as cópias em `.claude/skills` e
`.agents/skills` são geradas por `python scripts/dev.py sync-skills`.

## Como pedir uma skill nova

> Use a skill plan-skill para me ajudar a definir uma skill que revise contratos em PDF antes do envio.

A conversa é feita de perguntas curtas. Responda com exemplos concretos: as
frases que você realmente usaria ao pedir, os arquivos de entrada e um exemplo
de resultado bom. A especificação sai daí.

## Como aproveitar o que já existe

> Use a skill import-workflow: nosso processo de fechamento está no documento X e no prompt que eu colo toda semana.

## Como implementar

> A especificação foi aprovada. Use a skill create-skill e garanta que `python scripts/dev.py validate` passe limpo.

## Como medir se funciona

> Use a skill evaluate-skill na summarize-csv e me mostre o placar de gatilho e execução.

## Como revisar e corrigir

> Use a skill review-skill na skill nova antes do PR.
>
> Use a skill refactor-skill para aplicar os achados bloqueadores.

## Limites de autonomia

O agente deve:

- Não criar skill sem especificação aprovada.
- Não expandir o escopo além do que foi pedido.
- Não adicionar dependências de terceiros sem justificativa e `requirements.txt` na skill.
- Não expor segredos, credenciais ou dados de cliente dentro de uma skill.
- Não distribuir pacote com verificação pendente.
- Não alterar a estrutura das skills sem registrar a decisão em `docs/decisions/`.

Na dúvida, o agente deve perguntar antes de agir.
