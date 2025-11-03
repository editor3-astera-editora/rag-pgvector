Esse projeto processa os teóricos da coleção InovaTech em formato `.docx`, extrai capítulos, gera embeddings semânticos e mapeia fórmulas gerais utilizando os modelos **OpenAI GPT-4o** e **text-embedding-3-large**. O resultado é um banco vetorial persistente em **PostgreSQL + pgVector**, integrando textos e fórmulas pronto para ser consultado em um sistema RAG (retrieval-augmented generation).

## Conhecendo a estrutura dos livros InovaTech

Os livros InovaTech são separados em 4 unidades, cada uma dessas 4 unidades possuindo 4 capítulos cada. Ao longo do documento `.docx`, essa separação entre unidades e capítulos segue o padrão:

```
Unidade X - Capítulo Y
Título do capítulo Y
```

e isso é detectado utilizando o Regex ```^\s*Unidade\s+(\d+)\s*[-–]\s*Capítulo\s+(\d+)(?:\s*[-:]?\s+(.+))?$```

## Estrutura do projeto

```
.
├── config.py
├── main.py
├── schema.sql
├── modules/
│   ├── generation.py
│   ├── ingestion.py
│   ├── logging_config.py
│   ├── preprocessar_formulas.py
│   ├── prompts.py
│   ├── rag_builder.py
│   └── utils.py
├── livros_originais/
├── resultados/
└── logs/
```

### Fluxo de processamento 

1. `main.py`:
     - Varre a pasta `livros_originais/` em busca de arquivos `.docx`;
     - Extrai capítulos e unidades (ex: "Unidade 3 - Capítulo 2")
     - Chama o módulo `preprocessar_formulas.py` para gerar o mapa de fórmulas;
     - Chama `rag_builder.py` para gerar embeddings e armazenar no pgVector
       
 2. `ingestion.py`
      - Extrai texto bruto do `.docx`;
      - Remove comentários `<...>` que podem atrapalhar a qualidade dos embeddings gerados;
      - Divide o texto em chunks semânticos com `RecursiveCharacterTextSplitter`.

 3. `generation.py`
       - Chama a API OpenAI (`gpt-4o`) para geração controlada de conteúdo;
       - Rastrei o uso de tokens e custos com `get_openai_callback()`.

 4. `preprocessar_formulas.py`
        - Usa o prompt `FORMULA_MAPPING_PROMPT` para descrever as fórmulas detectadas;
        - Salva o resultado em JSON e no banco PostgreSQL (tabela `formulas_map`).

5. `rag_builder.py`
        - Gera embeddings com `text-embedding-3-large` e persite via `langchain_postgres.PGVector`.

## Banco de dados e codificação UTF-8

Caso você esteja utilizando windows, é obrigatório setar o banco de dados como UTF-8 para evitar erros de codificação ao processar textos e fórmulas com acentos, símbolos matemáticos e caracteres especiais. O arquivo `schema.sql` já define corretamente essa configuração:

```
CREATE DATABASE embeddings_db
  WITH OWNER = postgres
  ENCODING = 'UTF8'
  LC_COLLATE = 'pt_BR.UTF-8'
  LC_CTYPE = 'pt_BR.UTF-8'
  TEMPLATE template0;
```

# Criando o banco UTF-8 no Windows (passo a passo)

1. Abra o psql:

```
psql -U postgres
```

2. Execute o SQL abaixo (ou o conteúdo do arquivo schema.sql):

```
CREATE DATABASE embeddings_db
  WITH OWNER = postgres
  ENCODING = 'UTF8'
  LC_COLLATE = 'pt_BR.UTF-8'
  LC_CTYPE = 'pt_BR.UTF-8'
  TEMPLATE template0;
```

3. Confirme que o banco foi criado com codificação UTF-8:

```
\l embeddings_db
```

4. Habilite as extensões:

```
\c embeddings_db
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
```

5. Crie as demais tabelas presentes em `schema.sql`.

## Exemplo de `.env`
```
OPENAI_API_KEY="sk-..."
PSYCOPG_DB_URI=postgresql://postgres:SUASENHA@localhost:5432/embeddings_db
PGVECTOR_DB_URI=postgresql+psycopg://postgres:SUASENHA@localhost:5432/embeddings_db
``` 

## Execução do pipeline

1. Crie o ambiente virtual:

```
python -m venv .venv
.venv\Scripts\activate
```

2. Instale as dependências

```
pip install -r requirements.txt
```

3. Execute o processamento:

```
python main.py
```

4. Verifique os resultados:
    - Vetores no banco: `langchain_pg_embedding`
    - Fórmulas extraídas: `formulas_map`
    - Logs: `logs/processamento_*.log`
    - JSONs gerados: `resultados/<nome_do_livro>/mapa_de_formulas.json`
  

## Estrutura das tabelas principais 

| Tabela                     | Descrição                             | Campos Relevantes                                     |
| -------------------------- | ------------------------------------- | ----------------------------------------------------- |
| **langchain_pg_embedding** | Armazena embeddings e chunks de texto | `embedding VECTOR(3072)`, `document`, `cmetadata`     |
| **formulas_map**           | Armazena fórmulas mapeadas por LLM    | `book_name`, `unit`, `chapter`, `formula`, `concepts` |

## Por que usar `VECTOR(3072)` no pgVector?

O campo `embedding VECTOR(3072)` no banco é **diretamente determinado pelo modelo de embeddings usado** nesse projeto, o `text-embedding-3-large` da OpenAI.

### O que isso significa?

Cada texto (chunk) processado gera um vetor numérico que representar semanticamente seu conteúdo. O tamanho desse vetor (dimensionalidade) depende do modelo usado:

| Modelo                   | Dimensão do Vetor | Precisão                    | Custo aproximado | Uso recomendado             |
| ------------------------ | ----------------- | --------------------------- | ---------------- | --------------------------- |
| `text-embedding-3-small` | 1536              | Boa                         | Mais barato      | Casos leves, FAQs           |
| `text-embedding-3-large` | **3072**          | **Alta precisão semântica** | Mais caro        | Conteúdos longos e técnicos |

O parâmetro `VECTOR(3072)` no Postgres informa ao pgVector quantos valores float4 serão armazenados em cada embedding. Se o tamanho não corresponder ao do modelo, o Postgres retornará erro ao inserir os dados. O vetor salvo no banco de dados já é normalizado, ou seja, seu módulo

\[ ||v||_{2} = \sqrt{\sum_{i=1}^{3072}v_{i}^{2}} = 1 \]

Essa normalização apesar de custosa computacionalmente é importante para que o modelo não dê peso indevido a embeddings de maior magnitude e não retorne resultados falsos.
