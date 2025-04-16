from pydantic import BaseModel
from typing import Optional

class UsuarioBase(BaseModel):
    id: str
    nome: str
    email: str
    telefone: str
    senha: str
    endereco : str

class UsuarioCidadao(UsuarioBase):
    tipo: str = "cidadão"

class UsuarioCooperativa(UsuarioBase):
    cooperativa_id: str
    tipo: str = "cooperativa"
    cnpj: str
    nome_cooperativa: str

class UsuarioCatador(UsuarioBase):
    autonomo: bool
    cooperativa_id: Optional[int] = None  
    tipo: str = "catador"




