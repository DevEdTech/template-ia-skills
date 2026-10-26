# ADR 0005 — Limites com dispensa justificada, heurística como aviso

- Status: aceita
- Data: 2026-10-26

## Contexto

A verificação de skills tratava tudo como erro bloqueante, inclusive duas
classes de regra que não sustentam esse peso:

1. **Heurística.** `description` precisava conter uma de oito palavras
   (`quando`, `use `, `usar`, `ao `, ...) para "indicar o acionamento". É
   varredura de substring: uma descrição boa sem essas palavras reprovava, e
   uma ruim contendo "quando" passava. O mesmo para o prefixo de enchimento.
2. **Limite duro sem válvula.** 500 linhas de corpo, 5 termos no nome, 64
   caracteres, 40 caracteres mínimos de descrição, conjunto fechado de entradas
   na raiz. O próprio repositório documenta que existem fluxos de trabalho
   longos e legítimos (`docs/architecture.md`), e a única saída era quebrar a
   skill ou burlar o número.

Uma regra que reprova sem conseguir sustentar o julgamento ensina a contornar a
verificação, não a escrever melhor.

## Decisão

Cada achado carrega a regra que o produziu, e há três níveis:

- **Erro**: reprova. O resto das regras — nome divergente, link quebrado,
  arquivo órfão, script sem docstring, import fora do permitido, cópias
  dessincronizadas.
- **Aviso heurístico**: `description-trigger` e `description-filler`. Aparecem
  no relatório e não reprovam. Chamam a atenção de quem escreve; não decidem no
  lugar dessa pessoa.
- **Limite dispensável**: `body-lines`, `name-terms`, `name-chars`,
  `description-min`, `description-max`, `top-level-entry`, `skill-size`. A
  skill declara a dispensa no frontmatter, com motivo:

```yaml
metadata:
  waivers:
    body-lines: O processo tem sete etapas verificáveis e quebrar a skill perderia o estado entre elas.
```

A dispensa é verificada: só vale para regra dispensável e com pelo menos 30
caracteres de motivo. Dispensa de regra essencial, dispensa sem motivo e
dispensa declarada sem a regra ter sido acionada são **erros** — o frontmatter
não pode mentir sobre o que a skill faz.

O perfil `rigoroso` trata aviso como falha. Quem publica para a máquina de
outra pessoa paga o preço cheio; quem está explorando, não.

`tests/` passa a ser entrada prevista na raiz da skill e não entra no pacote
distribuído: o teste serve a quem edita a skill, não a quem a instala.

## Consequências

- O relatório distingue "corrija isto" de "olhe isto": uma dispensa aparece com
  o motivo ao lado, legível em revisão de pull request.
- Contornar um limite deixa rastro no frontmatter, revisável, em vez de virar
  uma skill artificialmente picada em duas.
- `--strict` (e o perfil `rigoroso`) restauram o comportamento antigo quando
  ele é o desejado.
- A API de `check_skills` passou de `list[str]` para `list[Finding]`. Quem
  consome precisa filtrar por `is_error`; `package_skills` e `smoke_bundles`
  já o fazem.
