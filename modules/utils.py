import os 
import re 

def find_book_file(directory: str) -> tuple[str | None, str | None]:
    """Encontra o primeiro arquivo .docx no diretório especificado."""
    try: 
        files = [f for f in os.listdir(directory) if f.endswith('.docx')]
        if not files:
            print(f"ERRO: Nenhum arquivo .docx encontrado no diretório '{directory}'.")
            return None, None 
        if len(files) > 1:
            print(f"AVISO: Mais de um arquivo .docx encontrado. Usando o primeiro: '{files[0]}'.")

        file_path = os.path.join(directory, files[0])
        book_name = os.path.splitext(files[0])[0]
        return file_path, book_name 
    
    except FileNotFoundError:
        print(f"ERRO: O diretório '{directory}' não foi encontrado.")
        return None, None

def extrair_numeros_ord(nome_arquivo):
    """
    Função auxiliar para extrair números de unidade e capítulo para ordenação.
    Agora aceita tanto 'U1_C1' quanto 'U1-C1'.
    """
    match = re.search(r'U(\d+)[-_]C(\d+)', nome_arquivo)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return (0, 0)