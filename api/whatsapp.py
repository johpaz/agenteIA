from typing import Dict, Any
import httpx
from config.config import settings
from models.language_model import LanguageModel  # Nuevo servicio de generación de respuestas

# Inicialización del servicio de generación de respuestas
response_generator = LanguageModel()

class WhatsAppService:
    def __init__(self):
        """
        Inicializa el servicio de WhatsApp con el token de verificación y la URL de la API.
        """
        self.token = settings.VERIFY_TOKEN
        self.api_url = f"https://graph.facebook.com/v21.0/{settings.PHONE_NUMBER_ID}/messages"

    async def send_message(self, to: str, message: str) -> Dict[str, Any]:
        """
        Envía un mensaje a través de la API de WhatsApp.
        Args:
            to (str): Número de teléfono del destinatario.
            message (str): Mensaje a enviar.
        Returns:
            Dict[str, Any]: Respuesta de la API de WhatsApp.
        Raises:
            httpx.HTTPStatusError: Si la solicitud a la API de WhatsApp falla.
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"Error al enviar el mensaje: {e}")
                raise

    async def process_incoming_message(self, message_data: Dict[str, Any]) -> str:
        """
        Procesa el mensaje entrante y genera una respuesta.
        Args:
            message_data (Dict[str, Any]): Datos del mensaje entrante.
        Returns:
            str: Respuesta generada.
        Raises:
            ValueError: Si el mensaje no tiene la estructura esperada.
        """
        if "text" not in message_data or "body" not in message_data["text"]:
            print("Mensaje entrante no tiene la estructura esperada.")
            return "Mensaje no válido."

        user_message = message_data["text"]["body"]
        try:
            # Generar respuesta usando el servicio de generación de respuestas
            response_text = await response_generator.generate_response(user_message)
            print(f"Respuesta generada: {response_text}")
            return response_text
        except Exception as e:
            print(f"Error al procesar el mensaje: {e}")
            return "Hubo un error al procesar tu mensaje. Por favor, inténtalo de nuevo."