from datetime import date, datetime
from http import HTTPStatus
from typing import List
from fastapi import APIRouter, Body, HTTPException
from schemas.cooperativa import Tutorial
from schemas.cidadao import FeedbackColeta
from schemas.residencia import ResidenceCreate, ResidenceResponse
from models.residencia import ResidenceModel, EnderecoModel
from firebase_config import db
import uuid
from services import gerar_mapa_com_coops, gerar_rota_no_mapa
from services.verificar_user import verificar_usuario

cidadao_router = APIRouter()

USUARIOS_COLLECTION = "usuarios"
RESIDENCIAS_COLLECTION = "residencias"
ROTAS_COLLECTION = "rotas"



@cidadao_router.post("/cadastrar_residencias/{user_id}", response_model=ResidenceResponse, status_code=HTTPStatus.CREATED)
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

@cidadao_router.get("/ver_mapa/{user_id}")
async def ver_mapa(user_id: str):
    verificar_usuario(user_id)

    residencias_ref = db.collection(USUARIOS_COLLECTION).document(user_id)\
        .collection(RESIDENCIAS_COLLECTION)

    bairros_usuario = set()
    for doc in residencias_ref.stream():
        data = doc.to_dict()
        endereco = data.get("endereco", {})
        bairro = endereco.get("bairro")
        if bairro:
            bairros_usuario.add(bairro.lower())

    if not bairros_usuario:
        raise HTTPException(status_code=404, detail="Nenhum bairro encontrado para suas residências.")

    usuarios_ref = db.collection(USUARIOS_COLLECTION)
    cooperativas_ativas = []

    for doc in usuarios_ref.stream():
        usuario = doc.to_dict()
        if usuario.get("role") == "cooperativa":
            bairros_coop = [b.lower().strip() for b in usuario.get("bairros_atendidos", [])]
            if any(b in bairros_usuario for b in bairros_coop):
                cooperativas_ativas.append(usuario)

    if not cooperativas_ativas:
        return {"message": "Nenhuma cooperativa atende sua região."}

    else:
        mapa = gerar_mapa_com_coops(cooperativas_ativas)
        return {"cooperativas": cooperativas_ativas,
                "mapa": mapa}


@cidadao_router.get("/ver_rota/{user_id}")
async def ver_rota(user_id: str):
    verificar_usuario(user_id)

    residencias_ref = db.collection(USUARIOS_COLLECTION).document(user_id)\
        .collection(RESIDENCIAS_COLLECTION)
    residencia_ids = [doc.id for doc in residencias_ref.stream()]

    if not residencia_ids:
        raise HTTPException(status_code=404, detail="Usuário não possui residências.")

    hoje = date.today().isoformat()
    rotas_ref = db.collection("rotas").where("data", "==", hoje)

    rotas_do_usuario = []
    for rota_doc in rotas_ref.stream():
        rota = rota_doc.to_dict()
        if any(res_id in rota.get("residencias", []) for res_id in residencia_ids):
            rotas_do_usuario.append(rota)

    if not rotas_do_usuario:
        return {"message": "Nenhuma residência do usuário está em rota ativa hoje."}

   
    rota_visual = gerar_rota_no_mapa(rotas_do_usuario)

    return {
        "rotas": rotas_do_usuario,
        "rota_visual": rota_visual
    }


@cidadao_router.post("/feedback/{user_id}", status_code=HTTPStatus.CREATED)
async def enviar_feedback(user_id: str, feedback: FeedbackColeta):
    verificar_usuario(user_id)

    residencias_ref = db.collection(USUARIOS_COLLECTION).document(user_id)\
        .collection(RESIDENCIAS_COLLECTION)
    residencia_ids = [doc.id for doc in residencias_ref.stream()]

    if not residencia_ids:
        raise HTTPException(status_code=404, detail="Usuário não possui residências.")

    hoje = date.today().isoformat()
    rotas_ref = db.collection(ROTAS_COLLECTION).where("data", "==", hoje)
    encontrou = False

    for rota_doc in rotas_ref.stream():
        rota = rota_doc.to_dict()
        if any(res_id in rota.get("residencias", []) for res_id in residencia_ids):
            encontrou = True
            break

    if not encontrou:
        raise HTTPException(status_code=403, detail="Nenhuma coleta registrada hoje para suas residências.")

    feedback_data = feedback.model_dump()
    feedback_data["user_id"] = user_id
    feedback_data["data"] = hoje
    db.collection("feedback_coletas").add(feedback_data)

    return {"message": "Feedback enviado com sucesso!"}


@cidadao_router.get("/tutoriais", response_model=List[Tutorial])
async def listar_tutoriais():
    tutoriais = []
    for doc in db.collection("tutoriais").stream():
        tutoriais.append(Tutorial(**doc.to_dict()))
    return tutoriais
