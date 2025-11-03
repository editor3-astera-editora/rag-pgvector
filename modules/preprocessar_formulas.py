import sys
import os
import re
import json
import config
import psycopg2
from psycopg2.extras import execute_values
from unidecode import unidecode

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .prompts import FORMULA_MAPPING_PROMPT
from .ingestion import extract_chapters_from_word
from .generation import _call_llm_with_tracking

def salvar_formulas_no_banco(mapa_de_formulas: list, book_name: str):
    """
    Salva as fórmulas processadas no banco de dados PostgreSQL.
    """

    if not mapa_de_formulas:
        print(" Nenhuma fórmula para salvar no banco.")
        return

    try:
        conn = psycopg2.connect(config.PSYCOPG_DB_URI)
        conn.set_client_encoding('UTF8')
        cur = conn.cursor() 

        registros = []
        for item in mapa_de_formulas:
            source = item.get("source_chapter", "U0-C0")
            match = re.match(r"U(\d+)-C(\d+)", source)
            unit, chap = (int(match.group(1)), int(match.group(2))) if match else (0, 0)

            registros.append((
                book_name,
                unit,
                chap,
                item.get("formula", ""),
                json.dumps(item.get("concepts", [])),
                item.get("description", ""),
                source
            ))

        sql = """
        INSERT INTO formulas_map
        (book_name, unit, chapter, formula, concepts, description, source_chapter)
        VALUES %s;
        """

        registros_limpos = []
        for r in registros:
            r_limpo = tuple(
                unidecode(c) if isinstance(c, str) else c
                for c in r
            )
            registros_limpos.append(r_limpo)

        execute_values(cur, sql, registros_limpos)
        conn.commit()
        cur.close()
        conn.close()
        print(f" {len(registros)} fórmulas salvas no banco de dados PostgreSQL.")
    except Exception as e:
        print(f" Erro ao salvar fórmulas no banco: {str(e).encode('utf-8', 'ignore').decode('utf-8')}")


def criar_mapa_de_formulas(docx_path: str, book_name: str):
    """
    Lê um livro, extrai/filtra/mapeia todas as fórmulas e salva um mapa em JSON.
    """
    print("="*80)
    print(f"INICIANDO PRÉ-PROCESSAMENTO DE FÓRMULAS PARA O LIVRO: {book_name}")
    print("="*80)

    chapters = extract_chapters_from_word(docx_path)
    if not chapters:
        return

    mapa_de_formulas_completo = []
    
    for chapter_data in sorted(chapters, key=lambda d: (d['unit'], d['chapter'])):
        unit, chap, title, chapter_text = chapter_data.values()
        capitulo_id = f"U{unit}-C{chap}"
        print(f"\n--- Processando Capítulo: {capitulo_id}: {title} ---")

        if not chapter_text.strip():
            print("   - Capítulo vazio. Pulando.")
            continue

        input_vars = {"chapter_text": chapter_text}
        response_str, _ = _call_llm_with_tracking(FORMULA_MAPPING_PROMPT, input_vars, temperature=0.0)

        try:
            json_match = re.search(r'\[.*\]', response_str, re.DOTALL)
            if json_match:
                formulas_do_capitulo = json.loads(json_match.group(0))
                if formulas_do_capitulo:
                    print(f"   - {len(formulas_do_capitulo)} fórmulas encontradas e mapeadas.")
                    for formula_info in formulas_do_capitulo:
                        formula_info['source_chapter'] = capitulo_id
                    mapa_de_formulas_completo.extend(formulas_do_capitulo)
                else:
                    print("   - Nenhuma fórmula geral encontrada neste capítulo.")
        except json.JSONDecodeError:
            print(f"   - AVISO: Não foi possível decodificar a resposta JSON: '{response_str}'")

    pasta_livro_resultado = os.path.join(config.PASTA_RESULTADOS, book_name)
    os.makedirs(pasta_livro_resultado, exist_ok=True)
    caminho_mapa = os.path.join(pasta_livro_resultado, "mapa_de_formulas.json")

    with open(caminho_mapa, "w", encoding="utf-8") as f:
        json.dump(mapa_de_formulas_completo, f, ensure_ascii=False, indent=2)

    print(f"\n JSON salvo em: {caminho_mapa}")
    print("Tentando salvar as fórmulas no banco de dados...")

    salvar_formulas_no_banco(mapa_de_formulas_completo, book_name)

    print("\n" + "="*80)
    print(f"SUCESSO! Mapa de Fórmulas salvo em: {caminho_mapa} e registrado no banco.")
    print("="*80)
