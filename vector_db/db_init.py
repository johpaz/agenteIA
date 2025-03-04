from .pinecone_utils import create_collection, add_embeddings_to_collection
from models.embedding_model import EmbeddingModel
from pdf_processing.pdf_loader import load_pdf
from models.model_utils import split_text_into_chunks

# Inicialización del modelo de embeddings
embedding_model = EmbeddingModel()

def initialize_vector_db():
    """
    Inicializa la base de datos vectorial con datos de ejemplo.
    """
    # Crear una colección predeterminada
    collection_name = "pdf_embeddings"
    create_collection(collection_name)

    # Cargar un PDF de ejemplo y generar embeddings
    example_pdf_text = load_pdf("example.pdf")
    chunks = split_text_into_chunks(example_pdf_text)
    embeddings = [embedding_model.generate_embeddings(chunk) for chunk in chunks]
    ids = [f"id_{i}" for i in range(len(chunks))]

    # Añadir embeddings a la colección
    add_embeddings_to_collection(collection_name, chunks, embeddings, ids)