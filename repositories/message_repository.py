from typing import List, Optional
from bson import ObjectId  # Para manejar IDs de MongoDB
from models.model import Message  # Modelo de mensaje
from motor.motor_asyncio import AsyncIOMotorClient
from config.config import settings

class MessageRepository:
    def __init__(self):
        """
        Inicializa el repositorio conectándose a MongoDB.
        """
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db["messages"]

    async def create_message(self, message: dict) -> str:
        """
        Inserta un nuevo mensaje en la base de datos.
        Args:
            message (dict): Datos del mensaje a insertar.
        Returns:
            str: ID del mensaje insertado.
        Raises:
            Exception: Si ocurre un error al insertar el mensaje.
        """
        try:
            result = await self.collection.insert_one(message)
            return str(result.inserted_id)  # Convertimos el ObjectId a string para mayor compatibilidad
        except Exception as e:
            print(f"Error al insertar en MongoDB: {str(e)}")
            raise

    async def get_messages_by_number(self, phone_number: str, limit: int = 50) -> List[Message]:
        """
        Obtiene los mensajes más recientes de un número de teléfono específico.
        Args:
            phone_number (str): Número de teléfono del remitente.
            limit (int): Número máximo de mensajes a recuperar.
        Returns:
            List[Message]: Lista de mensajes encontrados.
        """
        try:
            messages_cursor = self.collection.find(
                {"from_number": phone_number}
            ).sort("timestamp", -1).limit(limit)

            messages = await messages_cursor.to_list(length=limit)
            return [Message(**msg) for msg in messages]  # Convertimos cada documento en un objeto Message
        except Exception as e:
            print(f"Error al obtener mensajes de MongoDB: {str(e)}")
            raise

    async def update_message(self, message_id: str, new_data: dict) -> bool:
        """
        Actualiza un mensaje existente en la base de datos.
        Args:
            message_id (str): ID del mensaje a actualizar.
            new_data (dict): Datos actualizados para el mensaje.
        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario.
        """
        try:
            # Convertimos el ID de string a ObjectId para MongoDB
            result = await self.collection.update_one(
                {"_id": ObjectId(message_id)},
                {"$set": new_data}
            )
            return result.modified_count > 0  # Retorna True si se modificó al menos un documento
        except Exception as e:
            print(f"Error al actualizar el mensaje en MongoDB: {str(e)}")
            raise

    async def delete_message(self, message_id: str) -> bool:
        """
        Elimina un mensaje de la base de datos.
        Args:
            message_id (str): ID del mensaje a eliminar.
        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario.
        """
        try:
            result = await self.collection.delete_one({"_id": ObjectId(message_id)})
            return result.deleted_count > 0  # Retorna True si se eliminó al menos un documento
        except Exception as e:
            print(f"Error al eliminar el mensaje en MongoDB: {str(e)}")
            raise

    async def get_message_by_id(self, message_id: str) -> Optional[Message]:
        """
        Obtiene un mensaje por su ID.
        Args:
            message_id (str): ID del mensaje a buscar.
        Returns:
            Optional[Message]: El mensaje encontrado, o None si no existe.
        """
        try:
            message = await self.collection.find_one({"_id": ObjectId(message_id)})
            return Message(**message) if message else None
        except Exception as e:
            print(f"Error al buscar mensaje en MongoDB: {str(e)}")
            raise