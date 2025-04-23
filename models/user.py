from pydantic import BaseModel
from typing import Optional

class UsuarioBase(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    telefone: str
    endereco: str
    tipo: str  # "cidadao" ou "cooperativa"

class UsuarioCidadao(UsuarioBase):
    tipo: str = "cidadao"  
    cpf: str
    

from pydantic import BaseModel, field_validator, model_validator

class UsuarioCooperativa(UsuarioBase):
    cnpj: Optional[str]
    nome_cooperativa: Optional[str]

    @model_validator(mode="after")
    def validar_cooperativa(self):
        if self.tipo == "cooperativa":
            if not self.cnpj or not self.nome_cooperativa:
                raise ValueError("Cooperativas devem fornecer cnpj e nome_cooperativa.")
        return self


class UsuarioCreate(BaseModel):
    senha: str

class UsuarioEntrar(BaseModel):
    senha: str
    email: Optional[str] = None  # Entrada com email é opcional
    telefone: str  # Mas telefone é obrigatório
