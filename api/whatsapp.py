from typing import Dict, Any, Optional
import httpx
from fastapi import status
from pydantic import BaseModel
from config.config import settings
from models.language_model import EnhancedAIAssistant
from redis.asyncio import Redis
from utils.retry import async_retry

class WhatsAppMessageRequest(BaseModel):
    messaging_product: str = "whatsapp"
    to: str
    type: str = "text"
    text: dict
    
    
class WhatsAppService:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.response_generator = EnhancedAIAssistant()
        self.base_url = f"https://graph.facebook.com/v21.0/{settings.PHONE_NUMBER_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }

    @async_retry(retries=3, delay=1, backoff=2)
    async def send_message(self, to: str, message: str) -> Dict[str, Any]:
        """Envía mensajes con retry automático y caché de estado"""
        cache_key = f"msg_status:{to}:{hash(message)}"
        if await self.redis.get(cache_key):
            return {"status": "already_sent"}

        payload = WhatsAppMessageRequest(
            to=to,
            text={"body": message}
        ).dict()

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            await self.redis.setex(cache_key, 3600, "sent")
            return response.json()

    async def process_incoming_message(self, message_data: Dict[str, Any]) -> str:
        """Procesamiento con caché y rate limiting"""
        user_number = message_data.get("from")
        message_body = message_data.get("text", {}).get("body", "")
        print(message_body)
        # Rate Limiting (15 mensajes/minuto)
        rate_key = f"rate_limit:{user_number}"
        current_count = await self.redis.incr(rate_key)
        if current_count > 15:
            return "Demasiadas solicitudes. Por favor espere."
        if current_count == 1:
            await self.redis.expire(rate_key, 60)

        # Cache de respuestas
        cache_key = f"response_cache:{hash(message_body)}"
        print(cache_key)
        cached_response = await self.redis.get(cache_key)
        if cached_response:
            return cached_response

        # Generar y cachear nueva respuesta
        response = await self.response_generator.generate_response(message_body)
        await self.redis.setex(cache_key, 300, response)  # Cache por 5 minutos
        
        return response