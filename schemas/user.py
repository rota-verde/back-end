from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserCreate(BaseModel):
    nome_usuario: str
    telefone: str
    senha: str
    role: str  # cidadao | cooperativa | motorista

class UserLogin(BaseModel):
    email: str
    senha: str

class UserResponse(BaseModel):
    uid: str
    nome_usuario: str
    telefone: str
    role: str
    residencias: Optional[List[str]]
    cooperativa_id: Optional[str]
