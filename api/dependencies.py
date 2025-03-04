from fastapi import Depends
from redis.asyncio import Redis
from contextlib import asynccontextmanager
from api.whatsapp import WhatsAppService
from repositories.message_repository import MessageRepository
from config.config import settings



@asynccontextmanager
async def get_redis():
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )
    try:
        yield redis
    finally:
        await redis.close()

async def get_whatsapp_service(redis: Redis = Depends(get_redis)):
    return WhatsAppService(redis=redis)

# Elimina esta línea vieja:
# whatsapp_service = WhatsAppService()lo las dependencias no asíncronas
message_repository = MessageRepository()