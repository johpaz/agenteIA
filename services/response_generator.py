from models.language_model import LanguageModel
from models.user_model import UserDB
from typing import Dict, Any

class ResponseGenerator:
    def __init__(self):
        """
        Inicializa el generador de respuestas.
        """
        self.language_model = LanguageModel()
        self.user_model = UserDB()

    
    async def generate_response(self, user_message: str) -> str:
        try:
            user_id = "679d76229037d7466b684ada"
            print(f"Usuario: {user_id} | Mensaje: {user_message}")
            
            # Recuperar el system prompt del usuario
            system_prompt = await self.user_model.get_system_prompt(user_id)
            if not system_prompt:
                return "Por favor, crea tu System Prompt antes de continuar."
            
            # Recuperar información relevante de la base de datos vectorial
            retrieved_context = await self.vector_db.retrieve_context(user_message)
            
            # Construir la lista de mensajes con roles
            messages = [
                {"role": "system", "content": system_prompt.instruction},
                {"role": "user", "content": f"Contexto relevante:\n{retrieved_context}\n\nPregunta: {user_message}"},
            ]
            
            # Llamada al modelo de lenguaje
            response = await self.language_model.generate_response(messages)
        
            return response
        except Exception as e:
            print(f"Error al generar la respuesta: {str(e)}")
            return "Hubo un error al procesar tu mensaje. Por favor, inténtalo de nuevo."