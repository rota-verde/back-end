from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class MotoristaBase(BaseModel):
    nome: str
    telefone: str
    bairo : str

class RotaBase(BaseModel):
    nome: str
    data: datetime
    motoristas: List[str]
    pontos: Dict[str, float]  # lat/long 

class RotaUpdate(BaseModel):
    nome: Optional[str]
    data: Optional[datetime]
    motoristas: Optional[List[str]]
    pontos: Optional[Dict[str, float]]

class Tutorial(BaseModel):
    id: str
    titulo: str
    conteudo: str
