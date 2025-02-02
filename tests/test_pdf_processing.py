import pytest
from pdf_processing.pdf_loader import load_pdf
from pdf_processing.text_chunker import split_text_into_chunks
from pdf_processing.preprocess_pdf import preprocess_pdf

def test_load_pdf(tmp_path):
    # Crear un archivo PDF temporal
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("Test PDF content")

    text = load_pdf(pdf_file)
    assert "Test PDF content" in text

def test_split_text_into_chunks():
    text = "Este es un texto de prueba para dividir en fragmentos."
    chunks = split_text_into_chunks(text, chunk_size=10, overlap=2)
    assert len(chunks) > 0
    assert "texto" in chunks[0]
    



def test_preprocess_pdf(tmp_path):
    # Crear un archivo PDF temporal
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("Esta es una prueba.\nOtra línea de texto.")

    # Procesar el PDF
    processed_data = preprocess_pdf(pdf_file)

    # Verificar que el resultado tenga el formato esperado
    assert "sections" in processed_data
    assert len(processed_data["sections"]) > 0
    assert "Esta es una prueba." in processed_data["sections"][0]