# Rubrico de revisão de skills

Percorra na ordem. Cada pergunta tem resposta verificável no arquivo ou no comando.

## 1. Gatilho

- A `description` cita as palavras que o usuário realmente usa, não o jargão interno?
- Ela diz **quando não** usar, ou pelo menos delimita o caso?
- Duas skills do repositório podem reivindicar o mesmo pedido? Qual vence e por quê?
- Os gatilhos negativos de `evals/<nome>.json` cobrem as skills vizinhas?
- A descrição continua verdadeira se lida sem o corpo do `SKILL.md`?

## 2. Processo

- Cada passo tem um resultado observável, ou é conselho genérico?
- A ordem é executável por alguém que não participou da conversa?
- Existem pontos de confirmação antes de ações irreversíveis (apagar, enviar, publicar)?
- O que o agente faz quando um passo falha está escrito?
- O processo cabe em um `SKILL.md` curto, ou está pedindo `reference/`?

## 3. Divulgação progressiva

- O `SKILL.md` cabe em 500 linhas?
- O que está no corpo é usado em **toda** execução? O que é ocasional foi para `reference/`?
- Cada arquivo de `reference/` é citado do passo que precisa dele?
- Existe conteúdo duplicado entre corpo e referência?

## 4. Scripts

- O passo virou script porque é determinístico, ou o script está fazendo julgamento?
- `python -I <script> --help` funciona fora do repositório?
- Imports são só stdlib (ou o que está em `requirements.txt`)?
- Erros vão para `stderr` com código diferente de zero?
- O script escreve apenas onde foi mandado escrever?
- Há teste para sucesso, entrada inválida e caso vazio?

## 5. Assets

- Os modelos têm marcadores claros e instruções de preenchimento?
- Algum asset é grande demais para o valor que entrega?
- Algum arquivo está órfão (não citado por ninguém)?

## 6. Fluxos complexos

- Etapas longas produzem artefato intermediário verificável?
- O estado do trabalho fica em arquivo, e não na memória da conversa?
- Existe critério explícito de conclusão?
- A skill sabe quando devolver a decisão ao usuário?

## 7. Segurança e limites

- Há segredo, token, credencial, caminho pessoal ou dado de cliente?
- A skill instrui o agente a contornar regras do projeto ou a agir sem confirmação?
- Ações externas (rede, envio, publicação) estão explicitadas?
- A skill declara o que nunca faz?

## 8. Portabilidade

- Caminhos usam `/` relativo, sem raiz de máquina?
- O texto assume um sistema operacional específico sem necessidade?
- A skill funciona em um repositório que não é este?
