from fastapi import APIRouter, Request, Response, HTTPException
from typing import Dict, Any
from api.dependencies import WhatsAppService
from config.config import settings  # Configuración de entorno

# Inicialización del enrutador y servicios necesarios
router = APIRouter()
whatsapp_service = WhatsAppService()

# Endpoint para verificar el webhook con la API de WhatsApp
@router.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == settings.WHATSAPP_TOKEN:
            return Response(content=challenge)  # Responde con el desafío si la verificación es exitosa
        raise HTTPException(status_code=403, detail="Invalid verification token")
    
    raise HTTPException(status_code=400, detail="Invalid parameters")

# Endpoint para procesar mensajes entrantes
@router.post("/webhook")
async def process_webhook(request: Request):
    try:
        data = await request.json()
        if "entry" not in data or not data["entry"]:
            raise ValueError("No entries found in the webhook payload.")

        for entry in data["entry"]:
            for change in entry.get("changes", []):
                if "value" in change and "messages" in change["value"]:
                    for msg in change["value"]["messages"]:
                        from_number = msg.get("from")
                        if not from_number:
                            print("No se encontró el número del remitente en el mensaje.")
                            continue

                        if "text" not in msg or "body" not in msg["text"]:
                            print("El mensaje no contiene texto.")
                            continue

                        user_message = msg["text"]["body"]
                        try:
                            # Procesar el mensaje con el servicio de WhatsApp
                            response_text = await whatsapp_service.process_incoming_message(msg)

                            # Enviar respuesta a través de WhatsApp
                            await whatsapp_service.send_message(to=from_number, message=response_text)
                        except Exception as e:
                            print(f"Error al procesar el mensaje: {str(e)}")
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    return {"status": "success"}