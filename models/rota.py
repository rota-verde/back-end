from pydantic import BaseModel, Field # type: ignore
from typing import List, Optional
from datetime import datetime

class ResidenciaNaRota(BaseModel):
    id_residencia: str
    endereco: str
    confirmado_pelo_cidadao: bool = False
    vai_disponibilizar_reciclavel: bool = False
    hora_prevista_passagem: Optional[str] = None

class RotaBase(BaseModel):
    id: str
    titulo: str
    descricao: Optional[str] = None
    data_coleta: str 
    hora_inicio: str
    cooperativa_id: str
    cooperativa_nome: Optional[str]
    status: str = Field(default="agendada") 
    residencias: List[ResidenciaNaRota] = []
    pontos_mapa: List[dict]  # latitude/longitude dos pontos da rota???

class RotaCreate(RotaBase):
    pass

class RotaResponse(RotaBase):
    relatorio_final: Optional[str] = None
    feedbacks: Optional[List[str]] = []