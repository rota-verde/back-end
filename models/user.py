import uuid
from pydantic import BaseModel, model_validator
from typing import Optional
from pydantic import Field

# Base comum
class UsuarioBase(BaseModel):

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    username: str
    email: Optional[str] = None
    telefone: str
    endereco: str
    bairro : str
    tipo: str  # "cidadao" ou "cooperativa"

# Cidadão
class UsuarioCidadao(UsuarioBase):
    tipo: str = "cidadao"
    cpf: str

# Cooperativa
class UsuarioCooperativa(UsuarioBase):
    tipo: str = "cooperativa"
    cnpj: str
    nome_cooperativa: str

    @model_validator(mode="after")
    def validar_cooperativa(self):
        if self.tipo == "cooperativa":
            if not self.cnpj or not self.nome_cooperativa:
                raise ValueError("Cooperativas devem fornecer cnpj e nome_cooperativa.")
        return self

# NOVOS: Incluindo senha
class UsuarioCreateCidadao(UsuarioCidadao):
    senha: str

class UsuarioCreateCooperativa(UsuarioCooperativa):
    senha: str

# Para entrada
class UsuarioEntrar(BaseModel):
    senha: str
    email: Optional[str] = None
    telefone: str

