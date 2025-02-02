from fastapi import HTTPException

class CustomHTTPException(HTTPException):
    """
    Excepción personalizada para manejar errores HTTP.
    """
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

def raise_bad_request(message: str):
    """
    Lanza una excepción HTTP 400 (Bad Request).
    Args:
        message (str): Mensaje de error.
    """
    raise CustomHTTPException(status_code=400, detail=message)

def raise_not_found(message: str):
    """
    Lanza una excepción HTTP 404 (Not Found).
    Args:
        message (str): Mensaje de error.
    """
    raise CustomHTTPException(status_code=404, detail=message)

def raise_internal_server_error(message: str):
    """
    Lanza una excepción HTTP 500 (Internal Server Error).
    Args:
        message (str): Mensaje de error.
    """
    raise CustomHTTPException(status_code=500, detail=message)