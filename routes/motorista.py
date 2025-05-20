from datetime import date, datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from firebase_config import db
from schemas.motorista import IniciarColetaRequest, FinalizarColetaRequest
from schemas.rota import RouteResponse, FeedbackSchema

motorista_router = APIRouter()

ROTAS_COLLECTION = "rotas"

@motorista_router.get("/rotas/hoje", response_model=List[RouteResponse])
async def listar_rotas_hoje_motorista(current_user_id: str):
    """Listar as rotas do motorista para o dia de hoje."""
    hoje = date.today()
    rotas = []
    query = db.collection(ROTAS_COLLECTION).where("motorista_id", "==", current_user_id).where("data", "==", hoje)
    for doc in query.stream():
        rotas.append(RouteResponse(**doc.to_dict()))
    return rotas

#Acessar a rota e acompanha-la if status = true = apertou p inicar


#Falta verificar se o motorista tem acessoa essa rota p fazer isso ne
@motorista_router.post("/iniciar_rota/{rota_id}")
async def iniciar_rota(rota_id: str):
    rota_ref = db.collection(ROTAS_COLLECTION).document(rota_id)
    rota_doc = rota_ref.get()

    if not rota_doc.exists:
        raise HTTPException(status_code=404, detail="Rota não encontrada.")

    rota_ref.update({
        "inicio": datetime.now().isoformat(),
        "status": True
    })

    return {"message": "Rota iniciada com sucesso."}

@motorista_router.post("/finalizar_rota/{rota_id}")
async def finalizar_rota(rota_id: str):
    rota_ref = db.collection(ROTAS_COLLECTION).document(rota_id)
    rota_doc = rota_ref.get()

    if not rota_doc.exists:
        raise HTTPException(status_code=404, detail="Rota não encontrada.")

    rota_ref.update({
        "fim": datetime.now().isoformat(),
        "status": False
    })

    return {"message": "Rota finalizada com sucesso."}
