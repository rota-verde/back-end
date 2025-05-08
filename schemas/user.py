from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserBase(BaseModel):
    nome_usuario: str
    email: str
    telefone: str
    role: str  # "cidadao", "cooperativa" ou "motorista"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "nome_usuario": "João Silva",
                "email": "joao@email.com",
                "telefone": "+5511999999999",
                "role": "cidadao"
            }
        }

class UserCreate(UserBase):
    senha: str
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    cnh: Optional[str] = None
    nome_cooperativa: Optional[str] = None
    cooperativa_id: Optional[str] = None
    residencias: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "nome_usuario": "João Silva",
                "email": "joao@email.com",
                "telefone": "+5511999999999",
                "role": "cidadao",
                "senha": "senha_secreta",
                "cpf": "12345678909",
                "residencias": ["residencia_1"]
            }
        }

class UserLogin(BaseModel):
    email: str
    senha: str
    class Config:
        json_schema_extra = {
            "example": {
                "email": "joao@email.com",
                "senha": "senha_secreta"
            }
        }

class UserResponse(UserBase):
    uid: str
    nome_usuario: str
    email: EmailStr
    telefone: str
    role: str
    cpf: Optional[str]
    cnpj: Optional[str]
    cnh: Optional[str]
    nome_cooperativa: Optional[str]
    residencias: Optional[List[str]]
    cooperativa_id: Optional[str]
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "uid": "1234567890",
                "nome_usuario": "João Silva",
                "email": "joao@email.com",
                "telefone": "+5511999999999",
                "role": "cidadao",
                "residencias": ["residencia_1"],
            }
        }
