from pydantic import BaseModel, root_validator, validator
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
    

class UsuarioCooperativa(UsuarioBase):
    tipo: str = "cooperativa" 
    cnpj: str
    nome_cooperativa: str

    @root_validator
    def validar_cooperativa(cls, values):
        cnpj = values.get("cnpj")
        nome_cooperativa = values.get("nome_cooperativa")

        if not cnpj or not nome_cooperativa:
            raise ValueError("Cooperativas devem fornecer cnpj e nome_cooperativa.")
        return values

class UsuarioCreate(BaseModel):
    senha: str

class UsuarioEntrar(BaseModel):
    senha: str
    email: Optional[str] = None  # Entrada com email é opcional
    telefone: str  # Mas telefone é obrigatório
