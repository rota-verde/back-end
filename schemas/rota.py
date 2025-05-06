from pydantic import BaseModel
from typing import List
from datetime import date, time

class FeedbackSchema(BaseModel):
    residencia_id: str
    coletado: bool
    class Config:
        schema_extra = {
            "example": {
                "residencia_id": "residencia1",
                "coletado": True
            }
        }

class RouteCreate(BaseModel):
    motorista_id: str
    residencias_incluidas: List[str]
    bairro: str
    data: date
    hora_inicio: time
    class Config:
        schema_extra = {
            "example": {
                "motorista_id": "1",
                "residencias_incluidas": ["residencia1", "residencia2"],
                "bairro": "Centro",
                "data": "2023-10-01",
                "hora_inicio": "08:00:00"
            }
        }

class RouteResponse(BaseModel):
    id: str
    cooperativa_id: str
    motorista_id: str
    residencias_incluidas: List[str]
    data: date
    hora_inicio: time
    status: bool
    feedbacks: List[FeedbackSchema]
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "1",
                "cooperativa_id": "1",
                "motorista_id": "1",
                "residencias_incluidas": ["residencia1", "residencia2"],
                "data": "2023-10-01",
                "hora_inicio": "08:00:00",
                "status": "True",
                "feedbacks": [
                    {
                        "residencia_id": "residencia1",
                        "coletado": True
                    },
                    {
                        "residencia_id": "residencia2",
                        "coletado": False
                    }
                ]
            }
        }