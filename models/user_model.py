from pydantic import BaseModel, Field, EmailStr
from pymongo import MongoClient
from bson import SON
from datetime import datetime
import os
from models.model import UserModel 
from models.model import SystemPromptModel
from config.database import db
from motor.motor_asyncio import AsyncIOMotorClient 
from config.config import settings



class UserDB:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db["users"]
        self.collection = self.db["system_promt"]

    def save_user(self, user_data: dict):
        """
        Guarda o actualiza un usuario en MongoDB.
        Args:
            user_data (dict): Datos del usuario.
        Returns:
            dict: Confirmación de la operación.
        """
        # Validar el modelo Pydantic
        user = UserModel(**user_data)

        # Guardar en MongoDB
        self.collection.update_one(
            {"email": user.email},
            {
                "$set": user.dict(exclude={"created_at"}),
                "$setOnInsert": {"created_at": user.created_at}
            },
            upsert=True
        )
        return {"message": "Usuario guardado exitosamente."}

    def get_user(self, user_id: str) -> UserModel:
        """
        Recupera un usuario desde MongoDB.
        Args:
            user_id (str): ID del usuario.
        Returns:
            UserModel: Datos del usuario.
        """
        user_data = self.collection.find_one({"_id": user_id})
        if user_data:
            return UserModel(**user_data)
        raise ValueError(f"No se encontró ningún usuario con el ID: {user_id}")

    def save_system_prompt(self,  system_promt_data: dict):
        """
        Guarda o actualiza el system prompt del usuario en MongoDB.
        Args:
            user_id (str): ID del usuario (como string).
            instruction (str): Instrucción del system prompt.
        Returns:
            dict: Confirmación de la operación.
        """
 
        # Validar el modelo Pydantic
        
        system_prompt = SystemPromptModel(**system_promt_data)
        
      
        # Guardar en MongoDB
        self.collection.update_one(
             {"user_id": system_prompt.user_id}, 
            {
                
                    "$set": system_prompt.dict(exclude={"created_at"}),
                "$setOnInsert": {"created_at": system_prompt.created_at}
                },
                upsert=True
                        
        )
        return {"message": "System prompt guardado exitosamente."}


    async def get_system_prompt(self, user_id: str) -> SystemPromptModel:
        """
        Recupera el system prompt del usuario desde MongoDB.
        
        Args:
            user_id (str): ID del usuario.
        
        Returns:
            SystemPromptModel: System prompt del usuario si existe, de lo contrario, None.
        """
        system_prompt_data = await self.collection.find_one({"user_id": user_id})
        
        if system_prompt_data:
            
            return SystemPromptModel(**system_prompt_data)
        else:
            print("Por favor, crea tu System Prompt.")
            return None
