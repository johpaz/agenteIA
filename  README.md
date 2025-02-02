# WhatsApp Chatbot Backend

Este proyecto implementa un backend para un chatbot de WhatsApp que utiliza modelos de lenguaje (Llama3) y una base de datos vectorial (ChromaDB) para proporcionar respuestas basadas en PDFs cargados por el usuario.

## Características Principales

- **Conexión con WhatsApp**: Interactúa con la API de WhatsApp Business para recibir y enviar mensajes.
- **Procesamiento de PDFs**: Extrae texto de archivos PDF, genera embeddings y los almacena en ChromaDB.
- **Modelo de Lenguaje**: Utiliza Llama3 para generar respuestas en lenguaje natural basadas en el contexto del PDF.
- **Fine-Tuning**: Permite ajustar el modelo con nuevos datos para mejorar su precisión.
- **Despliegue con Docker**: Contenerización del proyecto para facilitar el despliegue en producción.

## Estructura del Proyecto
/proyecto-agente-whatsapp
│
├── /api # Manejo de la API de WhatsApp
├── /backend # Backend principal (FastAPI)
├── /data # Datos y archivos PDF
├── /models # Modelos de lenguaje y embeddings
├── /pdf_processing # Procesamiento de PDFs
├── /vector_db # Base de datos vectorial (ChromaDB)
├── /repositories # Repositorios para MongoDB
├── /services # Servicios principales (QA, WhatsApp, etc.)
├── /tests # Pruebas unitarias e integración
├── /docker # Configuración de Docker
├── /config # Configuración global
├── requirements.txt # Dependencias del proyecto
├── README.md # Documentación del proyecto
└── .gitignore # Archivos ignorados por Git


## Requisitos Previos

- Python 3.9+
- MongoDB
- Docker (opcional, para despliegue)

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/johpaz/proyecto-agente-whatsapp.git
   cd proyecto-agente-whatsapp

   pip install -r requirements.txt

   MONGODB_URL=mongodb://localhost:27017

2.  Instala las dependencias:
    pip install -r requirements.txt

3.  Configura las variables de entorno:
Crea un archivo .env en la carpeta config y completa las variables necesarias:


DATABASE_NAME=whatsapp_bot
VERIFY_TOKEN=tu_verify_token
WHATSAPP_TOKEN=tu_whatsapp_access_token
PHONE_NUMBER_ID=tu_phone_number_id
HF_API_KEY=tu_huggingface_api_key

4. Inicia la aplicación:

uvicorn backend.main:app --reload

Despliegue con Docker

1. Construye la imagen de Docker:

docker-compose up --build

2. Accede a la aplicación en http://localhost:8000.


Pruebas
Ejecuta las pruebas unitarias e integración:
pytest tests/


Contribuciones
Las contribuciones son bienvenidas. Si encuentras algún problema o tienes sugerencias, abre un issue o envía un pull request.

Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

---

