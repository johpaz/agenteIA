from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Información general del proyecto
    PROJECT_NAME: str = "WhatsApp Chatbot"
    PROJECT_VERSION: str = "1.0.0"

    # Configuración de MongoDB
    MONGODB_URL: str  # URL de conexión a MongoDB (ejemplo: mongodb://localhost:27017)
    DATABASE_NAME: str  # Nombre de la base de datos (ejemplo: whatsapp_bot)

    # Configuración de la API de WhatsApp
    VERIFY_TOKEN: str  # Token de verificación para el webhook
    WHATSAPP_TOKEN: str  # Token de acceso para la API de WhatsApp
    PHONE_NUMBER_ID: str  # ID del número de teléfono registrado en WhatsApp Business

    # Plantilla de mensajes (opcional)
    TEMPLATE: Optional[str] = None  # Plantilla de mensaje predeterminada (si aplica)

    # Clave de API de Hugging Face
    HF_API_KEY: str  # Clave de API para acceder a modelos de Hugging Face

    class Config:
        env_file = ".env"  # Cargar variables de entorno desde el archivo .env
        env_file_encoding = "utf-8"  # Codificación del archivo .env
        case_sensitive = True  # Las variables son sensibles a mayúsculas/minúsculas

# Instancia de la configuración
settings = Settings()

# Validación adicional para asegurar que las variables críticas estén configuradas
def validate_settings():
    critical_vars = [
        "MONGODB_URL",
        "DATABASE_NAME",
        "VERIFY_TOKEN",
        "WHATSAPP_TOKEN",
        "PHONE_NUMBER_ID",
        "HF_API_KEY",
    ]
    missing_vars = [var for var in critical_vars if not getattr(settings, var)]
    if missing_vars:
        raise ValueError(f"Faltan las siguientes variables de entorno: {', '.join(missing_vars)}")

validate_settings()