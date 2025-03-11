from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
import operator
from pinecone import Pinecone, ServerlessSpec
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from models.user_model import UserDB
from sentence_transformers import SentenceTransformer
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
from config.config import settings

# Configuración de logging
logger = logging.getLogger(__name__)
load_dotenv()

# Modelo de estado para el grafo
class AgentState(TypedDict):
    input: str
    context: Optional[str]
    system_prompt: Optional[str]
    response: Optional[str]
    user_id: str
    valid: Optional[bool]

class EnhancedAIAssistant:
    def __init__(self):
        self.user_model = UserDB()  # Mantenemos MongoDB para system prompts
        self._setup_vector_db()
        self._setup_llm()
        self._setup_graph()
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def _setup_vector_db(self):
        """Configuración optimizada de Pinecone"""
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = "chatbot"
        
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=384,  # Dimensión de all-MiniLM-L6-v2
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-west-2")
            )
        self.index = self.pc.Index(self.index_name)

    def _setup_llm(self):
        """Configuración del modelo sin cuantización y con un modelo más pequeño"""
        self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")  # Modelo más pequeño
        self.model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Llama-3.2-3B-Instruct",
            device_map="cpu",  # Usar CPU en lugar de GPU
            offload_folder="./offload"
        )

    def _setup_graph(self):
        """Grafo mejorado con manejo de errores"""
        workflow = StateGraph(AgentState)
        
        workflow.add_node("retrieve", self.retrieve_context)
        workflow.add_node("get_prompt", self.get_system_prompt)
        workflow.add_node("generate", self.generate_response)
        workflow.add_node("validate", self.validate_response)
        workflow.add_node("handle_error", self.handle_error)
        
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "get_prompt")
        workflow.add_edge("get_prompt", "generate")
        workflow.add_edge("generate", "validate")
        
        workflow.add_conditional_edges(
            "validate",
            self.needs_correction,
            {"REPEAT": "generate", "END": END}
        )
        
        workflow.add_edge("handle_error", END)
        self.workflow = workflow.compile()

    async def retrieve_context(self, state: AgentState):
        """Búsqueda semántica mejorada"""
        try:
            query = state["input"]
            embedding = self.embedder.encode(query).tolist()
            
            results = self.index.query(
                vector=embedding,
                top_k=3,
                include_metadata=True,
                namespace="courses"
            )
            
            matches = results.get("matches", [])
            if not matches:
                logger.warning("No se encontraron resultados para la consulta.")
                state["context"] = "Sin resultados encontrados"
            else:
                state["context"] = "\n".join(
                    f"- {match['metadata']['content']}" for match in matches
                )
        except Exception as e:
            logger.error(f"Error en búsqueda: {str(e)}")
            state["context"] = "Sin resultados encontrados"
        return state

    async def get_system_prompt(self, state: AgentState):
        """Obtener prompt desde MongoDB"""
        try:
            user_data = await self.user_model.get_user(state["user_id"])
            state["system_prompt"] = user_data.get(
                "custom_prompt",
                self._default_prompt()
            )
        except Exception as e:
            logger.error(f"Error obteniendo prompt: {str(e)}")
            state["system_prompt"] = self._default_prompt()
        return state

    async def generate_response(self, state: AgentState):
        """Generación optimizada de respuestas"""
        try:
            prompt = self._format_prompt(state)
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=2048,
                truncation=True
            ).to(self.model.device)
            
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
            
            state["response"] = self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:], 
                skip_special_tokens=True
            )
        except Exception as e:
            logger.error(f"Error en generación: {str(e)}")
            state["response"] = None
        return state

    async def validate_response(self, state: AgentState):
        """Validación de calidad de respuesta"""
        response = state.get("response", "")
        invalid_phrases = ["no sé", "no tengo información"]

        valid = (
            bool(response) and
            len(response) >= 30 and
            not any(phrase in response.lower() for phrase in invalid_phrases)
        )

        return {**state, "valid": valid}

    def needs_correction(self, state: AgentState):
        return "REPEAT" if not state.get("valid") else "END"

    async def handle_error(self, state: AgentState):
        """Manejo centralizado de errores"""
        return {
            "response": self._fallback_response(),
            "status": "error"
        }

    def _format_prompt(self, state: AgentState):
        return f"""<|system|>
{state['system_prompt']}
Contexto: {state.get('context', '')}
<|user|>
{state['input']}
<|assistant|>"""

    def _default_prompt(self):
        return """Eres un asistente especializado en IA. Proporciona respuestas precisas y útiles basadas en el contexto proporcionado."""

    def _fallback_response(self):
        return {
            "status": "error",
            "response": "Estamos experimentando dificultades técnicas. Por favor intenta nuevamente.",
            "timestamp": datetime.now().isoformat()
        }

    async def process_query(self, user_input: str, user_id: str):
        """Flujo principal mejorado"""
        try:
            initial_state = AgentState(
                input=user_input,
                user_id=user_id,
                context="",
                system_prompt=self._default_prompt(),
                response="",
                valid=False
            )
            
            async for state in self.workflow.astream(initial_state):
                if END in state:
                    return state[END].get("response", "No se pudo generar respuesta")
            
            return "No se pudo generar respuesta"
        
        except Exception as e:
            logger.error(f"Error en proceso: {str(e)}")
            return self._fallback_response()