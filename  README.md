# Chatbot Asistente IA con WhatsApp

Este proyecto implementa un backend inteligente que integra WhatsApp con modelos de lenguaje avanzados y una base de datos vectorial para proporcionar respuestas contextualizadas basadas en documentos PDF.

## Características Principales

- **Procesamiento Inteligente de PDFs**: Sistema avanzado de extracción y procesamiento de texto de PDFs
- **Base de Datos Vectorial**: Utiliza ChromaDB para almacenamiento eficiente de embeddings
- **Modelo de Lenguaje**: Implementa modelos de lenguaje para generar respuestas naturales y contextualizadas
- **API de WhatsApp**: Integración completa con la API de WhatsApp Business
- **Sistema de Usuarios**: Gestión de usuarios y sus documentos
- **Arquitectura Modular**: Diseño escalable y mantenible

## Estructura del Proyecto

```plaintext
├── api/                  # Integración con WhatsApp
├── backend/             # Servidor FastAPI
├── config/              # Configuración y variables de entorno
├── models/              # Modelos de IA y gestión de usuarios
├── pdf_processing/      # Procesamiento de documentos
├── repositories/        # Capa de acceso a datos
├── services/           # Lógica de negocio
└── vector_db/          # Gestión de base de datos vectorial

Requisitos del Sistema
Python 3.11
MongoDB
Docker (opcional)
Cuenta de WhatsApp Business
Acceso a modelos de lenguaje

Instalación

Clonar el repositorio:
git clone https://github.com/johpaz/agenteIA.git
cd agenteIA


Crear y activar entorno virtual:
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

Instalar dependencias:
pip install -r requirements.txt

Configurar variables de entorno: Crear archivo .env en la carpeta config/ con:
MONGODB_URL=mongodb://localhost:27017 DATABASE_NAME=whatsapp_bot WHATSAPP_TOKEN=tu_token PHONE_NUMBER_ID=tu_id MODEL_PATH=ruta_modelo CHROMA_PERSIST_DIR=ruta_chromadb
Iniciar la aplicación:
uvicorn backend.main:app --reload

Despliegue con Docker
Construir y ejecutar contenedores:

docker-compose up --build
Acceder a la API en http://localhost:8000
Uso del Sistema
Configurar Webhook de WhatsApp:

Configurar URL de webhook en el panel de WhatsApp Business
Verificar conexión con el endpoint de verificación
Gestión de PDFs:

Subir PDFs a través de la API
El sistema procesará y vectorizará automáticamente el contenido
Interacción con WhatsApp:

Los usuarios pueden hacer preguntas sobre el contenido de los PDFs
El sistema proporcionará respuestas contextualizadas
Documentación API
La documentación detallada de la API está disponible en:

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
Contribuciones
Las contribuciones son bienvenidas. Por favor:

Haz fork del repositorio
Crea una rama para tu feature
Envía un pull request
Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo LICENSE para más detalles.
