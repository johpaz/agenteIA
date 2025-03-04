from fastapi import APIRouter, HTTPException, UploadFile, File
import os
import pdfplumber
import uuid
import numpy as np
from typing import List
from pydantic import BaseModel
import asyncio
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

router = APIRouter()

# Configuración Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "pdf-documents"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 32
EMBEDDING_DIM = 384  # Dimensión del modelo all-MiniLM-L6-v2

# Inicializar cliente Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Crear índice si no existe
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIM,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

# Obtener referencia al índice
index = pc.Index(INDEX_NAME)

# Modelo de embeddings
embedder = SentenceTransformer(EMBEDDING_MODEL)

# Configuración de directorios
UPLOAD_FOLDER = "data/pdfs/user_uploaded/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class PDFContent(BaseModel):
    text: str
    metadata: dict

@router.post("/upload-pdf", tags=["PDF Management"])
async def upload_pdf(file: UploadFile = File(...)):
    """Endpoint para cargar PDFs con validación mejorada"""
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(400, "Solo se aceptan archivos PDF")

        file_id = uuid.uuid4().hex
        safe_filename = f"{file_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        
        contents = await file.read()
        if len(contents) > 50 * 1024 * 1024:
            raise HTTPException(413, "Tamaño máximo excedido (50MB)")
        
        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        return {
            "message": "PDF almacenado exitosamente",
            "file_id": file_id,
            "filename": safe_filename
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error en la carga: {str(e)}")

@router.post("/process-pdfs", tags=["Processing"])
async def process_pdfs():
    """Pipeline de procesamiento optimizado para Pinecone"""
    try:
        pdf_files = [
            f for f in os.listdir(UPLOAD_FOLDER) 
            if f.endswith(".pdf") and os.path.isfile(os.path.join(UPLOAD_FOLDER, f))
        ]
        
        if not pdf_files:
            raise HTTPException(400, "No hay PDFs para procesar")

        tasks = [process_single_pdf(filename) for filename in pdf_files]
        results = await asyncio.gather(*tasks)

        total_pages = sum(results)
        if total_pages == 0:
            raise HTTPException(400, "No se encontró texto válido")

        return {
            "message": "Procesamiento completado",
            "total_pages": total_pages,
            "indexed_documents": total_pages
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error en el procesamiento: {str(e)}")

async def process_single_pdf(filename: str) -> int:
    """Procesamiento individual de PDF con manejo de errores"""
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    processed_pages = 0
    
    try:
        with pdfplumber.open(file_path) as pdf:
            texts = []
            metadatas = []
            
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and len(text) > 50:
                    texts.append(text)
                    metadatas.append({
                        "source": filename,
                        "page": page_num + 1,
                        "file_id": filename.split("_")[0]
                    })
                    processed_pages += 1

            if texts:
                # Generar embeddings por lotes
                embeddings = embedder.encode(
                    texts,
                    batch_size=BATCH_SIZE,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
                
                # Preparar vectores para Pinecone
                vectors = []
                for idx, (text, metadata) in enumerate(zip(texts, metadatas)):
                    vector_id = f"{metadata['file_id']}_p{metadata['page']}"
                    vectors.append({
                        "id": vector_id,
                        "values": embeddings[idx].tolist(),
                        "metadata": metadata
                    })
                
                # Upsert en batches
                for i in range(0, len(vectors), BATCH_SIZE):
                    batch = vectors[i:i+BATCH_SIZE]
                    index.upsert(vectors=batch)
                
        os.remove(file_path)
        return processed_pages

    except Exception as e:
        print(f"Error procesando {filename}: {str(e)}")
        return 0