from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
import torch
from datasets import Dataset

class FineTuner:
    def __init__(self, model_name: str = "meta-llama/Llama-2-13b-chat-hf"):
        """
        Inicializa el fine-tuner.
        Args:
            model_name (str): Nombre del modelo a ajustar.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

    def fine_tune(self, training_data: list, output_dir: str = "./fine-tuned"):
        """
        Realiza el fine-tuning del modelo con datos específicos.
        Args:
            training_data (list): Datos de entrenamiento (pares de pregunta-respuesta).
            output_dir (str): Directorio donde guardar el modelo ajustado.
        """
        # Convertir datos de entrenamiento en un formato compatible con Hugging Face
        dataset = Dataset.from_dict({
            "text": [f"Contexto: {item['context']}\nPregunta: {item['question']}\nRespuesta: {item['answer']}" for item in training_data]
        })

        def tokenize_function(examples):
            return self.tokenizer(examples["text"], padding="max_length", truncation=True)

        tokenized_dataset = dataset.map(tokenize_function, batched=True)

        # Configurar el fine-tuning
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=2,
            save_steps=10,
            save_total_limit=2,
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
        )

        # Entrenar
        trainer.train()

        # Guardar el modelo ajustado
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)