# nome-do-repositorio

Um parágrafo dizendo o que o repositório entrega e para quem.

## Objetivo

O que ele resolve, em duas ou três frases. Sem marketing.

## Quando usar

- Caso de uso 1
- Caso de uso 2

## Quando NÃO usar

- Cenário fora do escopo 1
- Cenário fora do escopo 2

## Pré-requisitos

- Python 3.13 (a mesma versão em `.python-version`, no `requires-python` e no CI)
- `uv` (recomendado) — ou `pip` + `venv` como alternativa
- git
- Um agente de código

## Criar um projeto a partir do template

Seção que existe só enquanto o repositório for o template. Remova-a depois do
setup.

## Prompts iniciais

**Cenário A — "Tenho um processo repetitivo e quero virar skill"**

```text
Use a skill plan-skill para me ajudar a definir uma skill que [descreva o processo].
```

## Anatomia de uma skill

```
skills/nome-da-skill/
├── SKILL.md          # gatilho, processo e regras
├── reference/        # material carregado sob demanda
├── assets/           # modelos que a skill preenche
└── scripts/          # passos determinísticos
```

## Validação

Antes de considerar qualquer alteração pronta, rode:

```bash
python scripts/dev.py validate
```

Uma frase dizendo o que esse comando executa, em sequência.

## Comandos

| Comando                              | O que faz                         |
| ------------------------------------ | --------------------------------- |
| `python scripts/dev.py new-skill`    | Cria o esqueleto de uma skill     |
| `python scripts/dev.py check-skills` | Valida metadados e estrutura      |
| `python scripts/dev.py check-evals`  | Valida os cenários de avaliação   |
| `python scripts/dev.py package`      | Empacota cada skill em um `.zip`  |
| `python scripts/dev.py validate`     | Roda todos os portões             |

## Fluxo de trabalho

```
plan-skill → create-skill → evaluate-skill → review-skill → package-skill
```

Diga onde entram as skills de apoio e o que fecha o ciclo.

## Estrutura de pastas

```
skills/     # skills canônicas
evals/      # cenários de avaliação, um por skill
docs/       # esta documentação
scripts/    # runner e verificações cross-platform
```

## Distribuição

Como os pacotes são gerados e instalados no destino.

## Limitações conhecidas

- Limitação real 1
- Limitação real 2
