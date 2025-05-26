from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class MotoristaBase(BaseModel):
    nome: str
    telefone: str
    bairro : List[str]
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
    residencias_ids : List[str] #lista id das residencias contempladas pela rota
    class Config:
        json_schema_extra = {
            "example": {
                "nome": "Rota Exemplo",
                "data": "2023-10-01T08:00:00",
                "motoristas": ["motorista1", "motorista2"],
                "pontos": {
                    "ponto1": [40.7128, -74.0060],
                    "ponto2": [34.0522, -118.2437]
                },
                "residencias_ids" : "1"
            }
        }

class RotaUpdate(BaseModel):
    nome: Optional[str]
    data: Optional[datetime]
    motoristas: Optional[List[str]]
    pontos: Optional[Dict[str, float]]
    residencias_ids : List[str] #lista id das residencias contempladas pela rota

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "Rota Atualizada",
                "data": "2023-10-01T08:00:00",
                "motoristas": ["motorista1", "motorista2"],
                "pontos": {
                    "ponto1": [40.7128, -74.0060],
                    "ponto2": [34.0522, -118.2437]
                },
                "residencias_ids" : "1"
            }
        }

class Tutorial(BaseModel):
    id: str
    titulo: str
    conteudo: str

class CooperativaResponse(BaseModel):
    id: str
    nome_usuario: str
    nome_cooperativa: str
    area_atuacao: List[str]
    location: Dict[str, float]
    endereco: Dict[str, List[str]]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123",
                "nome_usuario": "João Silva",
                "nome_cooperativa": "Coop Verde",
                "area_atuacao": ["Reciclagem", "Compostagem"],
                "location": {
                    "latitude": -23.5505,
                    "longitude": -46.6333
                },
                "endereco": {
                    "bairros_atendidos": ["Centro", "Vila Mariana"]
                }
            }
        }
