# 0003 — Scripts de skill usam apenas a biblioteca padrão

- Status: aceita
- Data: 2026-08-11

## Contexto

Um script de skill roda no ambiente de quem instalou a skill, não neste
repositório. Dependência de terceiros significa instalação prévia, versão
compatível e permissão de rede — condições que a skill não controla.

## Decisão

Por padrão, scripts de skill importam apenas a stdlib. Quando não houver
alternativa, a dependência é declarada em `skills/<nome>/requirements.txt`,
justificada no pull request e registrada em ADR. O `check_skills.py` reprova
import de pacote não declarado; o `smoke-bundles` executa `--help` em modo
isolado (`python -I`) para skills sem dependências.

## Consequências

- A maioria das skills funciona em qualquer máquina com Python.
- Tarefas que exigem bibliotecas pesadas ficam mais trabalhosas — é o custo aceito.
- Skills com dependência não são executadas no smoke; a instalação passa a ser
  responsabilidade do destino, e isso precisa ser comunicado na entrega.
