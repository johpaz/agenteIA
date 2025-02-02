from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
from config.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db: Database = None

    async def connect_to_database(self):
        """Conecta a la base de datos MongoDB utilizando la URL y el nombre de la base de datos de la configuración."""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = self.client[settings.DATABASE_NAME]
            print("Conexión a la base de datos establecida.")
        except Exception as e:
            print(f"Error al conectar a la base de datos: {str(e)}")
            raise

    async def close_database_connection(self):
        """Cierra la conexión a la base de datos."""
        if self.client is not None:
            self.client.close()
            print("Conexión a la base de datos cerrada.")

# Instancia de la clase MongoDB
db = MongoDB()
    