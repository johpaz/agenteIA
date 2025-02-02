def split_text_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    Divide un texto largo en fragmentos más pequeños con un cierto grado de solapamiento.
    Args:
        text (str): Texto a dividir.
        chunk_size (int): Tamaño máximo de cada fragmento.
        overlap (int): Número de caracteres que se solapan entre fragmentos.
    Returns:
        list: Lista de fragmentos de texto.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap  # Avanzar con solapamiento
    return chunks