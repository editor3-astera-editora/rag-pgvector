import docx 
import re 
from typing import Dict, List, Tuple
from langchain.text_splitter import RecursiveCharacterTextSplitter
from modules.generation import _call_llm_with_tracking

def extract_chapters_from_word(docx_path: str) -> dict[tuple[int, int], str]:
    """
    Abre um arquivo .docx e o divide em capítulos com base no padrão "Unidade X - Capítulo Y."
    Retorna um dicionário com chave (unidade, capítulo) e o valor com o texto.

    Limpa comentários de formação que estão entre <*?>

    Extrai também texto de dentro de objetos de equação do word.
    """
    print(f"Lendo e dividindo o arquivo: {docx_path}")
    try: 
        document = docx.Document(docx_path)
        
        full_text_parts = []
        for child in document.element.body:
            if child.tag.endswith('p'): 
                para = docx.text.paragraph.Paragraph(child, document)
                
                xml_text_fragments = para._p.xpath(".//*[local-name()='t']/text()")
                
                full_text_parts.append("".join(xml_text_fragments))
        
        full_text = "\n".join(full_text_parts)

    except Exception as e:
        print(f"Erro ao ler o arquivo .docx: {e}")
        return []
    
    comment_pattern = re.compile(r'<.*?>')
    cleaned_text = re.sub(comment_pattern, '', full_text)
    print(" - Comentários de formatação (ex: <...> foram removidos do texto.)")

    pattern = r'^\s*Unidade\s+(\d+)\s*[-–]\s*Capítulo\s+(\d+)(?:\s*[-:]?\s+(.+))?$'
    chapter_pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)

    matches = list(chapter_pattern.finditer(cleaned_text))

    print(f"Total de capítulos encontrados: {len(matches)}")

    if not matches:
        print("AVISO: Nenhum padrão 'Unidade X - Capítulo Y' encontrado.")
        return []
    
    chapters_data = []
    for i, match in enumerate(matches):
        start_index = match.end()
        end_index = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned_text)

        chapter_text = cleaned_text[start_index:end_index].strip()

        unit_num = int(match.group(1))
        chap_num = int(match.group(2))
        title = match.group(3).strip()

        chapter_info = {
            "unit": unit_num,
            "chapter": chap_num,
            "title": title,
            "text": chapter_text
        }

        chapters_data.append(chapter_info)
        print(f" - Extraído: U{unit_num}-C{chap_num}: {title}")

    return chapters_data

def get_text_chunks(text: str) -> list[str]:
    """Divide o texto de um capítulo em chuncks semânticos."""
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size =1500, 
        chunk_overlap=250,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    print(f" - Texto dividido em {len(chunks)} chunks.")
    return chunks