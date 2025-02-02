import pytest
from fastapi.testclient import TestClient
from backend.main import app  # Importa la instancia de FastAPI

client = TestClient(app)

# Prueba para verificar el webhook de WhatsApp
def test_webhook_verification():
    response = client.get("/api/webhook", params={
        "hub.mode": "subscribe",
        "hub.verify_token": "tu_verify_token",
        "hub.challenge": "test_challenge"
    })
    assert response.status_code == 200
    assert response.text == "test_challenge"

# Prueba para cargar un PDF
def test_upload_pdf(tmp_path):
    # Crear un archivo PDF temporal
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("Test PDF content")

    with open(pdf_file, "rb") as file:
        response = client.post(
            "/api/upload-pdf",
            files={"file": ("test.pdf", file, "application/pdf")}
        )
    assert response.status_code == 200
    assert response.json()["message"] == "PDF cargado y procesado exitosamente."