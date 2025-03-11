from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from typing import List, Optional
import re

# Mixin para campos de tiempo
class TimestampMixin(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha de última actualización")

# Modelo para texto de mensaje
class MessageText(BaseModel):
    body: str

# Modelo para mensaje
class Message(BaseModel):
    from_: str = Field(alias="from")
    id: str
    timestamp: str
    text: Optional[MessageText] = None
    type: str

    class Config:
        allow_population_by_field_name = True

# Modelo para valor de cambio
class ChangeValue(BaseModel):
    messaging_product: str = Field(alias="messaging_product")
    metadata: dict
    messages: List[Message]

    @validator("messages")
    def validate_messages(cls, value):
        if not value:
            raise ValueError("La lista de mensajes no puede estar vacía")
        return value

# Modelo para cambio
class Change(BaseModel):
    value: ChangeValue
    field: str

# Modelo para entrada
class Entry(BaseModel):
    id: str
    changes: List[Change]

# Modelo para evento de WhatsApp
class WhatsAppEvent(BaseModel):
    object: str
    entry: List[Entry]

# Modelo para system prompt
class SystemPromptModel(TimestampMixin):
    instruction: str = Field(..., description="Instrucción personalizada del system prompt")
    user_id: str = Field(..., description="Id del usuario dueño del system prompt")

    def update_instruction(self, new_instruction: str):
        self.instruction = new_instruction
        self.updated_at = datetime.utcnow()

# Modelo para usuario
class UserModel(TimestampMixin):
    name: str = Field(..., description="Nombre del usuario")
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    phone: str = Field(..., description="Número de teléfono del usuario")

    @validator("phone")
    def validate_phone(cls, value):
        if not re.match(r"^\+?[0-9]{10,15}$", value):
            raise ValueError("El número de teléfono debe tener entre 10 y 15 dígitos y puede incluir un '+' al inicio")
        return value