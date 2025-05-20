from pydantic import BaseModel
from typing import Dict, List
from datetime import date, time

class FeedbackSchema(BaseModel):
    residencia_id: str
    coletado: bool
    class Config:
        json_schema_extra = {
            "example": {
                "residencia_id": "residencia1",
                "coletado": True
            }
        }

class RouteCreate(BaseModel):
    motorista_id: str
    residencias_incluidas_ids: List[str]
    bairro: str
    data: date
    hora_inicio: time
    pontos: Dict[str, List[float]]   # agora lista de floats
    class Config:
        json_schema_extra = {
            "example": {
                "motorista_id": "1",
                "residencias_incluidas_ids": ["residencia1", "residencia2"],
                "bairro": "Centro",
                "data": "2023-10-01",
                "hora_inicio": "08:00:00",
                "pontos": {
                    "ponto1": [40.7128, -74.0060],
                    "ponto2": [34.0522, -118.2437]
                }
            }
        }

class RouteResponse(BaseModel):
    id: str
    cooperativa_id: str
    motorista_id: str
    residencias_incluidas_ids: List[str]
    data: date
    hora_inicio: time
    status: bool
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "1",
                "cooperativa_id": "1",
                "motorista_id": "1",
                "residencias_incluidas_ids": ["residencia1", "residencia2"],
                "data": "2023-10-01",
                "hora_inicio": "08:00:00",
                "status": "True",
            }
        }