from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated, Optional
import operator
from pinecone import Pinecone, ServerlessSpec
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from models.user_model import UserDB
import os
from dotenv import load_dotenv
from datetime import datetime
from config.config import settings
from functools import partial

load_dotenv()

# Configuración mejorada del estado
class AgentState(TypedDict):
    input: str
    context: Optional[str]
    system_prompt: Optional[str]
    response: Optional[str]
    user_id: str  # Nuevo campo para contexto de usuario

class EnhancedAIAssistant:
    def __init__(self):
        self._setup_vector_db()  # Nueva base vectorial
        self._setup_llm()
        self._setup_graph()
        self.user_model = UserDB()

    def _setup_vector_db(self):
        """Configuración de Pinecone para mejor escalabilidad"""
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = "chatbot"
        
        # Crear índice si no existe
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # Compatible con embeddings de OpenAI
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-west-2"
                )
            )
        
        self.index = self.pc.Index(self.index_name)

    def _setup_llm(self):
        """Configuración mejorada del modelo LLM"""
        self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.3-70B-Instruct")
        self.model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Llama-3.3-70B-Instruct",
            device_map="auto",
            torch_dtype=torch.bfloat16
        )
        self.chat_template = self._create_chat_template()

    def _create_chat_template(self):
        return [
            {"role": "system", "content": "{system_prompt}\nContexto: {context}"},
            {"role": "user", "content": "{input}"}
        ]

    def _setup_graph(self):
        """Configuración del grafo LangGraph con flujo mejorado"""
        workflow = StateGraph(AgentState)
        
        # Definición de nodos
        workflow.add_node("retrieve", self.retrieve_context)
        workflow.add_node("get_prompt", self.get_system_prompt)
        workflow.add_node("generate", self.generate_response)
        workflow.add_node("validate", self.validate_response)
        
        # Conexiones mejoradas con validación
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "get_prompt")
        workflow.add_edge("get_prompt", "generate")
        workflow.add_edge("generate", "validate")
        workflow.add_conditional_edges(
            "validate",
            self.needs_correction,
            {"REPEAT": "generate", "END": END}
        )
        
        self.workflow = workflow.compile()

    async def retrieve_context(self, state: AgentState):
        """Búsqueda mejorada con Pinecone"""
        try:
            # Aquí deberías generar embeddings (usar modelo de embeddings)
            # Ejemplo simplificado:
            query_embedding = [0.5]*1536  # Reemplazar con embeddings reales
            
            results = self.index.query(
                vector=query_embedding,
                top_k=5,
                include_values=True,
                namespace="courses"
            )
            state["context"] = "\n".join(
                f"- {match['metadata']['content']}" 
                for match in results.matches
            )
        except Exception as e:
            print(f"Error en búsqueda: {e}")
            state["context"] = "No se encontró contexto relevante"
        return state

    async def get_system_prompt(self, state: AgentState):
        """Obtener prompt con manejo mejorado de errores"""
        try:
            user_data = await self.user_model.get(state["user_id"])
            state["system_prompt"] = user_data.get(
                "custom_prompt",
                self._default_prompt()
            )
        except Exception as e:
            print(f"Error obteniendo prompt: {e}")
            state["system_prompt"] = self._default_prompt()
        return state

    async def generate_response(self, state: AgentState):
        """Generación con plantilla dinámica"""
        messages = self._format_messages(state)
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        try:
            outputs = await self.model.async_generate(
                inputs,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True
            )
            state["response"] = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )
        except Exception as e:
            print(f"Error en generación: {e}")
            state["response"] = None
        return state

    def _format_messages(self, state: AgentState):
        return [{
            "role": "system",
            "content": f"{state['system_prompt']}\nContexto: {state.get('context', '')}"
        }, {
            "role": "user",
            "content": state["input"]
        }]

    async def validate_response(self, state: AgentState):
        """Validación mejorada con modelo de criterios"""
        # Implementar lógica de validación aquí
        return state

    def needs_correction(self, state: AgentState):
        """Decide si se necesita corrección"""
        return "REPEAT" if not state.get("response") else "END"

    def _default_prompt(self):
        return """Eres un asistente especializado en IA y cursos tecnológicos. 
Proporciona respuestas útiles y precisas basadas en el contexto."""

    async def process_query(self, user_input: str, user_id: str):
        """Flujo principal mejorado"""
        try:
            initial_state = AgentState(
                input=user_input,
                user_id=user_id,
                context=None,
                system_prompt=None,
                response=None
            )
            
            async for state in self.workflow.astream(initial_state):
                if END in state:
                    return state[END].get("response")
                    
            return "No se pudo generar respuesta"
            
        except Exception as e:
            print(f"Error en proceso: {e}")
            return self._fallback_response()

    def _fallback_response(self):
        return {
            "status": "error",
            "response": "Estamos experimentando dificultades técnicas. Por favor intenta nuevamente.",
            "timestamp": datetime.now().isoformat()
        }