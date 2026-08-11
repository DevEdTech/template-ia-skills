# Arquitetura

Este documento descreve como as skills deste repositório são organizadas e quais
fronteiras o `validate` faz valer.

## Princípios

- A skill é a unidade de entrega: uma pasta, autocontida, instalável em qualquer agente.
- Divulgação progressiva: o agente carrega o mínimo para decidir e só então busca detalhe.
- O que é determinístico vira script; o que é julgamento fica em instrução.
- Nome e descrição são interface pública: é por eles que a skill é escolhida.
- Nada de dependência entre skills — cópias divergem, imports quebram na distribuição.
- Simplicidade primeiro: só adicione partes (scripts, assets, referências) quando houver necessidade real.

## Layout do repositório

```
skills/                     # skills canônicas (fonte da verdade)
└── summarize-csv/
    ├── SKILL.md            # frontmatter + processo executável
    ├── scripts/            # passos determinísticos em Python (stdlib)
    ├── assets/             # modelos preenchidos pela skill
    └── reference/          # conhecimento carregado sob demanda
evals/                      # cenários de gatilho e execução, um JSON por skill
scripts/                    # ferramentas do template (runner e verificações)
tests/                      # testes das ferramentas e dos scripts das skills
docs/                       # esta documentação
dist/                       # pacotes gerados (ignorado pelo Git)
.claude/skills/             # cópia gerada, lida pelo agente durante o desenvolvimento
.agents/skills/             # cópia gerada, para agentes que usam esse diretório
```

As cópias em `.claude/skills` e `.agents/skills` são **geradas** por
`python scripts/dev.py sync-skills`. Editar a cópia é perder o trabalho na próxima
sincronização.

## As quatro camadas de uma skill

| Camada | Onde | Carregada quando | Contém |
| ------ | ---- | ---------------- | ------ |
| Metadados | frontmatter do `SKILL.md` | sempre, em toda sessão | `name` e `description` |
| Processo | corpo do `SKILL.md` | quando a skill é acionada | passos, regras, limites |
| Referência | `reference/*.md` | quando o passo aponta para ela | tabelas, exceções, detalhe extenso |
| Execução | `scripts/*.py` | quando o agente roda o comando | contagem, parsing, validação, conversão |

O custo cresce a cada camada: metadados ficam no contexto o tempo todo, o corpo
entra inteiro quando a skill dispara, a referência entra sob demanda e o script
não entra no contexto — ele roda. Coloque cada conteúdo na camada mais barata
que resolve.

## Fronteiras verificadas

`python scripts/dev.py check-skills` reprova:

- entrada não prevista na raiz da skill (só `SKILL.md`, `scripts/`, `assets/`, `reference/`, `requirements.txt`);
- frontmatter com chave desconhecida, `name` divergente da pasta ou fora do padrão;
- descrição fora dos limites de tamanho, sem indicação de quando usar, ou começando com enchimento;
- `SKILL.md` acima de 500 linhas ou sem título;
- link relativo quebrado, caminho absoluto ou link apontando para fora da skill;
- arquivo órfão em `scripts/`, `assets/` ou `reference/`;
- script sem docstring, fora de `snake_case`, com nome repetido em outra skill ou importando pacote não declarado;
- skill acima do limite de tamanho;
- cópias em `.claude/skills` e `.agents/skills` divergentes.

`python scripts/dev.py smoke-bundles` vai além: extrai o pacote em um diretório
temporário, revalida a skill fora do repositório e roda cada script com
`python -I ... --help`. Um script que só funciona "aqui" falha nessa etapa.

## Onde cada coisa mora

**No `SKILL.md`** — o que vale em toda execução: objetivo, quando usar, quando
não usar, passos, pontos de confirmação, resultado esperado.

**Em `reference/`** — o que é consultado em parte dos casos: tabelas de
formatação, listas de exceções, regras de domínio extensas, exemplos longos.
Cada arquivo responde a uma pergunta específica e é citado do passo que precisa dele.

**Em `assets/`** — o que a skill preenche ou copia: modelos de documento,
esquemas, formulários, arquivos de configuração de exemplo.

**Em `scripts/`** — o que não pode variar: contagem, leitura de formato,
validação de estrutura, conversão, geração determinística. Se duas execuções da
mesma entrada podem dar resultados diferentes, o passo pertence a um script.

## Nomes de script

Os nomes de arquivo de script são únicos no repositório inteiro. A regra tem
duas razões: o typecheck roda em uma passada só sobre todas as skills, e um
`scripts/main.py` em cada skill deixa a documentação ambígua. Prefira o nome que
descreve o passo: `summarize_csv.py`, `validate_contract_fields.py`.

## Dependências

O padrão é **zero dependências**: os scripts usam apenas a biblioteca padrão,
para que a skill funcione onde quer que o agente esteja. Quando não houver
alternativa, declare em `skills/<nome>/requirements.txt`, justifique no pull
request e registre a decisão em `docs/decisions/`. Skills com dependência não
são executadas no smoke — a instalação passa a ser responsabilidade do destino.

## Fluxos de trabalho complexos

Skills que operam processos longos seguem quatro regras:

1. **Etapas com artefato** — cada etapa produz algo verificável (arquivo, resumo,
   lista), para que a próxima possa começar sem reler a conversa inteira.
2. **Estado em arquivo** — o progresso fica em um arquivo de trabalho, não na
   memória da conversa. Sessão nova retoma de onde parou.
3. **Falha declarada** — cada passo diz o que fazer quando dá errado: repetir,
   pular, perguntar ou parar.
4. **Confirmação antes do irreversível** — apagar, mover, enviar, publicar e
   gastar dinheiro exigem aprovação explícita.

## Ciclo de vida

```
plan-skill → create-skill → evaluate-skill → review-skill → package-skill
                  ↑                              |
                  └────────── refactor-skill ────┘
```

`import-workflow` entra antes de `create-skill` quando o processo já existe fora
do repositório. `document-skills` fecha qualquer mudança que altere o conjunto de skills.
