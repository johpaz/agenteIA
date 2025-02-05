from fastapi import APIRouter, Request, Response, HTTPException, File, UploadFile
from pdf_processing.preprocess_pdf import preprocess_pdf, save_processed_data
from models.embedding_model import EmbeddingModel
from vector_db.chroma_utils import ChromaClient
import os
import json

router = APIRouter()

# Instanciar el cliente de ChromaDB
chroma_client = ChromaClient()

def save_processed_data(processed_data, json_path):
    """Guarda los datos procesados en un archivo JSON, eliminando el archivo existente si es necesario."""
    # Si el archivo ya existe, eliminarlo antes de crear uno nuevo
    if os.path.exists(json_path):
        os.remove(json_path)
    
    # Guardar el archivo JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)

# Ruta para cargar un PDF y transformarlo en JSON
@router.post("/upload-pdf", tags=["PDF Upload"])
async def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint para cargar un archivo PDF, preprocesarlo y guardarlo como JSON.
    Args:
        file (UploadFile): Archivo PDF enviado por el usuario.
    Returns:
        dict: Respuesta indicando éxito o error.
    """
    try:
        # Validar que el archivo sea un PDF
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="El archivo debe ser un PDF.")

        # Guardar el archivo temporalmente
        temp_file_path = f"data/pdfs/user_uploaded/{file.filename}"
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Preprocesar el PDF y obtener las secciones
        processed_data = preprocess_pdf(temp_file_path)

        # Guardar el JSON de las secciones procesadas
        json_path = f"data/processed_pdfs/{file.filename.replace('.pdf', '.json')}"
        save_processed_data(processed_data, json_path)

        return {"message": f"PDF cargado, procesado y almacenado como JSON exitosamente. Archivo JSON: {json_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el PDF: {str(e)}")


# Endpoint para lanzar el entrenamiento usando los datos del JSON
@router.post("/train", tags=["Training"])
async def train_model():
    """
    Endpoint para entrenar el modelo con los PDFs cargados previamente.
    Returns:
        dict: Respuesta indicando éxito o error.
    """
    try:
        # Leer el archivo JSON procesado
        json_path = "data/processed_pdfs/tuprofe.json"
        if not os.path.exists(json_path):
            raise HTTPException(status_code=400, detail="No se encontró el archivo JSON procesado. Carga un PDF primero.")

        with open(json_path, "r", encoding="utf-8") as f:
            processed_data = json.load(f)

        # Extraer secciones del JSON
        sections = processed_data.get("sections", [])
        if not sections:
            raise HTTPException(status_code=400, detail="El archivo JSON procesado no contiene secciones válidas.")

        # Generar embeddings
        embedding_model = EmbeddingModel()
        embeddings = [embedding_model.generate_embeddings(section) for section in sections]

        # Verificar que las embeddings sean una lista de números flotantes
        for idx, embedding in enumerate(embeddings):
            if not all(isinstance(x, (int, float)) for x in embedding):
                raise HTTPException(status_code=400, detail=f"Las embeddings en la sección {idx} no son válidas. Deben ser números flotantes o enteros.")

        # Crear IDs únicos para cada sección
        ids = [f"section_{i}" for i in range(len(sections))]

        # Almacenar en ChromaDB
        collection_name = "pdf_embeddings"
        chroma_client.add_embeddings_to_collection(collection_name, sections, embeddings, ids)

        return {"message": "Entrenamiento completado exitosamente. Datos almacenados en ChromaDB."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el entrenamiento: {str(e)}")
