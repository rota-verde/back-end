from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MotoristaCreate(BaseModel):
    nome: str
    telefone: str
    senha: str
    

class IniciarColetaRequest(BaseModel):
    rota_id: str
    timestamp_inicio: Optional[datetime] = None

class FinalizarColetaRequest(BaseModel):
    rota_id: str
    timestamp_fim: Optional[datetime] = None
