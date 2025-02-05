from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
import torch
from models.user_model import UserDB
from vector_db.chroma_utils import ChromaClient
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_deepseek import ChatDeepSeek
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from huggingface_hub import login  # Importación necesaria para iniciar sesión en Hugging Face
import os

class LanguageModel:
    def __init__(self):
        # Inicialización de la base de datos de usuarios y el cliente de Chroma
        self.user_model = UserDB()
        self.chroma_client = ChromaClient(persist_directory="./chroma_db")
        self.hf_api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        
    async def generate_response(self, user_message: str) -> str:
        user_id = "679d76229037d7466b684ada"
        try:
            # Obtención del prompt del sistema desde la base de datos de usuarios
            system_prompt = await self.user_model.get_system_prompt(user_id)
            
            # Iniciar sesión en Hugging Face (se solicitará tu clave HF y se guardará localmente)
            login(token=self.hf_api_token) 
            
            # Configuración del modelo de Hugging Face para generación de texto
            llm = HuggingFaceEndpoint(
                repo_id="microsoft/Phi-3-mini-4k-instruct",
                task="text-generation",
                max_new_tokens=512,   # Longitud máxima de respuesta
                do_sample=False,
                repetition_penalty=1.03,
            )
            
            # Creación del prompt combinando el mensaje del sistema y el del usuario
            prompt = ChatHuggingFace.from_messages(
                [
                    ("system", system_prompt),
                    ("human", user_message),
                ]
            )
            
            # Creación de la cadena que combina documentos
            chain = create_stuff_documents_chain(llm, prompt)
            
            # Creación de la cadena de recuperación (RAG: Retrieval-Augmented Generation)
            rag = create_retrieval_chain(self.retriever, chain)
            
            # Ejecución de la cadena para generar la respuesta
            results = rag.invoke({"input": user_message})
            return results.get('answer', "No se pudo generar una respuesta.")
        
        except Exception as e:
            return f"Error: {str(e)}"
