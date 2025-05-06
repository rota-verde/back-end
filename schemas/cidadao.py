from pydantic import BaseModel
from typing import List, Optional

class ResidenciaCreate(BaseModel):
    endereco: str
    numero: str
    bairro: str
    cidade: str

class ResidenciaResponse(ResidenciaCreate):
    id: str
    coletavel: bool = False

class FeedbackColeta(BaseModel):
    residencia_id: str
    rota_id: str
    coleta_confirmada: bool
