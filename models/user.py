from typing import List, Optional
from pydantic import BaseModel

class UserModel(BaseModel):
    uid: str  
    role: str  # "cidadao", "cooperativa" ou "motorista"
    nome_usuario: str
    nome_cooperativa: Optional[str] = None  # apenas para cooperativa
    cpf: Optional[str] = None
    cnh: Optional[str] = None
    cnpj: Optional[str] = None
    email: Optional[str] = None
    telefone: str
    residencias: Optional[List[str]] = []  # apenas para cidadão
    cooperativa_id: Optional[str] = None  # se for motorista
    auth_2fa_enabled: Optional[bool] = False
