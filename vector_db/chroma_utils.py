import chromadb
from sentence_transformers import SentenceTransformer
from typing import List


class ChromaClient:
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "whatsapp_bot"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def generate_embeddings(self, text: str) -> List[float]:
        """Genera embeddings para un texto."""
        return self.embedding_model.encode(text).tolist()

    def get_or_create_collection(self, collection_name: str):
        """Obtiene o crea una colección."""
        return self.client.get_or_create_collection(name=collection_name)

    def add_embeddings_to_collection(self, collection_name: str, sections: list, embeddings: list, ids: list):
        """
        Agrega los embeddings y los datos de las secciones a la colección de ChromaDB.

        Args:
            collection_name (str): Nombre de la colección en ChromaDB.
            sections (list): Lista de secciones (texto).
            embeddings (list): Lista de embeddings generados.
            ids (list): Lista de IDs únicos para cada sección.
        """
        # Obtener la colección o crearla
        collection = self.get_or_create_collection(collection_name)
        
        # Insertar los embeddings en la colección
        collection.add(
            documents=sections,  # Secciones de texto
            metadatas=[{"section": section} for section in sections],  # Metadata opcional, aquí es solo el nombre de la sección
            embeddings=embeddings,  # Embeddings generados
            ids=ids  # IDs únicos
        )
    def query_data(self, query_embedding: list, n_results: int = 1):
        """
        Realiza una consulta semántica en ChromaDB.
        Args:
            query_embedding (list): Embedding de la consulta.
            n_results (int): Número de resultados a devolver.
        Returns:
            dict: Resultados de la consulta.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results