import pytest
from vector_db.chroma_utils import create_collection, add_embeddings_to_collection, query_collection

def test_chroma_db_operations():
    collection_name = "test_collection"
    create_collection(collection_name)

    # Añadir embeddings
    documents = ["Documento de prueba"]
    embeddings = [[0.1, 0.2, 0.3]]
    ids = ["id_1"]
    add_embeddings_to_collection(collection_name, documents, embeddings, ids)

    # Consultar embeddings
    results = query_collection(collection_name, [0.1, 0.2, 0.3])
    assert "Documento de prueba" in results["documents"][0]