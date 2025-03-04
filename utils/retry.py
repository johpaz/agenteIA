import asyncio
from functools import wraps
from typing import Callable, Any

def async_retry(retries: int = 3, delay: float = 1, backoff: float = 2) -> Callable:
    """
    Decorador para reintentos asíncronos con backoff exponencial
    
    Args:
        retries: Número máximo de reintentos
        delay: Retardo inicial en segundos
        backoff: Factor de multiplicación del retardo
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            _delay = delay
            for attempt in range(1, retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == retries:
                        raise
                    await asyncio.sleep(_delay)
                    _delay *= backoff
            return await func(*args, **kwargs)  # Último intento
        return wrapper
    return decorator