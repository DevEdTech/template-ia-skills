# Avaliação de skills

Guia para calibrar expectativas ao testar um agente, modelo ou configuração nova
com as skills deste repositório. Os prompts e os critérios executáveis vivem em
`evals/<skill>.json`; aqui ficam o método e os sinais que valem para todas.

## Método

1. `python scripts/dev.py check-evals` — os cenários estão completos?
2. `python scripts/dev.py eval-sheet <skill>` — gera a folha para executar.
3. **Gatilho**: sessão limpa, prompt colado **sem citar a skill**. Anote qual skill foi carregada.
4. **Execução**: sessão limpa, prompt do cenário, sem ajuda durante o trabalho.
5. Três repetições por caso. Registre a variação.
6. Resultado em `docs/evaluations/<skill>-<data>.md`.

## Sinais que valem para qualquer skill

**Bom resultado**

- A skill certa foi acionada sem que o nome fosse citado.
- O agente seguiu os passos do `SKILL.md` na ordem, sem inventar etapas.
- Os scripts da skill foram executados em vez de reimplementados na conversa.
- Referências foram abertas quando o passo mandava, e não "por precaução".
- Pontos de confirmação foram respeitados antes de qualquer ação irreversível.
- O resultado final é o artefato prometido, no lugar prometido.
- Entradas inválidas foram apontadas, não adivinhadas.

**Sinais de alerta**

- Nenhuma skill foi acionada, ou foi acionada a vizinha.
- Duas skills disputaram o mesmo pedido.
- O agente fez à mão o que um script da skill já faz.
- Carregou toda a pasta `reference/` antes de precisar.
- Ampliou o escopo ("já aproveitei e fiz também...").
- Declarou sucesso sem produzir o artefato.
- Resultado diferente a cada execução do mesmo prompt.

## Diagnóstico: da falha à correção

| Sintoma | Causa provável | Onde corrigir |
| ------- | -------------- | ------------- |
| Não disparou | descrição sem o vocabulário do usuário | `description` |
| Disparou no caso errado | descrição ampla, sem limite | `description` + gatilho negativo nos evals |
| Disparou a skill vizinha | fronteira não declarada entre as duas | ambas as descrições |
| Pulou etapas | passo vago ou não verificável | `Processo` do `SKILL.md` |
| Resultado instável | julgamento onde deveria haver script | novo script em `scripts/` |
| Contexto estourado | corpo longo demais | mover para `reference/` |
| Quebrou fora do repositório | dependência implícita | script e `smoke-bundles` |

## Particularidades por skill

- **plan-skill** — bom: perguntas em rodadas curtas, aprovação explícita antes de gerar arquivos. Alerta: escreveu a skill durante o planejamento.
- **import-workflow** — bom: todo trecho do material com destino declarado. Alerta: melhorou o processo enquanto o importava.
- **create-skill** — bom: usou o gerador, citou todos os arquivos criados, validate verde. Alerta: `SKILL.md` inchado no lugar de `reference/`.
- **evaluate-skill** — bom: sessões limpas, repetição, falha ligada ao arquivo que precisa mudar. Alerta: corrigiu a skill durante a avaliação.
- **review-skill** — bom: achados com arquivo, trecho e correção mínima. Alerta: "está tudo certo" sem evidência.
- **refactor-skill** — bom: partiu de evidência, mostrou antes e depois da descrição. Alerta: adicionou capacidades novas.
- **package-skill** — bom: conferiu o manifesto e informou o `sha256`. Alerta: empacotou com verificação pendente.
- **document-skills** — bom: catálogo no formato exato e sem skill órfã. Alerta: copiou o `SKILL.md` para a documentação.
- **summarize-csv** — bom: números saíram do `resumo.json`. Alerta: estatística inventada ou CSV inteiro no contexto.
