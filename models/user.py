from typing import List, Optional
from pydantic import BaseModel
from schemas.user import UserBase

class UserModel(UserBase):
    uid: str
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    cnh: Optional[str] = None
    nome_cooperativa: Optional[str] = None
    cooperativa_id: Optional[str] = None
    auth_2fa_enabled: Optional[bool] = False
