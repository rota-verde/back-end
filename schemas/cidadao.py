from pydantic import BaseModel
from typing import List, Optional

class ResidenciaCreate(BaseModel):
    endereco: str
    numero: str
    bairro: str
    cidade: str
    class Config:
        json_schema_extra = {
            "example": {
                "endereco": "Rua Exemplo",
                "numero": "123",
                "bairro": "Centro",
                "cidade": "São Paulo"
            }
        }

class ResidenciaResponse(ResidenciaCreate):
    id: str
    coletavel: bool = False
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "1",
                "endereco": "Rua Exemplo",
                "numero": "123",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "coletavel": True
            }
        }

class FeedbackColeta(BaseModel):
    residencia_id: str
    rota_id: str
    coleta_confirmada: bool
    class Config:
        json_schema_extra = {
            "example": {
                "residencia_id": "1",
                "rota_id": "1",
                "coleta_confirmada": True
            }
        }
