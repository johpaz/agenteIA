from models.language_model import LanguageModel
from models.user_model import UserDB
from vector_db.chroma_utils import ChromaClient  # Importa la nueva clase

class ResponseGenerator:
    def __init__(self,):
        """
        Inicializa el generador de respuestas.
        """
        self.language_model = LanguageModel()
        self.user_model = UserDB()
        self.chroma_client = ChromaClient(persist_directory="./chroma_db")

    async def generate_response(self, user_message: str) -> str:
        try:
            user_id = "679d76229037d7466b684ada"
            print(f"📩 Usuario: {user_id} | Mensaje: {user_message}")
            
            # 🔹 Recuperar el System Prompt
            system_prompt = await self.user_model.get_system_prompt(user_id)
            if not system_prompt or not system_prompt.instruction:
                return "Por favor, crea tu System Prompt antes de continuar."
            
            # 🔹 Generar embedding para la consulta
            query_embedding = self.chroma_client.generate_embeddings(user_message,user_id)
            
            # 🔹 Consultar en ChromaDB
            retrieved_context = self.chroma_client.query_data(query_embedding)
            context_results = retrieved_context.get('results', [])
            
            if not context_results:
                print("⚠️ No se encontró contexto relevante. Respondiendo con el System Prompt.")
                messages = [
                    {"role": "system", "content": system_prompt.instruction},
                    {"role": "user", "content": user_message}
                ]
            else:
                # 🔹 Construir mensaje con el contexto recuperado
                context = "\n".join(context_results)
                messages = [
                    {"role": "system", "content": system_prompt.instruction},
                    {"role": "user", "content": f"Contexto relevante:\n{context}\n\nPregunta: {user_message}"}
                ]

            print(f"📩 Mensajes enviados al modelo: {messages}")

            # 🔹 Llamada al modelo de lenguaje con atención correcta
            response = await self.language_model.generate_response(
                messages=messages,
                 # Agregar si el modelo lo soporta
            )

            print("📤 Respuesta generada:", response)
            return response if response else "No pude generar una respuesta. Inténtalo de nuevo."

        except Exception as e:
            print(f"❌ Error al generar la respuesta: {str(e)}")
            return "Hubo un error al procesar tu mensaje. Por favor, inténtalo de nuevo."
