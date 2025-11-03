CREATE DATABASE embeddings_db
  WITH OWNER = postgres
  ENCODING = 'UTF8'
  LC_COLLATE = 'pt_BR.UTF-8'
  LC_CTYPE = 'pt_BR.UTF-8'
  TEMPLATE template0;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS langchain_pg_collection (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE,
    cmetadata JSONB
);

CREATE TABLE IF NOT EXISTS langchain_pg_embedding (
    id TEXT PRIMARY KEY,
    collection_id UUID REFERENCES langchain_pg_collection(uuid) ON DELETE CASCADE,
    embedding VECTOR(3072),
    document TEXT,
    cmetadata JSONB,
    custom_id TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS formulas_map (
    id SERIAL PRIMARY KEY,
    book_name TEXT NOT NULL,
    unit INT NOT NULL,
    chapter INTEGER NOT NULL,
    formula TEXT NOT NULL,
    concepts JSONB,
    description TEXT,
    source_chapter TEXT,
    createad_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_formulas_book_unit_chapter
    ON formulas_map (book_name, unit, chapter);

CREATE INDEX idx_formulas_concepts_gin
    ON formulas_map USING GIN (concepts);