import uuid
import pydantic
from pydantic import BaseModel, Field
from typing import Optional

class Caminhao(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    placa: str
    capacidade: int 
    cooperativa_id: str
    cooperativa_nome: Optional[str] = None
    status: bool = Field(default=False) # False = fora de rota, True = em uso

