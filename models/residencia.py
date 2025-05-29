from ast import Str
from typing import Dict, List, Optional
from pydantic import BaseModel

class EnderecoModel(BaseModel):
    logradouro: str
    numero: str
    bairro: str
    cidade: str

class ResidenceModel(BaseModel):
    id: Optional[str] = None
    user_id: str  
    endereco: EnderecoModel
    location: Dict[str, float]  # {"lat": ..., "lng": ...} -> botao do maps acessar sua loc
    coletavel: bool = False
    
