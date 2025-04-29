import uuid
from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional
from pydantic import Field

# Base comum
class UsuarioBase(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    username: str
    email: Optional[str] = None
    telefone: str
    endereco: List[str] = []
    bairro: str
    tipo: str  # "cidadao" ou "cooperativa"

    @field_validator("telefone")
    def validar_telefone(cls, telefone):
        if not telefone:
            raise ValueError("Telefone é obrigatório.")
        if len(telefone) < 10:
            raise ValueError("Telefone deve ter pelo menos 10 dígitos.")
        return telefone

    @field_validator("endereco")
    def validar_endereco(cls, endereco):
        if not endereco:
            raise ValueError("Endereço é obrigatório.")
        if len(endereco) < 5:
            raise ValueError("Endereço deve ter pelo menos 5 caracteres.")
        return endereco

# Cidadão
class UsuarioCidadao(UsuarioBase):
    tipo: str = "cidadao"
    cpf: str
    @model_validator(mode="after")
    def validar_cidadao(self):
        if self.tipo == "cidadao":
            if not self.cpf:
                raise ValueError("Cidadãos devem fornecer CPF.")
        return self

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

