# 0001 — A skill é a unidade de entrega

- Status: aceita
- Data: 2026-08-11

## Contexto

O repositório não produz um aplicativo: produz conhecimento executável que outros
agentes carregam. Um layout de aplicação (`src/`, pacote instalável, features)
não descreve esse produto e força uma dependência entre o que é distribuído e o
repositório que o gerou.

## Decisão

Cada skill é uma pasta autocontida em `skills/<nome>/`, com `SKILL.md` na raiz e,
opcionalmente, `scripts/`, `assets/`, `reference/` e `requirements.txt`. Nenhuma
skill importa código do repositório nem depende de caminhos externos. O projeto
não é um pacote Python (`[tool.uv] package = false`); o build gera pacotes de
skill em `dist/`.

## Consequências

- A skill instalada em outro projeto se comporta como aqui — o `smoke-bundles` prova isso.
- Não há biblioteca compartilhada entre skills: código repetido entre duas skills
  é aceito conscientemente, em troca de independência na distribuição.
- Duas skills que precisariam compartilhar muita lógica provavelmente são uma só.
