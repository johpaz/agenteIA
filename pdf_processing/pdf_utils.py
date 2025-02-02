import os

def validate_pdf(file_path: str) -> bool:
    """
    Valida que un archivo sea un PDF válido.
    Args:
        file_path (str): Ruta completa del archivo.
    Returns:
        bool: True si el archivo es un PDF válido, False en caso contrario.
    """
    if not os.path.exists(file_path):
        return False
    if not file_path.lower().endswith(".pdf"):
        return False
    return True

def clean_text(text: str) -> str:
    """
    Limpia el texto extraído de un PDF eliminando caracteres innecesarios.
    Args:
        text (str): Texto a limpiar.
    Returns:
        str: Texto limpio.
    """
    # Eliminar múltiples espacios y saltos de línea consecutivos
    cleaned_text = " ".join(text.split())
    return cleaned_text