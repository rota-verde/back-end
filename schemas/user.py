from pydantic import BaseModel, EmailStr
from typing import List, Optional
from models.user import UserModel
from models.residencia import EnderecoModel


class UserBase(UserModel):
    nome_usuario: str
    email: EmailStr
    telefone: str
    role: str  # "cidadao", "cooperativa" ou "motorista"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "nome_usuario": "João Silva",
                "email": "joao@email.com",
                "telefone": "+5511999999999",
                "role": "cidadao",
            }
        }


class UserCreate(UserModel):
    uid: str
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    cnh: Optional[str] = None
    nome_usuario: Optional[str] = None
    nome_cooperativa: Optional[str] = None
    area_atuacao: Optional[List[str]] = None
    materiais_reciclaveis: Optional[List[str]] = None
    cooperativa_id: Optional[str] = None
    auth_2fa_enabled: Optional[bool] = False

    class Config:
        json_schema_extra = {
            "example": {
                "nome_usuario": "João Silva",
                "email": "joao@email.com",
                "telefone": "+5511999999999",
                "role": "cidadao",
                "senha": "senha_secreta",
                "cpf": "12345678909",
                "cnpj": "12345678",
                "cnh": "12355",
                "nome_cooperativa": "coop",
                "area_atuacao": ["Centro", "Farol"],
                "endereco": {
                    "logradouro": "Rua Exemplo",
                    "numero": "123",
                    "bairro": "Centro",
                    "cidade": "Cidade Exemplo",
                },
                "materiais_reciclaveis": ["papel", "plástico", "vidro"],
            }
        }


class UserLogin(BaseModel):
    email: EmailStr
    senha: str

    class Config:
        json_schema_extra = {
            "example": {"email": "joao@email.com", "senha": "senha_secreta"}
        }


class UserResponse(UserBase):
    uid: str
    nome_usuario: str
    email: EmailStr
    telefone: str
    role: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "uid": "1234567890",
                "nome_usuario": "João Silva",
                "email": "joao@email.com",
                "telefone": "+5511999999999",
                "role": "cidadao",
            }
        }
