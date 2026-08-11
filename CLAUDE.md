# Contexto do projeto para o Claude Code

Leia e siga o `AGENTS.md`.

Depois leia, quando relevante:

1. `docs/architecture.md` (anatomia e fronteiras de uma skill)
2. `docs/skill-metadata.md` (nome e descrição)
3. `docs/development-process.md`
4. `docs/testing.md`
5. `docs/packaging.md` (empacotamento e distribuição)
6. os arquivos relevantes em `docs/decisions`

As skills do projeto estão disponíveis em `.claude/skills` (cópias geradas por
`python scripts/dev.py sync-skills`; edite sempre os originais em `skills/`).

Para criar uma skill:

1. use a skill de planejamento (plan-skill) e obtenha aprovação da especificação;
2. gere o esqueleto com `python scripts/dev.py new-skill`;
3. implemente com a skill create-skill, um incremento por vez;
4. execute `python scripts/dev.py validate`;
5. avalie com evaluate-skill e revise com review-skill;
6. atualize o catálogo com document-skills;
7. revise o diff final.

Não expanda o escopo, não adicione dependências, não exponha
segredos e não altere a estrutura das skills sem antes explicar a necessidade.
