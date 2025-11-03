O projeto implementa um pipeline que:

1. Lê e divide livros `.docx` em capítulos.
2. Extrai e mapeia **fórmulas** com auxílio de um LLM (OpenAI)
3. Salva as fórmulas em JSON e no PostgreSQL
4. Cria embeddings dos textos e os armazena em um **pgVector**
5. Usa logs para rastreio de tokens/custos das chamadas à API

- `prompts.py`: Define o prompt `FORMULA_MAPPING_PROMPT`, que instrui o LLM a extrair fórmulas gerais e conceitos associados ao texto

- `utils.py`: Localiza o arquivo `.docx` e extrai números de unidade e capítulos para ordenação

- `ingetion.py`: Lê o `.docx`, remove macações como `<...>`, e divide o conteúdo em capítulos (via regex Unidade X - Capítulo Y), além de oferecer `get_text_chunks()` para dividir o texto em pedaços semânticos.

- `generation.py`: Implementa `_call_llm_with_tracking()`, que formata o prompt, chama o modelo `ChatOpenAI` e coleta dados de custo/token.

- `preprocessar_formulas.py`: Coordena a extração e o mapeamento de fórmulas: lê capítulos, envia cada um ao LLM, decodifica JSON, salva em arquivo e insere no banco PostgreSQL (`formulas_map`);

- `rag_builder.py` Cria e carrega vetores persistentes no PostgreSQL via `langchain_postgres.PGVector`, armazenando embeddings e metadados (livro, unidade, capítulo).

- `loggin_config.py`: Configura logs detalhados em arquivo + console e fornece o `PerformanceLogger`para medir duração de operações

Em resumo, o fluxo de atividades é:

Word (.docx)
 └── ingestion.extract_chapters_from_word()
      └── geração de chunks
           └── preprocessar_formulas.criar_mapa_de_formulas()
                ├── _call_llm_with_tracking(FORMULA_MAPPING_PROMPT)
                ├── JSON → PostgreSQL
                └── JSON → arquivo local
                     └── rag_builder.create_chapter_vector_store()
