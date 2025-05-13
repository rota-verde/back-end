from typing import List, Dict
from fastapi import APIRouter, Body, Depends, HTTPException
from schemas.cooperativa import Tutorial
from services.auth_service import get_current_user_id
from firebase_config import db
from schemas.cidadao import FeedbackColeta
from schemas.residencia import ResidenceCreate, ResidenceResponse, EnderecoSchema
from models.residencia import ResidenceModel
import uuid
from models.residencia import EnderecoModel
from models.residencia import ResidenceModel
cidadao_router = APIRouter()

USUARIOS_COLLECTION = "usuarios"
RESIDENCIAS_COLLECTION = "residencias"

@cidadao_router.post("/cadastrar_residencias/{user_id}", response_model=ResidenceResponse, status_code=201)
async def cadastrar_residencia(user_id: str, residencia: ResidenceCreate):
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
        .collection(RESIDENCIAS_COLLECTION).document(residencia_id).set(residencia_model.model_dump())
    return ResidenceResponse(id=residencia_id, endereco=residencia.endereco, location=residencia.location, coletavel=False)


@cidadao_router.get("/residencias/{user_id}", response_model=List[ResidenceResponse])
async def listar_residencias(user_id: str ):
    residencias_ref = db.collection(USUARIOS_COLLECTION).document(user_id)\
        .collection(RESIDENCIAS_COLLECTION)
    residencias = []
    for doc in residencias_ref.stream():
        residencia_data = doc.to_dict()
        residencias.append(ResidenceResponse(**residencia_data))
    return residencias

@cidadao_router.delete("/deletar_residencias/{residencia_id}/{user_id}", status_code=204)
async def deletar_residencia(residencia_id: str, user_id: str ):
    residencia_ref = db.collection(USUARIOS_COLLECTION).document(user_id)\
        .collection(RESIDENCIAS_COLLECTION).document(residencia_id)
    doc = residencia_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Residência não encontrada.")
    else:
        residencia_ref.delete()
    return {"message": "Residência removida com sucesso!"}

@cidadao_router.patch("/residencias/{residencia_id}/coletar", response_model=ResidenceResponse)
async def coletar_residencia(residencia_id: str, user_id: str ):
    residencia_ref = db.collection(USUARIOS_COLLECTION).document(user_id)\
        .collection(RESIDENCIAS_COLLECTION).document(residencia_id)
    doc = residencia_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Residência não encontrada.")

    residencia_ref.update({"coletavel": True})
    updated_doc = residencia_ref.get()
    return ResidenceResponse(**updated_doc.to_dict())

@cidadao_router.patch("/residencias/{residencia_id}/nao_coletar", response_model=ResidenceResponse)
def nao_coletar_residencia(residencia_id: str, user_id: str ):
    residencia_ref = db.collection(USUARIOS_COLLECTION).document(user_id)\
        .collection(RESIDENCIAS_COLLECTION).document(residencia_id)
    doc = residencia_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Residência não encontrada.")

    residencia_ref.update({"coletavel": False})
    updated_doc = residencia_ref.get()
    return ResidenceResponse(**updated_doc.to_dict())

@cidadao_router.get("/ver_mapa")
async def ver_mapa():
    # Lógica para retornar o mapa com as cooperativas proximas 
    # Aqui você pode integrar com uma API de mapas
    return {"message": "Aqui está o mapa com as residências coletáveis."}

# @cidadao_router.post("/feedback", status_code=201)
# async def enviar_feedback(feedback: FeedbackColeta, current_user_id: str = Depends(get_current_user_id)):
#     # Lógica para salvar o feedback do cidadão
#     feedback_data = feedback.model_dump()
#     feedback_data["user_id"] = current_user_id
#     await db.collection("feedback_coletas").add(feedback_data)
#     return {"message": "Feedback enviado com sucesso!"}

@cidadao_router.get("/tutoriais", response_model=List[Tutorial])
async def listar_tutoriais(current_user_id: str = Depends(get_current_user_id)):
    tutoriais = []
    async for doc in db.collection("tutoriais").stream():
        tutoriais.append(Tutorial(**doc.to_dict()))
    return tutoriais

