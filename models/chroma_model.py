import chromadb

class ChromaDB:
    def __init__(self, collection_name: str = "whatsapp_bot"):
        """
        Inicializa la conexión a ChromaDB.
        Args:
            collection_name (str): Nombre de la colección.
        """
        # Crear un cliente de ChromaDB
        self.client = chromadb.PersistentClient(path="./chroma_db")  # Directorio para persistir los datos

        # Crear o cargar una colección
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_data(self, user_id: str, text: str, embedding: list):
        """
        Añade datos a la colección de ChromaDB.
        Args:
            user_id (str): ID del usuario.
            text (str): Texto a almacenar.
            embedding (list): Embedding del texto.
        """
        self.collection.add(
            ids=[user_id],  # ID único para cada entrada
            documents=[text],  # Texto asociado
            embeddings=[embedding]  # Embedding del texto
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