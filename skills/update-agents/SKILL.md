---
name: update-agents
description: Atualiza o AGENTS.md da raiz — as regras que todo agente lê em toda sessão — quando anatomia de skill, verificações, scripts, avaliação ou convenções do repositório mudam. Use depois que a mudança foi implementada e validada; para o catálogo de skills em docs/agents.md, use document-skills.
---

# Atualizar AGENTS.md

## Objetivo

Manter o `AGENTS.md` da raiz fiel às regras que valem hoje no repositório.
Ele é carregado em toda sessão de agente: regra errada ali se propaga para
todas as skills criadas depois.

## Não confunda os dois arquivos

| Arquivo          | O que é                          | Quem cuida        |
| ---------------- | -------------------------------- | ----------------- |
| `AGENTS.md`      | As **regras** do repositório     | `update-agents`   |
| `docs/agents.md` | O **catálogo** de skills         | `document-skills` |

Skill nova entra no catálogo, não no `AGENTS.md`. O `AGENTS.md` só muda
quando a **regra** muda.

## Quando usar

Depois que uma mudança importante foi implementada e validada:

- Anatomia da skill: pasta permitida, arquivo obrigatório, limite de tamanho.
- Regra de `name` ou `description` que o `check-skills` passou a exigir.
- Regra de divulgação progressiva entre `SKILL.md`, `reference/` e `assets/`.
- Convenção dos scripts das skills: nomes, dependências, erros, testes.
- Exigência nova em `evals/` ou no modo de avaliar.
- Regra de segurança sobre o que pode ser distribuído em `dist/`.
- ADR aprovado que muda como as skills são organizadas ou validadas.

## Quando não usar

- Para acrescentar, renomear ou remover skill do catálogo: `document-skills`.
- Para reescrever o `README.md`: `update-readme`.
- Para registrar a evidência de uma entrega: `document-delivery`.
- Para mudança que não cria nem revoga regra.

## O que entra no AGENTS.md

Entra a regra imperativa, curta e verificável, que vale para **toda** skill.
Não entra explicação, tutorial nem histórico.

| Entra                                          | Não entra                        |
| ---------------------------------------------- | -------------------------------- |
| "Nenhuma outra entrada é permitida na raiz da skill." | A lista de exemplos de layout |
| "Somente biblioteca padrão."                   | Como declarar `requirements.txt` |
| "Mudou a descrição? Reavalie o gatilho."       | Como rodar a folha de avaliação  |

O detalhe fica em `docs/skill-metadata.md`, `docs/testing.md` e
`docs/packaging.md`; o `AGENTS.md` aponta para lá. Duplicar os dois é
garantir que um vai divergir do outro.

## Processo

1. Identifique a mudança e confirme que ela já está no repositório, com
   `python scripts/dev.py validate` verde. Regra não documenta intenção;
   documenta o que passou a valer.
2. Leia o `AGENTS.md` atual inteiro antes de editar.
3. Decida se a mudança **cria**, **altera** ou **revoga** uma regra. Se não
   faz nenhuma das três, pare: não é caso desta skill.
4. Quando a regra nasceu de um verificador, cite o limite exato que ele
   aplica — o número em `scripts/check_skills.py` e `scripts/check_evals.py`
   é a fonte da verdade, não a memória.
5. Escreva a regra na seção existente que já trata do assunto. Só crie
   seção nova quando o assunto não couber em nenhuma; a ordem canônica das
   seções está em [assets/agents-outline.md](assets/agents-outline.md).
6. Remova a regra que deixou de valer. Regra morta ensina o errado.
7. Verifique se o `CLAUDE.md` continua coerente com o `AGENTS.md`.
8. Rode `python scripts/dev.py validate`. Aqui o `check-docs` também cobre o
   `AGENTS.md`: link quebrado e tarefa inexistente reprovam.

## Regras de escrita

- Uma regra por linha, no imperativo. Nada de "recomenda-se".
- Frase curta, sem adjetivo. A regra precisa caber na cabeça de quem lê.
- Sem emoji, sem seção decorativa.
- Mantenha a ordem das seções existentes; reordenar sem necessidade só gera
  diff difícil de revisar.
- Custo de contexto é real: o arquivo é lido em toda sessão. Se a regra não
  muda o comportamento do agente, ela não merece uma linha.

## Resultado esperado

- `AGENTS.md` atualizado, com as regras que valem hoje.
- Lista do que foi acrescentado, alterado e removido, com o motivo.
- Confirmação de que `CLAUDE.md` continua coerente.
- Resultado de `python scripts/dev.py validate`.
