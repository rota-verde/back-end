from pydantic import BaseModel
from typing import List
from datetime import date, time

class FeedbackSchema(BaseModel):
    residencia_id: str
    coletado: bool

class RouteCreate(BaseModel):
    motorista_id: str
    residencias_incluidas: List[str]
    bairro: str
    data: date
    hora_inicio: time

class RouteResponse(BaseModel):
    id: str
    cooperativa_id: str
    motorista_id: str
    residencias_incluidas: List[str]
    data: date
    hora_inicio: time
    status: str
    feedbacks: List[FeedbackSchema]
