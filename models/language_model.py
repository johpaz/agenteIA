from fastapi.concurrency import run_in_threadpool
from transformers import AutoTokenizer, AutoModelForCausalLM

class LanguageModel:
    def __init__(self, model_name: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"):
        """
        Inicializa el modelo de lenguaje.
        Args:
            model_name (str): Nombre del modelo a cargar.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

    async def generate_response(self, messages: list, max_length: int = 150) -> str:
        """
        Genera una respuesta basada en una lista de mensajes con roles.
        Args:
            messages (list): Lista de mensajes con roles ("system", "user", "assistant").
            max_length (int): Longitud máxima de la respuesta generada.
        Returns:
            str: Respuesta generada.
        """
        try:
            # Aplicar el template de chat al tokenizer
            inputs = self.tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                return_tensors="pt",
                add_generation_prompt=True  # Añade el prompt para que el modelo genere una respuesta
            )

            # Generar respuesta en un hilo separado
            outputs = await run_in_threadpool(
                self.model.generate,
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=max_length
            )

            # Decodificar la respuesta
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extraer solo la parte generada por el modelo (después del último mensaje del usuario)
            last_user_message_index = response.rfind("<|user|>")
            if last_user_message_index != -1:
                response = response[last_user_message_index:].split("<|assistant|>")[-1].strip()

            return response

        except Exception as e:
            print(f"Error al generar la respuesta: {str(e)}")
            return "Hubo un error al procesar tu mensaje. Por favor, inténtalo de nuevo."