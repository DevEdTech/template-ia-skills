---
name: package-skill
description: Empacota skills validadas em .zip determinístico com manifesto e entrega as instruções de instalação para Claude Code, Agent SDK, API e outros repositórios. Use quando uma skill pronta precisar ser distribuída, publicada ou entregue a outro time.
---

# Empacotar skill

## Objetivo

Transformar uma skill aprovada em um artefato instalável, com identidade
estável (`sha256`) e instruções de instalação para o destino escolhido.

## Quando usar

- A skill passou em `review-skill` e em `evaluate-skill`.
- Alguém pediu a skill para usar em outro projeto, time ou produto.

## Quando não usar

- Skill ainda em desenvolvimento neste repositório: ela já é carregada pelas
  cópias em `.claude/skills` (`python scripts/dev.py sync-skills`).

## Processo

1. Confirme que `python scripts/dev.py validate` está verde. Sem isso, não empacote.
2. Gere os pacotes: `python scripts/dev.py package` (ou `--skill <nome>` para uma só).
3. Verifique o artefato fora do repositório: `python scripts/dev.py smoke-bundles`.
4. Abra `dist/manifest.json` e confira, para cada skill, o `sha256`, o tamanho e
   a lista de arquivos — nada de arquivo inesperado, nada de dado sensível.
5. Escolha o destino e siga [reference/install-targets.md](reference/install-targets.md).
6. Informe a quem recebe: nome da skill, o que ela faz, quando dispara,
   dependências (se houver `requirements.txt`) e o `sha256` do pacote.
7. Registre a entrega: versão do repositório (commit), destino e data.

## Regras

- Não empacote skill com erro de verificação — o pacote é o que roda na máquina de outra pessoa.
- Não inclua `.env`, credenciais, dados de cliente ou caminhos pessoais.
- Não edite o zip manualmente: o pacote é gerado, e o `sha256` prova o conteúdo.
- Republicou? Gere pacote novo e informe o novo `sha256`; não sobrescreva silenciosamente.

## Resultado esperado

- Pacotes em `dist/` e `dist/manifest.json` atualizado.
- Saída do smoke dos pacotes.
- Instruções de instalação para o destino escolhido.
- Resumo da entrega: skill, `sha256`, commit e destino.
