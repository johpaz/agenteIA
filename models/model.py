from pydantic import  BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class Message(BaseModel):
    from_number: str
    body: str
    timestamp: datetime
    id: Optional[str] = None  # ID opcional para mapear con MongoDB
    
    
    # Modelo Pydantic para el System Prompt
class SystemPromptModel(BaseModel):
    instruction: str = Field(..., description="Instrucción personalizada del system prompt")
    user_id:  str = Field(..., description="Id del usuario dueño del system prompt")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha de última actualización")
    

    # Modelo Pydantic para el Usuario
class UserModel(BaseModel):
    name: str = Field(..., description="Nombre del usuario")
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    phone: str = Field(..., description="Número de teléfono del usuario")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha de última actualización")
    
    

