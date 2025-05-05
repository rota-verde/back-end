from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MotoristaBase(BaseModel):
    nome: str
    telefone: str
    area_abertura: str

class MotoristaCreate(MotoristaBase):
    senha: str

class MotoristaResponse(MotoristaBase):
    id: str
    rotas: Optional[List[str]] = []

class RotaBase(BaseModel):
    nome: str
    data: datetime
    motoristas: List[str]
    pontos: List[str]  # ids das residências

class RotaCreate(RotaBase):
    pass

class RotaUpdate(BaseModel):
    nome: Optional[str]
    data: Optional[datetime]
    motoristas: Optional[List[str]]
    pontos: Optional[List[str]]

class RotaResponse(RotaBase):
    id: str
    feedbacks: Optional[int] = 0
