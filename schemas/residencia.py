from pydantic import BaseModel
from typing import Dict

class EnderecoSchema(BaseModel):
    logradouro: str
    numero: str
    bairro: str
    cidade: str

class ResidenceCreate(BaseModel):
    endereco: EnderecoSchema
    location: Dict[str, float]  

class ResidenceResponse(BaseModel):
    id: str
    endereco: EnderecoSchema
    location: Dict[str, float]
    coletavel: bool
