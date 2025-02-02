def split_text_into_chunks(text: str, chunk_size: int = 500) -> list:
    """
    Divide un texto largo en fragmentos más pequeños.
    Args:
        text (str): Texto a dividir.
        chunk_size (int): Tamaño máximo de cada fragmento.
    Returns:
        list: Lista de fragmentos de texto.
    """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def validate_training_data(training_data: list) -> bool:
    """
    Valida que los datos de entrenamiento tengan el formato correcto.
    Args:
        training_data (list): Datos de entrenamiento (pares de pregunta-respuesta).
    Returns:
        bool: True si los datos son válidos, False en caso contrario.
    """
    if not isinstance(training_data, list):
        return False
    for item in training_data:
        if not all(key in item for key in ["context", "question", "answer"]):
            return False
    return True