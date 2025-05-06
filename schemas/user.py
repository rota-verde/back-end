from pydantic import BaseModel, EmailStr
from typing import List, Optional
class UserBase(BaseModel):
    nome_usuario: str
    email: str
    telefone: str
    role: str  # "cidadao", "cooperativa" ou "motorista"

class UserCreate(UserBase):
    senha: str
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    cnh: Optional[str] = None
    nome_cooperativa: Optional[str] = None
    cooperativa_id: Optional[str] = None
    residencias: Optional[List[str]] = None

class UserLogin(BaseModel):
    email: str
    senha: str

class UserResponse(UserBase):
    uid: str
    residencias: Optional[List[str]]
    cooperativa_id: Optional[str]
