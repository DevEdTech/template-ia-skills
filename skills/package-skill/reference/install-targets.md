# Destinos de instalação

Cada destino carrega a skill de um jeito. O conteúdo é sempre o mesmo: a pasta
`<nome>/` com o `SKILL.md` na raiz.

## 1. Agente de código, no projeto (recomendado para times)

Copie a pasta da skill para o diretório de skills do projeto que vai usá-la:

```
<projeto>/.claude/skills/<nome>/SKILL.md
```

Quem clona o repositório recebe a skill junto. É o caminho com menor chance de
divergência entre as máquinas do time.

## 2. Agente de código, no usuário

Para uso pessoal, fora de um projeto específico:

```
~/.claude/skills/<nome>/SKILL.md
```

No Windows: `%USERPROFILE%\.claude\skills\<nome>\SKILL.md`.

A skill passa a valer para todas as pastas em que o agente for aberto — o que
também significa que o gatilho dela concorre em qualquer contexto. Prefira o
destino de projeto quando a skill for específica de um domínio.

## 3. Outro repositório, versionado

Extraia o pacote dentro do repositório de destino e versione os arquivos:

```bash
unzip dist/<nome>.zip -d <repo-destino>/.claude/skills/
```

Combine com quem mantém o repositório de destino como as atualizações chegarão:
o pacote é uma cópia, e cópias divergem. Registre no destino de onde a skill
veio (repositório e commit).

## 4. Agent SDK / aplicação própria

Aponte o carregador de skills da aplicação para o diretório onde a pasta foi
extraída. O contrato é o mesmo: uma pasta por skill, `SKILL.md` na raiz, com
`name` e `description` no frontmatter.

## 5. API

Envie o `.zip` gerado em `dist/` pelo mecanismo de arquivos/containers da API que
a aplicação usa e referencie a skill pelo nome. Como o formato do envio muda com
a versão da API, confirme o procedimento na documentação vigente antes de
prometer prazo — o pacote deste repositório já está no formato de pasta esperado.

## Antes de entregar, em qualquer destino

- A skill passou em `python scripts/dev.py validate`.
- O `smoke-bundles` provou que os scripts rodam fora do repositório.
- O `sha256` do manifesto foi informado a quem recebe.
- Dependências de terceiros (se houver `requirements.txt`) foram combinadas com o destino.
- O nome não colide com skills já instaladas no destino.
