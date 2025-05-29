from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from models.user import UserModel
from schemas.cooperativa import MotoristaBase


class MotoristaCreate(UserModel):
    nome: str
    telefone: str
    email: EmailStr
    senha: str
    coop_id: str
    em_rota: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "Motorista Exemplo",
                "telefone": "+5511999999999",
                "email": "exemplo@email.com",
                "senha": "senhaSegura123",
                "coop_id": "1",
            }
        }


class MotoristaResponse(MotoristaBase):
    id: str
    rotas: Optional[List[str]] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "1",
                "nome": "Motorista Exemplo",
                "telefone": "+5511999999999",
                "email": "exemplo@email.com",
                "rotas": ["rota1", "rota2"],
            }
        }


class IniciarColetaRequest(BaseModel):
    rota_id: str
    timestamp_inicio: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {"rota_id": "1", "timestamp_inicio": "2023-10-01T08:00:00"}
        }


class FinalizarColetaRequest(BaseModel):
    rota_id: str
    timestamp_fim: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {"rota_id": "1", "timestamp_fim": "2023-10-01T10:00:00"}
        }
