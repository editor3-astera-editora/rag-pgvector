import os 
from dotenv import load_dotenv

load_dotenv()

# Chave da API do OpenAI 
OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPEN_AI_API_KEY:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Verifique seu arquivo .env")

# Modelos a serem usados
EMBEDDING_MODEL = "text-embedding-3-large"
GENERATION_MODEL = "gpt-4o"

# Credenciais do banco pgVector
PGVECTOR_DB_URI = os.getenv("PGVECTOR_DB_URI")
PGVECTOR_COLLECTION = "chapter_embeddings"
PSYCOPG_DB_URI = os.getenv("PSYCOPG_DB_URI")

# Caminhos 
PASTA_LIVROS_ORIGINAIS = "livros_originais/"
PASTA_RESULTADOS = "resultados/"
PASTA_FEITO = "FEITO"
PASTA_FALHA = "FALHA"