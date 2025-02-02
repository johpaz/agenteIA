import chromadb
from sentence_transformers import SentenceTransformer

# Cliente persistente de ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

# Cargar un modelo preentrenado para generar embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embeddings(text: str) -> list:
    """
    Genera un embedding para un texto dado.
    Args:
        text (str): Texto a convertir en embedding.
    Returns:
        list: Embedding del texto.
    """
    return embedding_model.encode(text).tolist()

def create_collection(collection_name: str):
    """
    Crea una nueva colección en ChromaDB.
    Args:
        collection_name (str): Nombre de la colección.
    Returns:
        Collection: Colección creada.
    """
    return client.create_collection(name=collection_name)

def get_or_create_collection(collection_name: str):
    """
    Obtiene una colección existente o crea una nueva si no existe.
    Args:
        collection_name (str): Nombre de la colección.
    Returns:
        Collection: Colección obtenida o creada.
    """
    return client.get_or_create_collection(name=collection_name)

def add_embeddings_to_collection(collection_name: str, documents: list, embeddings: list, ids: list):
    """
    Añade embeddings a una colección en ChromaDB.
    Args:
        collection_name (str): Nombre de la colección.
        documents (list): Lista de documentos (textos).
        embeddings (list): Lista de embeddings correspondientes.
        ids (list): Lista de IDs únicos para cada documento.
    """
    collection = get_or_create_collection(collection_name)
    collection.add(
        documents=documents,
        embeddings=embeddings,
        ids=ids
    )

def query_collection(collection_name: str, query_embedding: list, n_results: int = 1) -> dict:
    """
    Realiza una consulta semántica en una colección de ChromaDB.
    Args:
        collection_name (str): Nombre de la colección.
        query_embedding (list): Embedding de la consulta.
        n_results (int): Número de resultados a devolver.
    Returns:
        dict: Resultados de la consulta.
    """
    collection = get_or_create_collection(collection_name)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results