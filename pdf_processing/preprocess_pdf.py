import os
import re
from PyPDF2 import PdfReader

def clean_text(text: str) -> str:
    """
    Limpia el texto eliminando caracteres innecesarios y formateándolo.
    Args:
        text (str): Texto extraído del PDF.
    Returns:
        str: Texto limpio.
    """
    # Eliminar múltiples espacios y saltos de línea consecutivos
    text = re.sub(r"\s+", " ", text)
    # Eliminar encabezados/pies de página comunes
    text = re.sub(r"^\d+$", "", text, flags=re.MULTILINE)  # Números solos (números de página)
    text = re.sub(r"^\s*-\s*$", "", text, flags=re.MULTILINE)  # Guiones solos
    return text.strip()

def extract_sections(text: str) -> list:
    """
    Divide el texto en secciones lógicas (por ejemplo, párrafos o capítulos).
    Args:
        text (str): Texto limpio.
    Returns:
        list: Lista de secciones.
    """
    # Dividir por puntos seguidos de mayúsculas (indicadores de nuevos párrafos o secciones)
    sections = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    return [section.strip() for section in sections if section.strip()]

def preprocess_pdf(file_path: str) -> dict:
    """
    Procesa un PDF y lo transforma en un formato estructurado.
    Args:
        file_path (str): Ruta del archivo PDF.
    Returns:
        dict: Contenido estructurado del PDF.
    """
    # Leer el PDF
    reader = PdfReader(file_path)
    raw_text = ""
    for page in reader.pages:
        raw_text += page.extract_text()

    # Limpiar el texto
    cleaned_text = clean_text(raw_text)

    # Dividir en secciones
    sections = extract_sections(cleaned_text)

    # Crear un diccionario estructurado
    processed_data = {
        "file_name": os.path.basename(file_path),
        "sections": sections,
        "metadata": {
            "total_pages": len(reader.pages),
            "total_sections": len(sections),
        }
    }
    return processed_data

def save_processed_data(processed_data: dict, output_dir: str):
    """
    Guarda el contenido procesado en un archivo JSON.
    Args:
        processed_data (dict): Contenido estructurado del PDF.
        output_dir (str): Directorio donde guardar el archivo.
    """
    os.makedirs(output_dir, exist_ok=True)
    file_name = processed_data["file_name"].replace(".pdf", ".json")
    output_path = os.path.join(output_dir, file_name)
    with open(output_path, "w", encoding="utf-8") as f:
        import json
        json.dump(processed_data, f, ensure_ascii=False, indent=4)
    print(f"Datos procesados guardados en: {output_path}")