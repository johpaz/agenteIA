from typing import List, Dict, Optional, TypedDict, Any, AsyncGenerator
import pinecone
import numpy as np
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, ValidationError
import asyncio
from loguru import logger
from datetime import datetime

# Configuración de modelos
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # Dimensión del modelo seleccionado
INDEX_NAME = "chatbot"  # Nombre del índice en Pinecone
BATCH_SIZE = 128  # Tamaño óptimo para embeddings

class Document(BaseModel):
    content: str
    metadata: Dict[str, Any]
    namespace: str = "default"

class Query(BaseModel):
    text: str
    namespace: str = "default"
    top_k: int = 5
    score_threshold: float = 0.75

class VectorState(TypedDict):
    operation: str
    documents: List[Document]
    query: Optional[Query]
    embeddings: Optional[np.ndarray]
    results: Optional[List[Document]]
    error: Optional[str]
    timestamp: str

class PineconeManager:
    def __init__(self):
        self._initialize_components()
        self._setup_graph()
    
    def _initialize_components(self):
        """Inicialización optimizada con validación Pydantic"""
        try:
            # Configurar Pinecone
            pinecone.init(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENV
            )
            
            # Crear índice si no existe
            if INDEX_NAME not in pinecone.list_indexes():
                pinecone.create_index(
                    name=INDEX_NAME,
                    dimension=EMBEDDING_DIM,
                    metric="cosine",
                    spec=pinecone.ServerlessSpec(
                        cloud="aws",
                        region="us-west-2"
                    )
                )
            
            self.index = pinecone.Index(INDEX_NAME)
            
            # Modelo de embeddings con caché
            self.embedder = SentenceTransformer(
                EMBEDDING_MODEL,
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
            self.embedder.max_seq_length = 512  # Longitud óptima
            
        except Exception as e:
            logger.error(f"Error de inicialización: {e}")
            raise

    def _setup_graph(self):
        """Grafo de operaciones con flujo optimizado"""
        workflow = StateGraph(VectorState)
        
        # Nodos principales
        workflow.add_node("validate_input", self.validate_input)
        workflow.add_node("generate_embeddings", self.generate_embeddings)
        workflow.add_node("upsert_vectors", self.upsert_vectors)
        workflow.add_node("query_vectors", self.query_vectors)
        
        # Rutas condicionales
        workflow.add_conditional_edges(
            "validate_input",
            self.route_operation,
            {"store": "generate_embeddings", "query": "query_vectors"}
        )
        
        # Flujo para almacenamiento
        workflow.add_edge("generate_embeddings", "upsert_vectors")
        workflow.add_edge("upsert_vectors", END)
        
        # Flujo para consulta
        workflow.add_edge("query_vectors", END)
        
        # Manejo de errores
        workflow.add_node("handle_error", self.handle_error)
        workflow.add_edge("handle_error", END)
        
        workflow.set_entry_point("validate_input")
        self.workflow = workflow.compile()
    
    async def validate_input(self, state: VectorState) -> VectorState:
        """Validación avanzada con Pydantic"""
        try:
            if state["operation"] == "store":
                Document.validate_batch(state["documents"])
            elif state["operation"] == "query":
                Query(**state["query"])
            return {**state, "error": None}
        except ValidationError as e:
            logger.error(f"Validación fallida: {e}")
            return {**state, "error": str(e)}
    
    async def generate_embeddings(self, state: VectorState) -> VectorState:
        """Generación de embeddings con batch processing"""
        try:
            texts = [doc.content for doc in state["documents"]]
            
            # Generar embeddings en batches
            embeddings = []
            for i in range(0, len(texts), BATCH_SIZE):
                batch = texts[i:i+BATCH_SIZE]
                embeddings.extend(self.embedder.encode(
                    batch,
                    show_progress_bar=True,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                ))
            
            return {**state, "embeddings": np.array(embeddings)}
        except Exception as e:
            logger.error(f"Error generando embeddings: {e}")
            return {**state, "error": str(e)}
    
    async def upsert_vectors(self, state: VectorState) -> VectorState:
        """Upsert optimizado con manejo de namespaces"""
        try:
            vectors = []
            for doc, embedding in zip(state["documents"], state["embeddings"]):
                vectors.append({
                    "id": str(doc.metadata.get("id", uuid.uuid4())),
                    "values": embedding.tolist(),
                    "metadata": doc.metadata,
                    "namespace": doc.namespace
                })
            
            # Upsert en batches para mejor performance
            for i in range(0, len(vectors), BATCH_SIZE):
                batch = vectors[i:i+BATCH_SIZE]
                self.index.upsert(
                    vectors=batch,
                    namespace=batch[0]["namespace"]
                )
            
            return {**state, "results": None, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            logger.error(f"Error upsert: {e}")
            return {**state, "error": str(e)}
    
    async def query_vectors(self, state: VectorState) -> VectorState:
        """Búsqueda semántica avanzada con filtros"""
        try:
            query = state["query"]
            embedding = self.embedder.encode(
                query.text,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True
            ).tolist()
            
            results = self.index.query(
                vector=embedding,
                top_k=query.top_k,
                include_metadata=True,
                namespace=query.namespace,
                filter={"score": {"$gte": query.score_threshold}}
            )
            
            # Mapear resultados a documentos
            documents = [
                Document(
                    content=match["metadata"].get("content", ""),
                    metadata=match["metadata"],
                    namespace=query.namespace
                )
                for match in results["matches"]
            ]
            
            return {**state, "results": documents, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            logger.error(f"Error en query: {e}")
            return {**state, "error": str(e)}
    
    async def astore(self, documents: List[Document]) -> AsyncGenerator[Dict, None]:
        """Almacenamiento asíncrono con streaming"""
        state = {
            "operation": "store",
            "documents": documents,
            "query": None,
            "timestamp": datetime.now().isoformat()
        }
        
        async for update in self.workflow.astream(state):
            yield {
                "status": "success" if not update.get("error") else "error",
                "data": update.get("results"),
                "error": update.get("error"),
                "timestamp": update.get("timestamp")
            }
    
    async def asearch(self, query: Query) -> AsyncGenerator[Dict, None]:
        """Búsqueda asíncrona con streaming"""
        state = {
            "operation": "query",
            "documents": [],
            "query": query,
            "timestamp": datetime.now().isoformat()
        }
        
        async for update in self.workflow.astream(state):
            yield {
                "status": "success" if not update.get("error") else "error",
                "results": update.get("results"),
                "error": update.get("error"),
                "timestamp": update.get("timestamp")
            }

# Uso recomendado
async def main():
    manager = PineconeManager()
    
    # Ejemplo de almacenamiento
    documents = [
        Document(
            content="Deep Learning fundamentals...",
            metadata={"course": "AI-101", "author": "Dr. Smith"},
            namespace="ai-courses"
        )
    ]
    
    async for status in manager.astore(documents):
        if status["status"] == "success":
            logger.info("Documentos almacenados exitosamente")
        else:
            logger.error(f"Error: {status['error']}")
    
    # Ejemplo de búsqueda
    query = Query(
        text="Aprendizaje profundo para principiantes",
        namespace="ai-courses",
        top_k=3
    )
    
    async for result in manager.asearch(query):
        if result["status"] == "success":
            for doc in result["results"]:
                logger.info(f"Resultado: {doc.content[:50]}...")
        else:
            logger.error(f"Error en búsqueda: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())