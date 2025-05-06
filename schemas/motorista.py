from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from schemas.cooperativa import MotoristaBase

class MotoristaCreate(BaseModel):
    nome: str
    telefone: str
    email: str
    senha: str

class MotoristaResponse(MotoristaBase):
    id: str
    rotas: Optional[List[str]] = []
    
class IniciarColetaRequest(BaseModel):
    rota_id: str
    timestamp_inicio: Optional[datetime] = None

class FinalizarColetaRequest(BaseModel):
    rota_id: str
    timestamp_fim: Optional[datetime] = None
