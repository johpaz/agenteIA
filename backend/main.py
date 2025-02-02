from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import router as api_router
from config.config import settings
from config.database import db

# Inicialización de la aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Backend para el chatbot de WhatsApp"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes (ajusta según sea necesario)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Evento de inicio: Conectar a la base de datos
@app.on_event("startup")
async def startup():
    await db.connect_to_database()
    
# Incluir rutas
app.include_router(api_router, prefix="/api")

# Evento de inicio
@app.on_event("startup")
async def startup_event():
    print("🚀 Aplicación iniciada. Conectada a MongoDB y lista para recibir mensajes.")

# Evento de cierre
@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Aplicación detenida. Conexiones cerradas.")