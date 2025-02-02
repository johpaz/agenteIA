import os
import json

def load_processed_pdf(file_name: str) -> dict:
    """
    Carga un PDF procesado desde la carpeta 'data/processed_pdfs/'.
    Args:
        file_name (str): Nombre del archivo procesado (sin extensión).
    Returns:
        dict: Contenido estructurado del PDF.
    """
    file_path = os.path.join("data", "processed_pdfs", f"{file_name}.json")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo {file_name}.json no existe en la carpeta 'data/processed_pdfs/'.")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)