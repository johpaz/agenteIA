from fastapi import APIRouter, Request, Response, HTTPException, Depends, status
from typing import Dict, Any
import logging
from pydantic import BaseModel
from api.dependencies import get_whatsapp_service, WhatsAppService
from config.config import settings

# Configurar logging
logger = logging.getLogger(__name__)
router = APIRouter()

# Modelo Pydantic para validación de eventos
class WhatsAppEvent(BaseModel):
    object: str
    entry: list[dict]

@router.get("/webhook")
async def verify_webhook(
    request: Request,
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service)
):
    """Verificación del webhook para Meta"""
    try:
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")

        if not all([mode, token, challenge]):
            raise HTTPException(status_code=400, detail="Parámetros faltantes")

        if mode == "subscribe" and token == settings.WHATSAPP_TOKEN:
            logger.info("Webhook verificado exitosamente")
            return Response(content=challenge)
        
        logger.warning("Token de verificación inválido")
        raise HTTPException(status_code=403, detail="Token inválido")

    except Exception as e:
        logger.error(f"Error en verificación: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno")

@router.post("/webhook")
async def process_webhook(
    request: Request,
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service)
):
    """Procesamiento de mensajes entrantes de Meta"""
    try:
        data = await request.json()
        event = WhatsAppEvent(**data)
        if "entry" not in data or not data["entry"]:
            raise ValueError("No entries found in the webhook payload.")

        
        for entry in event.entry:
            for change in entry.get("changes", []):
                if self._valid_change(change):
                    await self._process_change(change, whatsapp_service)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

def _valid_change(change: dict) -> bool:
    """Valida la estructura del cambio según especificación de Meta"""
    required = {
        "value": {
            "messaging_product": "whatsapp",
            "metadata": ["display_phone_number", "phone_number_id"],
            "messages": list
        },
        "field": str
    }
    
    if not all(key in change for key in ["value", "field"]):
        return False
    
    value = change["value"]
    return all(
        value.get("messaging_product") == "whatsapp",
        isinstance(value.get("messages"), list),
        all(key in value.get("metadata", {}) for key in required["value"]["metadata"])
    )

async def _process_change(change: dict, service: WhatsAppService):
    """Procesa un cambio individual"""
    try:
        messages = change["value"].get("messages", [])
        for msg in messages:
            await self._handle_message(msg, service)
    except Exception as e:
        logger.error(f"Error procesando cambio: {str(e)}")
        await service.log_error(change)

async def _handle_message(msg: dict, service: WhatsAppService):
    """Maneja un mensaje individual"""
    try:
        from_number = msg.get("from")
        message_body = msg.get("text", {}).get("body", "")
        
        if not from_number or not message_body:
            logger.warning("Mensaje incompleto: %s", msg)
            return

        # Procesar y responder
        response = await service.process_incoming_message(msg)
        await service.send_message(to=from_number, message=response)
        
    except Exception as e:
        logger.error(f"Error manejando mensaje: {str(e)}")
        await service.send_message(
            to=from_number,
            message="⚠️ Error procesando tu mensaje. Intenta nuevamente."
        )