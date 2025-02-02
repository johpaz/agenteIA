import pytest
from models.embedding_model import EmbeddingModel
from models.language_model import LanguageModel
from models.fine_tuning import FineTuner

# Pruebas para el modelo de embeddings
def test_embedding_model():
    embedding_model = EmbeddingModel()
    text = "Este es un texto de prueba."
    embedding = embedding_model.generate_embeddings(text)

    # Verificar que el embedding sea una lista de números
    assert isinstance(embedding, list)
    assert all(isinstance(value, float) for value in embedding)

# Pruebas para el modelo de lenguaje
def test_language_model():
    language_model = LanguageModel()
    context = "El contexto es sobre inteligencia artificial."
    user_message = "¿Qué es la IA?"
    response = language_model.generate_response(context, user_message)

    # Verificar que la respuesta no esté vacía
    assert isinstance(response, str)
    assert len(response) > 0

# Pruebas para el fine-tuning (opcional)
@pytest.mark.skip(reason="Esta prueba puede ser costosa y lenta.")
def test_fine_tuning():
    fine_tuner = FineTuner()
    training_data = [
        {"context": "El contexto es sobre IA.", "question": "¿Qué es la IA?", "answer": "La IA es..."}
    ]
    fine_tuner.fine_tune(training_data, output_dir="./test_fine_tuned")

    # Verificar que el modelo ajustado se haya guardado
    import os
    assert os.path.exists("./test_fine_tuned")