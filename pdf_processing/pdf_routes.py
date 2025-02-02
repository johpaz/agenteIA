from fastapi import APIRouter, Request, Response, HTTPException, File, UploadFile
from pdf_processing.preprocess_pdf import preprocess_pdf, save_processed_data,  preprocess_pdf
from models.embedding_model import EmbeddingModel
from vector_db.chroma_utils import add_embeddings_to_collection
import os
import json


router = APIRouter()

# Ruta para cargar un PDF
@router.post("/upload-pdf", tags=["PDF Upload"])
async def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint para cargar un archivo PDF.
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

        # Preprocesar el PDF
        processed_data = preprocess_pdf(temp_file_path)
        save_processed_data(processed_data, "data/processed_pdfs")

        # Generar embeddings y almacenarlos en ChromaDB
        embedding_model = EmbeddingModel()
        sections = processed_data["sections"]
        embeddings = [embedding_model.generate_embeddings(section) for section in sections]
        ids = [f"{file.filename}_section_{i}" for i in range(len(sections))]
        add_embeddings_to_collection("pdf_embeddings", sections, embeddings, ids)

        return {"message": "PDF cargado, procesado y almacenado exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el PDF: {str(e)}")
    



router = APIRouter()

# Endpoint para lanzar el entrenamiento inicial
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
        

        # Crear IDs únicos para cada sección
        ids = [f"section_{i}" for i in range(len(sections))]

        # Almacenar en ChromaDB
        collection_name = "pdf_embeddings"
        add_embeddings_to_collection(collection_name, sections, embeddings, ids)

        return {"message": "Entrenamiento completado exitosamente. Datos almacenados en ChromaDB."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el entrenamiento: {str(e)}")