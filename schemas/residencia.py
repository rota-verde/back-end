from pydantic import BaseModel
from typing import Dict

class EnderecoSchema(BaseModel):
    logradouro: str
    numero: str
    bairro: str
    cidade: str
    class Config:
        json_schema_extra = {
            "example": {
                "logradouro": "Rua Exemplo",
                "numero": "123",
                "bairro": "Centro",
                "cidade": "São Paulo"
            }
        }

class ResidenceCreate(BaseModel):
    endereco: EnderecoSchema
    location: Dict[str, float]  
    class Config:
        json_schema_extra = {
            "example": {
                "endereco": {
                    "logradouro": "Rua Exemplo",
                    "numero": "123",
                    "bairro": "Centro",
                    "cidade": "São Paulo"
                },
                "location": {
                    "latitude": -23.5505,
                    "longitude": -46.6333
                }
            }
        }

class ResidenceResponse(BaseModel):
    id: str
    endereco: EnderecoSchema
    location: Dict[str, float]
    coletavel: bool
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "1",
                "endereco": {
                    "logradouro": "Rua Exemplo",
                    "numero": "123",
                    "bairro": "Centro",
                    "cidade": "São Paulo"
                },
                "location": {
                    "latitude": -23.5505,
                    "longitude": -46.6333
                },
                "coletavel": True
            }
        }
