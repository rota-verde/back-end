from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class MotoristaBase(BaseModel):
    nome: str
    telefone: str
    bairo : str
    class Config:
        json_schema_extra = {
            "example": {
                "nome": "Motorista Exemplo",
                "telefone": "+5511999999999",
                "bairro": "Centro"
            }
        }

class RotaBase(BaseModel):
    nome: str
    data: datetime
    motoristas: List[str]
    pontos: Dict[str, float]  # lat/long 
    class Config:
        json_schema_extra = {
            "example": {
                "nome": "Rota Exemplo",
                "data": "2023-10-01T08:00:00",
                "motoristas": ["motorista1", "motorista2"],
                "pontos": {
                    "ponto1": [40.7128, -74.0060],
                    "ponto2": [34.0522, -118.2437]
                }
            }
        }

class RotaUpdate(BaseModel):
    nome: Optional[str]
    data: Optional[datetime]
    motoristas: Optional[List[str]]
    pontos: Optional[Dict[str, float]]
    class Config:
        json_schema_extra = {
            "example": {
                "nome": "Rota Atualizada",
                "data": "2023-10-01T08:00:00",
                "motoristas": ["motorista1", "motorista2"],
                "pontos": {
                    "ponto1": [40.7128, -74.0060],
                    "ponto2": [34.0522, -118.2437]
                }
            }
        }

class Tutorial(BaseModel):
    id: str
    titulo: str
    conteudo: str
