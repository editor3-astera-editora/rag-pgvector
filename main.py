import os
import shutil
from modules.logging_config import setup_logging, get_logger
from modules.ingestion import extract_chapters_from_word, get_text_chunks
from modules.rag_builder import create_chapter_vector_store
from modules.preprocessar_formulas import criar_mapa_de_formulas
from modules.generation import _call_llm_with_tracking

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    setup_logging()
    logger = get_logger(__name__)
    logger.info("==== Iniciando processamento em lote de livros ====")

    base_dir = os.path.join(os.getcwd(), "livros_originais")
    feitos_dir = os.path.join(os.getcwd(), "feitos")
    os.makedirs(feitos_dir, exist_ok=True)

    livros = [f for f in os.listdir(base_dir) if f.endswith(".docx")]
    if not livros:
               
        logger.warning(f"Nenhum arquivo .docx encontrado em {base_dir}.")
        return

    for livro in livros:
        file_path = os.path.join(base_dir, livro)
        book_name = os.path.splitext(livro)[0]
        logger.info(f"\n===== Iniciando processamento do livro: {book_name} =====")

        try:
            chapters = extract_chapters_from_word(file_path)
            logger.info(f"{len(chapters)} capítulos extraídos do livro {book_name}.")

            criar_mapa_de_formulas(file_path, book_name)

            for chapter in chapters:
                unit = chapter["unit"]
                chap = chapter["chapter"]
                text = chapter["text"]
                chunks = get_text_chunks(text)
                try:
                    create_chapter_vector_store(chunks, book_name, unit, chap)
                    logger.info(f"Vetores criados para U{unit}-C{chap}.")
                except Exception as e:
                    logger.error(f"Erro ao criar vetores U{unit}-C{chap}: {e}")

            destino = os.path.join(feitos_dir, livro)
            shutil.move(file_path, destino)
            logger.info(f"Livro {livro} movido para {destino}")

        except Exception as e:
            logger.exception(f"Erro durante o processamento de {book_name}: {e}")
            continue

        logger.info(f"===== Livro {book_name} concluído com sucesso =====")

    logger.info("==== Todos os livros foram processados ====")


if __name__ == "__main__":
    main()
