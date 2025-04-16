from fastapi import APIRouter, HTTPException
from services.firestore import db
from models.user import UsuarioCidadao, UsuarioCooperativa, UsuarioPrefeitura

router = APIRouter()

@router.post("/cadastro/cidadao")
def cadastrar_cidadao(usuario: UsuarioCidadao):
    db.collection("usuarios").document("cidadão").collection("dados").add(usuario.dict())
    return {"mensagem": "Cidadão cadastrado com sucesso"}

@router.post("/cadastro/cooperativa")
def cadastrar_cooperativa(usuario: UsuarioCooperativa):
    db.collection("usuarios").document("cooperativa").collection("dados").add(usuario.dict())
    return {"mensagem": "Cooperativa cadastrada com sucesso"}

@router.post("/cadastro/prefeitura")
def cadastrar_prefeitura(usuario: UsuarioPrefeitura):
    db.collection("usuarios").document("prefeitura").collection("dados").add(usuario.dict())
    return {"mensagem": "Prefeitura cadastrada com sucesso"}
