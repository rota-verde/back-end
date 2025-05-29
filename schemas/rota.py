from pydantic import BaseModel
from typing import Dict, List
from datetime import date, time


class FeedbackSchema(BaseModel):
    residencia_id: str
    coletado: bool

    class Config:
        json_schema_extra = {
            "example": {"residencia_id": "residencia1", "coletado": True}
        }


class RouteCreate(BaseModel):
    motorista_id: str
    residencias_incluidas_ids: List[str]
    bairro: str
    data: date
    hora_inicio: time
    pontos: Dict[str, List[float]]  # cada ponto é [latitude, longitude]

    class Config:
        json_schema_extra = {
            "example": {
                "motorista_id": "1",
                "residencias_incluidas_ids": ["residencia1", "residencia2"],
                "bairro": "Centro",
                "data": "2023-10-01",
                "hora_inicio": "08:00:00",
                "pontos": {
                    "fixo_0": [-9.649848, -35.708949],
                    "fixo_1": [-9.660184, -35.735163],
                    "residencia1": [-23.5505, -46.6333],
                    "residencia2": [-23.5510, -46.6340],
                },
            }
        }


class RouteResponse(BaseModel):
    id: str
    cooperativa_id: str
    motorista_id: str
    residencias_incluidas_ids: List[str]
    bairro: str
    data: date
    hora_inicio: time
    status: bool
    pontos: Dict[str, List[float]]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "f3e8b29a-4a87-4e13-9125-bf17f8677e13",
                "cooperativa_id": "bCoop123",
                "motorista_id": "motorista456",
                "residencias_incluidas_ids": [
                    "7154fa6d-cc84-4326-a0af-e3ea8c1770d4",
                    "efcee48a-2cfd-4fed-8e67-b21d6c3f39f1",
                ],
                "bairro": "Centro",
                "data": "2025-05-22",
                "hora_inicio": "08:00:00",
                "status": True,
                "pontos": {
                    "fixo_0": [-9.649848, -35.708949],
                    "fixo_1": [-9.660184, -35.735163],
                    "7154fa6d-cc84-4326-a0af-e3ea8c1770d4": [-23.5505, -46.6333],
                    "efcee48a-2cfd-4fed-8e67-b21d6c3f39f1": [-23.5510, -46.6340],
                },
            }
        }
