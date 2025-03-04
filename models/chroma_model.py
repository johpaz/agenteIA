import chromadb
from chromadb.config import Settings
import uuid
from typing import List, Dict, Any, Union, Optional
from datetime import datetime

class EnhancedChromaDB:
    def __init__(self, collection_name: str = "whatsapp_bot", persist_directory: str = "./chroma_db"):
        """
        Inicializa una conexión mejorada a ChromaDB con opciones de configuración avanzadas.
        
        Args:
            collection_name (str): Nombre de la colección.
            persist_directory (str): Directorio para persistir los datos de ChromaDB.
        """
        # Configuración avanzada para ChromaDB
        settings = Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False,  # Desactivar telemetría
            allow_reset=True,  # Permitir reset cuando sea necesario
            is_persistent=True  # Garantizar que los datos se persistan en disco
        )
        
        # Crear cliente persistente con configuración mejorada
        self.client = chromadb.PersistentClient(settings=settings)
        
        # Crear o cargar la colección con metadatos
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Colección de datos para asistente virtual"},
            embedding_function=None  # Usaremos embeddings proporcionados externamente
        )
        
    def add_document(self, text: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Añade un documento a la colección con un ID generado automáticamente.
        
        Args:
            text (str): Texto a almacenar.
            embedding (List[float]): Embedding del texto.
            metadata (Dict[str, Any], optional): Metadatos adicionales.
            
        Returns:
            str: ID del documento añadido.
        """
        # Generar un ID único para el documento
        doc_id = str(uuid.uuid4())
        
        # Preparar metadatos básicos si no se proporcionan
        if metadata is None:
            metadata = {}
        
        # Añadir timestamp a los metadatos
        metadata.update({
            "timestamp": datetime.now().isoformat(),
            "source": "user_input"
        })
        
        # Añadir documento a la colección
        self.collection.add(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata]
        )
        
        return doc_id
    
    def add_documents_batch(self, texts: List[str], embeddings: List[List[float]], 
                           metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Añade múltiples documentos en lote para mayor eficiencia.
        
        Args:
            texts (List[str]): Lista de textos a almacenar.
            embeddings (List[List[float]]): Lista de embeddings correspondientes.
            metadatas (List[Dict[str, Any]], optional): Lista de metadatos.
            
        Returns:
            List[str]: Lista de IDs de los documentos añadidos.
        """
        # Validar que las listas tengan la misma longitud
        if len(texts) != len(embeddings):
            raise ValueError("Las listas de textos y embeddings deben tener la misma longitud")
        
        # Generar IDs únicos para cada documento
        doc_ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        
        # Si no se proporcionan metadatos, crear lista de diccionarios vacíos
        if metadatas is None:
            metadatas = [{
                "timestamp": datetime.now().isoformat(),
                "source": "batch_upload"
            } for _ in range(len(texts))]
        
        # Añadir documentos en lote
        self.collection.add(
            ids=doc_ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        return doc_ids
    
    def query_semantic(self, query_embedding: List[float], n_results: int = 5, 
                      filter_criteria: Optional[Dict[str, Any]] = None, 
                      include_embeddings: bool = False) -> Dict[str, Any]:
        """
        Realiza una consulta semántica avanzada en ChromaDB.
        
        Args:
            query_embedding (List[float]): Embedding de la consulta.
            n_results (int): Número de resultados a devolver.
            filter_criteria (Dict[str, Any], optional): Filtro para la consulta basado en metadatos.
            include_embeddings (bool): Si se deben incluir los embeddings en los resultados.
            
        Returns:
            Dict[str, Any]: Resultados de la consulta.
        """
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_criteria,  # Filtrar por metadatos específicos
            include=["documents", "metadatas", "distances"] + (["embeddings"] if include_embeddings else [])
        )
    
    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Recupera un documento específico por su ID.
        
        Args:
            doc_id (str): ID del documento a recuperar.
            
        Returns:
            Dict[str, Any]: Documento recuperado con sus metadatos y embedding.
        """
        result = self.collection.get(
            ids=[doc_id],
            include=["documents", "metadatas", "embeddings"]
        )
        
        if not result["ids"]:
            raise ValueError(f"No se encontró documento con ID: {doc_id}")
            
        return {
            "id": result["ids"][0],
            "document": result["documents"][0],
            "metadata": result["metadatas"][0],
            "embedding": result["embeddings"][0]
        }
    
    def update_document(self, doc_id: str, text: Optional[str] = None, 
                       embedding: Optional[List[float]] = None, 
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Actualiza un documento existente en la colección.
        
        Args:
            doc_id (str): ID del documento a actualizar.
            text (str, optional): Nuevo texto si se desea actualizar.
            embedding (List[float], optional): Nuevo embedding si se desea actualizar.
            metadata (Dict[str, Any], optional): Nuevos metadatos a añadir o actualizar.
        """
        update_args = {"ids": [doc_id]}
        
        if text is not None:
            update_args["documents"] = [text]
            
        if embedding is not None:
            update_args["embeddings"] = [embedding]
            
        if metadata is not None:
            # Obtener metadatos actuales y actualizarlos
            current = self.get_document(doc_id)
            current_metadata = current["metadata"]
            current_metadata.update(metadata)
            current_metadata["updated_at"] = datetime.now().isoformat()
            update_args["metadatas"] = [current_metadata]
            
        self.collection.update(**update_args)
    
    def delete_document(self, doc_id: str) -> None:
        """
        Elimina un documento de la colección.
        
        Args:
            doc_id (str): ID del documento a eliminar.
        """
        self.collection.delete(ids=[doc_id])
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas sobre la colección actual.
        
        Returns:
            Dict[str, Any]: Estadísticas de la colección.
        """
        count = self.collection.count()
        return {
            "collection_name": self.collection.name,
            "document_count": count,
            "metadata": self.collection.metadata
        }
    
    def get_nearest_neighbors(self, doc_id: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Encuentra los vecinos más cercanos a un documento específico.
        
        Args:
            doc_id (str): ID del documento de referencia.
            n_results (int): Número de vecinos a encontrar.
            
        Returns:
            Dict[str, Any]: Vecinos más cercanos con sus distancias.
        """
        # Obtener el embedding del documento
        doc = self.get_document(doc_id)
        embedding = doc["embedding"]
        
        # Excluir el documento de referencia del resultado
        return self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results + 1,  # Añadir 1 para compensar el documento original
            where={"$id": {"$ne": doc_id}},  # Filtrar el documento original
            include=["documents", "metadatas", "distances", "ids"]
        )