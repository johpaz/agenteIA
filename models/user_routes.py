from fastapi import APIRouter, HTTPException
from models.user_model import UserDB, UserModel , SystemPromptModel


# Crear un solo objeto router para todas las rutas
router = APIRouter()
user_db = UserDB()

# Endpoint para guardar un usuario
@router.post("/create-user", tags=["User"])
async def create_user(user: UserModel):
    """
    Guarda un usuario en MongoDB.
    Args:
        user (UserModel): Datos del usuario.
    Returns:
        dict: Confirmación de la operación.
    """
    try:
        
        result = user_db.save_user(user.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el usuario: {str(e)}")

# Endpoint para recuperar un usuario
@router.get("/get-user/{user_id}", tags=["User"])
async def get_user(user_id: str):
    """
    Recupera un usuario desde MongoDB.
    Args:
        user_id (str): ID del usuario.
    Returns:
        dict: Datos del usuario.
    """
    try:
        user = user_db.get_user(user_id)
        return user.dict()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Usuario no encontrado: {str(e)}")

# Endpoint para guardar el system prompt del usuario
@router.post("/set-system-prompt", tags=["System Prompt"])
async def set_system_prompt( system_promt:SystemPromptModel):
    """
    Guarda el system prompt del usuario en MongoDB.
    Args:
        user_id (str): ID del usuario.
        instruction (str): Instrucción del system prompt.
    Returns:
        dict: Confirmación de la operación.
    """
    try:
        result = user_db.save_system_prompt(system_promt.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el system prompt: {str(e)}")

# Endpoint para recuperar el system prompt del usuario
@router.get("/get-system-prompt/{user_id}", tags=["System Prompt"])
async def get_system_prompt(user_id: str):
    """
    Recupera el system prompt del usuario desde MongoDB.
    Args:
        user_id (str): ID del usuario.
    Returns:
        dict: System prompt del usuario.
    """
    try:
        system_prompt = user_db.get_system_prompt(user_id)
        return system_prompt.dict()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"System prompt no encontrado: {str(e)}")