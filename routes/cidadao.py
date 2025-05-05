from typing import List, Literal, Optional, Union
import uuid
from fastapi import APIRouter, Body, Depends, HTTPException
from firestore import db
from schemas.residencia import ResidenceCreate



cidadao_router = APIRouter()

@cidadao_router.post("/cadastrar_residencias")
async def cadastrar_residencias(residencia: ResidenceCreate):
    user_id = str(payload["id"])
    novo_endereco = payload["endereco"]

    doc_ref = db.collection("usuarios").document("cidadao")\
        .collection("dados").document(user_id)

    doc = doc_ref.get()
    if doc.exists:
        dados = doc.to_dict()
        enderecos = dados.get("enderecos", [])
        if novo_endereco in enderecos:
            raise HTTPException(status_code=400, detail="Endereço já cadastrado.")
        enderecos.append(novo_endereco)
    else:
        enderecos = [novo_endereco]

    doc_ref.set({"enderecos": enderecos}, merge=True)
    return {"message": "Endereço adicionado com sucesso!"}

@cidadao_router.get("/residencias")
async def listar_residencias():
    id = str(id)
    doc_ref = db.collection("usuarios").document("cidadao").collection("dados").document(id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    dados = doc.to_dict()
    enderecos = dados.get("enderecos", [])

    return {"enderecos": enderecos}

@cidadao_router.patch("/residencias/{residencia_id}/coletar")
async def coletar_residencias(residencia_id: str):
    """
    Atualizar status de coleta de uma residência.
    """
    pass

@cidadao_router.get("/rotas/hoje/feedback")
async def listar_feedback():
    """
    Listar feedbacks do dia.
    """
    pass

@cidadao_router.get("/rotas/hoje")
async def listar_rotas_hoje():
    """
    Listar rotas do dia.
    """
    pass

@cidadao_router.get("/rotas/hoje/{rota_id}")
async def listar_rota(rota_id: str):
    """
    Listar rota específica do dia.
    """
    pass

@cidadao_router.get("/tutoriais")
async def listar_tutoriais():
    """
    Listar tutoriais.
    """
    pass

