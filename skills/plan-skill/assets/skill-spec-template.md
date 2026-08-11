<!--
Modelo de especificação de skill. Salve como docs/skills/<nome>.md.
Remova todos os comentários e textos entre colchetes ao preencher.
-->

# Especificação — [nome-da-skill]

## Identidade

- **name**: `[kebab-case, verbo + objeto, até 5 termos]`
- **description**: [uma linha: o que faz + quando usar + quando não usar]
- **Skills vizinhas**: [skills existentes com gatilho parecido e como se diferenciam]

## Tarefa

[O trabalho que a skill executa, do gatilho ao resultado, em até cinco linhas.]

## Gatilhos

| Frase do usuário | Deve acionar? | Por quê |
| ---------------- | ------------- | ------- |
| [frase real]     | sim           | [motivo] |
| [frase real]     | sim           | [motivo] |
| [frase vizinha]  | não           | [skill que deveria atender] |

## Entradas

- [Arquivo, caminho ou dado obrigatório e seu formato]
- [Dado opcional e o padrão quando ausente]

## Saída

- **Artefato**: [arquivo, texto ou alteração produzida]
- **Local**: [onde fica]
- **Formato**: [estrutura, seções, esquema]

## Processo

1. [Passo]
2. [Passo — marque com `script:` os que serão executados por código]
3. [Ponto de confirmação com o usuário, se houver]

## Componentes

| Componente | Caminho | Papel |
| ---------- | ------- | ----- |
| Script     | `scripts/[nome].py` | [passo determinístico que ele executa] |
| Asset      | `assets/[nome]` | [modelo ou dado que a skill carrega] |
| Referência | `reference/[nome].md` | [conhecimento consultado sob demanda] |

## Limites

- Nunca: [ação proibida]
- Confirmar antes de: [ação irreversível ou externa]
- Dados sensíveis: [como tratar]

## Critérios de aceite

- CA-01: [resultado observável que um revisor consegue conferir]
- CA-02: [comportamento em caso de entrada inválida]
- CA-03: [comportamento em caso de dado ausente]

## Fora do escopo

- [Capacidade adjacente que esta skill não cobre e por quê]
