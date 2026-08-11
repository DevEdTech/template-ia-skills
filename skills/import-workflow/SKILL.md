---
name: import-workflow
description: Converte processo já existente — prompt salvo, runbook, checklist, planilha de passos ou documento interno — em uma skill estruturada, testável e autocontida. Use quando o conhecimento já está escrito fora do repositório e precisa virar skill.
---

# Importar processo

## Objetivo

Reconstruir, a partir de material existente, o que a skill precisa fazer — sem
inventar processo novo e sem perder regra que hoje só está na cabeça de alguém.

## Quando usar

- Existe um prompt longo que alguém cola repetidamente.
- Existe runbook, checklist, POP ou tutorial interno de um processo repetitivo.
- Uma pessoa executa o processo há tempos e quer transferi-lo para o agente.

## Quando não usar

- Não existe processo escrito nem praticado: use `plan-skill`.
- O processo já é uma skill e precisa de ajuste: use `refactor-skill`.

## Processo

1. Reúna o material bruto: prompts, documentos, planilhas, exemplos de entrada e
   de saída reais. Peça os exemplos de saída — eles definem o resultado melhor
   que qualquer descrição.
2. Preencha o inventário de [assets/inventory-template.md](assets/inventory-template.md), classificando cada trecho do
   material em: **instrução** (vai para o `SKILL.md`), **conhecimento**
   (vai para `reference/`), **passo determinístico** (vira script),
   **modelo** (vira asset) ou **descarte** (obsoleto, duplicado ou específico de uma pessoa).
3. Marque as lacunas: regra citada sem explicação, exceção sem critério, passo
   que depende de acesso que o agente não tem.
4. Pergunte ao dono do processo apenas sobre as lacunas — não repita o que o
   material já responde.
5. Reescreva os passos no imperativo, na ordem real de execução, removendo
   histórico, justificativas e enfeite.
6. Separe o que é decisão do agente do que é regra fixa: regra fixa vira script
   ou lista em `reference/`; decisão fica como critério explícito no `SKILL.md`.
7. Apresente o inventário e o esboço de `name` + `description` e peça **aprovação
   explícita** antes de criar arquivos.
8. Com a aprovação, siga para `create-skill`.

## Regras

- Não mude o processo enquanto o importa: registre as melhorias como propostas separadas.
- Não copie dados de cliente, credenciais ou anexos internos para dentro da skill.
- Todo trecho do material precisa de destino: instrução, conhecimento, script, modelo ou descarte declarado.
- Quando o material se contradiz, mostre o conflito e peça a decisão; não escolha sozinho.

## Resultado esperado

- Inventário preenchido, sem trecho sem destino.
- Lista de lacunas com as respostas obtidas.
- `name` e `description` propostos.
- Aprovação registrada e próximo passo (`create-skill`).
