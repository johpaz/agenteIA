from typing import Dict, Any

def format_response(status: str, message: str, data: Any = None) -> Dict[str, Any]:
    """
    Formatea una respuesta estándar para la API.
    Args:
        status (str): Estado de la respuesta (ej. "success", "error").
        message (str): Mensaje descriptivo.
        data (Any): Datos adicionales (opcional).
    Returns:
        Dict[str, Any]: Respuesta formateada.
    """
    return {
        "status": status,
        "message": message,
        "data": data
    }

def validate_phone_number(phone_number: str) -> bool:
    """
    Valida que un número de teléfono tenga el formato correcto.
    Args:
        phone_number (str): Número de teléfono a validar.
    Returns:
        bool: True si el formato es válido, False en caso contrario.
    """
    # Ejemplo básico de validación (ajusta según tus necesidades)
    return phone_number.startswith("+") and phone_number[1:].isdigit()