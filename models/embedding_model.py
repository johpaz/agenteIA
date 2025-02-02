from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Inicializa el modelo de embeddings.
        Args:
            model_name (str): Nombre del modelo de embeddings a cargar.
        """
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, text: str) -> list:
        """
        Genera embeddings a partir de un texto.
        Args:
            text (str): Texto del cual generar embeddings.
        Returns:
            list: Embeddings generados.
        """
        return self.model.encode(text).tolist()