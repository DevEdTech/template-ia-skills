# Empacotamento e distribuição

O artefato deste repositório é a skill instalável. Este documento descreve como
ela é empacotada e como chega ao destino.

## Formato do pacote

```bash
python scripts/dev.py package              # todas as skills
python scripts/dev.py package --skill summarize-csv
```

Cada skill vira `dist/<nome>.zip`, com a pasta da skill na raiz do arquivo:

```
summarize-csv.zip
└── summarize-csv/
    ├── SKILL.md
    ├── scripts/summarize_csv.py
    ├── assets/report-template.md
    └── reference/formatting.md
```

O zip é **determinístico**: ordem de arquivos e timestamps fixos. O mesmo
conteúdo gera os mesmos bytes, então o `sha256` do manifesto identifica a
versão da skill sem precisar de numeração própria.

## Manifesto

`dist/manifest.json` lista, para cada skill: `name`, `description`, arquivo do
pacote, arquivos incluídos, tamanho e `sha256`. Use-o para:

- conferir se entrou algum arquivo inesperado antes de distribuir;
- informar a quem recebe qual versão exata foi entregue;
- comparar o que está instalado no destino com o que existe aqui.

## Prova antes da entrega

```bash
python scripts/dev.py smoke-bundles
```

Extrai cada pacote em um diretório temporário, revalida a skill fora do
repositório e roda cada script com `python -I <script> --help`, sem acesso a
variáveis de ambiente do usuário. Uma skill que só funciona dentro deste
repositório falha aqui — que é exatamente o ponto.

Skills com `requirements.txt` são validadas, mas os scripts não são executados:
as dependências não estão instaladas no ambiente de smoke.

## Destinos de instalação

| Destino | Caminho | Quando usar |
| ------- | ------- | ----------- |
| Projeto | `<projeto>/.claude/skills/<nome>/` | skill específica de um repositório e time |
| Usuário | `~/.claude/skills/<nome>/` | uso pessoal, em qualquer pasta |
| Outro repositório | extrair o zip no destino e versionar | entrega para outro time |
| Agent SDK / aplicação | diretório de skills configurado na aplicação | produto próprio |
| API | envio do `.zip` pelo mecanismo de arquivos da API | execução hospedada |

O detalhamento de cada destino está em
`skills/package-skill/reference/install-targets.md`, para que a skill
`package-skill` consiga executar a entrega sem depender desta página.

## Versão e atualização

- O repositório é a fonte; o pacote é uma cópia. Cópias divergem.
- Ao republicar, gere pacote novo e informe o `sha256`; não sobrescreva em silêncio.
- Registre no destino de onde a skill veio: repositório e commit.
- Skill removida daqui continua instalada lá: avise quem recebeu.

## Checklist de entrega

- [ ] `python scripts/dev.py validate` verde.
- [ ] `dist/manifest.json` conferido: nenhum arquivo inesperado, nenhum dado sensível.
- [ ] `smoke-bundles` passou.
- [ ] Dependências (se houver) combinadas com o destino.
- [ ] Nome sem colisão com skills já instaladas no destino.
- [ ] `sha256` e commit informados a quem recebe.
