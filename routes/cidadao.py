from typing import List
from fastapi import APIRouter, Body, HTTPException
from schemas.cooperativa import Tutorial
from schemas.cidadao import FeedbackColeta
from schemas.residencia import ResidenceCreate, ResidenceResponse
from models.residencia import ResidenceModel, EnderecoModel
from firebase_config import db
import uuid

from services.verificar_user import verificar_usuario

cidadao_router = APIRouter()

USUARIOS_COLLECTION = "usuarios"
RESIDENCIAS_COLLECTION = "residencias"


@cidadao_router.post("/cadastrar_residencias/{user_id}", response_model=ResidenceResponse, status_code=201)
async def cadastrar_residencia(user_id: str, residencia: ResidenceCreate):
    verificar_usuario(user_id)
    residencia_id = str(uuid.uuid4())

    endereco_model = EnderecoModel(**residencia.endereco.model_dump())
    residencia_model = ResidenceModel(
        id=residencia_id,
        user_id=user_id,
        endereco=endereco_model,
        location=residencia.location,
        coletavel=False
    )

    db.collection(USUARIOS_COLLECTION).document(user_id)\
        .collection(RESIDENCIAS_COLLECTION).document(residencia_id)\
        .set(residencia_model.model_dump())

    return ResidenceResponse(
        id=residencia_id,
        endereco=residencia.endereco,
        location=residencia.location,
        coletavel=False
    )

@cidadao_router.get("/residencias/{user_id}", response_model=List[ResidenceResponse])
async def listar_residencias(user_id: str):
    verificar_usuario(user_id)
    residencias_ref = db.collection(USUARIOS_COLLECTION).document(user_id)\
        .collection(RESIDENCIAS_COLLECTION)

    residencias = []
    for doc in residencias_ref.stream():
        residencias.append(ResidenceResponse(**doc.to_dict()))
    return residencias

@cidadao_router.delete("/deletar_residencias/{user_id}/{residencia_id}", status_code=204)
async def deletar_residencia(user_id: str, residencia_id: str):
    verificar_usuario(user_id)
    residencia_ref = db.collection(USUARIOS_COLLECTION).document(user_id)\
        .collection(RESIDENCIAS_COLLECTION).document(residencia_id)

    doc = residencia_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Residência não encontrada.")

    residencia_ref.delete()
    return {"message": "Residência removida com sucesso!"}

@cidadao_router.put("/editar_residencias/{user_id}/{residencia_id}", response_model=ResidenceResponse)
async def update_residencia(user_id: str, residencia_id: str, nova_residencia: ResidenceCreate = Body(...)):
    verificar_usuario(user_id)

    residencia_ref = db.collection(USUARIOS_COLLECTION).document(user_id)\
        .collection(RESIDENCIAS_COLLECTION).document(residencia_id)

    doc = residencia_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Residência não encontrada.")

    endereco_model = EnderecoModel(**nova_residencia.endereco.model_dump())
    residencia_model = ResidenceModel(
        id=residencia_id,
        user_id=user_id,
        endereco=endereco_model,
        location=nova_residencia.location,
        coletavel=False  
    )

    residencia_ref.set(residencia_model.model_dump())

    return ResidenceResponse(
        id=residencia_id,
        endereco=nova_residencia.endereco,
        location=nova_residencia.location,
        coletavel=False
    )

@cidadao_router.patch("/residencias/{user_id}/{residencia_id}/coletar", response_model=ResidenceResponse)
async def coletar_residencia(user_id: str, residencia_id: str):
    verificar_usuario(user_id)
    residencia_ref = db.collection(USUARIOS_COLLECTION).document(user_id)\
        .collection(RESIDENCIAS_COLLECTION).document(residencia_id)

    doc = residencia_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Residência não encontrada.")

    atual = doc.to_dict().get("coletavel", False)
    residencia_ref.update({"coletavel": not atual})
    updated = residencia_ref.get().to_dict()
    return ResidenceResponse(**updated)

@cidadao_router.get("/ver_mapa")
async def ver_mapa():
    return {"message": "Aqui está o mapa com as coop."}

@cidadao_router.get("/ver_rota/{user_id}")

@cidadao_router.post("/feedback/{user_id}", status_code=201)
async def enviar_feedback(user_id: str, feedback: FeedbackColeta):
    verificar_usuario(user_id)
    #Tem que verificar se alguma residencia dele ta em rota ativa
    feedback_data = feedback.model_dump()
    feedback_data["user_id"] = user_id
    db.collection("feedback_coletas").add(feedback_data)
    return {"message": "Feedback enviado com sucesso!"}

@cidadao_router.get("/tutoriais", response_model=List[Tutorial])
async def listar_tutoriais():
    tutoriais = []
    for doc in db.collection("tutoriais").stream():
        tutoriais.append(Tutorial(**doc.to_dict()))
    return tutoriais
