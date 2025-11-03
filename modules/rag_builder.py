import config 
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

def create_chapter_vector_store(chunks: list[str], book_name: str, unit: int, chapter: int):
    """Cria um vetor store persistente no pgVector"""
    print(" - Gerando embeddings e armazenando no banco pgVector...")

    safe_chunks = []
    for c in chunks:
        safe_chunks.append(c.encode("utf-8", "ignore").decode("utf-8", "ignore"))

    embeddings = OpenAIEmbeddings(api_key=config.OPEN_AI_API_KEY, model=config.EMBEDDING_MODEL)

    vector_store = PGVector(
        embeddings=embeddings,
        connection=config.PGVECTOR_DB_URI,   # agora no formato correto
        collection_name=config.PGVECTOR_COLLECTION,
        use_jsonb=True
    )

    metadados = [
        {"book": book_name, "unit": unit, "chapter": chapter, "chunk_index": i}
        for i, _ in enumerate(chunks)
    ]
    vector_store.add_texts(safe_chunks, metadados)

    return vector_store

def load_vector_store():
    """Carrega o vetor store persistido no Postgres."""
    embeddings = OpenAIEmbeddings(api_key=config.OPEN_AI_API_KEY, model=config.EMBEDDING_MODEL)
    return PGVector(
        connection_string=config.PGVECTOR_DB_URI,
        collection_name=config.PGVECTOR_COLLECTION,
        embedding_function=embeddings,
        use_jsonb=True
    )
