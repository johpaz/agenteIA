from api.webhook import router as webhook_router
from fastapi import APIRouter, File, UploadFile, HTTPException
from pdf_processing.pdf_routes import router as  pdf_router
from models.user_routes import router as user_router




# Crear un router principal
router = APIRouter()

# Incluir los routers de los diferentes módulos
router.include_router(webhook_router, tags=["WhatsApp Webhook"])
router.include_router(pdf_router, tags=["Pdf Upload"])
router.include_router(user_router, tags="User Admin")






