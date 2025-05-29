from typing import List, Optional
from pydantic import BaseModel


class UserModel(BaseModel):
    uid: str
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    cnh: Optional[str] = None
    nome_usuario: Optional[str] = None
    nome_cooperativa: Optional[str] = None
    area_atuacao: Optional[List[str]] = None
    materiais_reciclaveis: Optional[List[str]] = None
    cooperativa_id: Optional[str] = None
    auth_2fa_enabled: Optional[bool] = False
