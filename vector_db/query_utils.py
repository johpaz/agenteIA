from .chroma_utils import query_collection
from models.embedding_model import EmbeddingModel

# Inicialización del modelo de embeddings
embedding_model = EmbeddingModel()

def find_relevant_context(user_message: str, collection_name: str = "pdf_embeddings") -> str:
    """
    Busca el contexto más relevante en la base de datos vectorial.
    Args:
        user_message (str): Mensaje del usuario.
        collection_name (str): Nombre de la colección.
    Returns:
        str: Contexto relevante encontrado.
    """
    # Generar embedding del mensaje del usuario
    query_embedding = embedding_model.generate_embeddings(user_message)

    # Realizar la consulta en ChromaDB
    results = query_collection(collection_name, query_embedding)

    # Extraer el contexto más relevante
    if results["documents"]:
        return results["documents"][0][0]  # Devuelve el primer documento relevante
    return "No se encontró información relevante."