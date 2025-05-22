from datetime import date, datetime
from http import HTTPStatus
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from firebase_config import db
from schemas.motorista import IniciarColetaRequest, FinalizarColetaRequest
from schemas.rota import RouteResponse, FeedbackSchema
from services import acompanhar_rota, verificar_user

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

@motorista_router.get(
    "/rota/atual",
    response_model=RouteResponse,
    status_code=HTTPStatus.OK,
    summary="Retorna a rota atualmente iniciada para o motorista"
)
async def obter_rota_atual(
    current_user_id: str 
):
    """
    Busca a rota com `status=True` que pertence ao motorista logado e
    retorna o resultado da função `rota()`.
    """
    verificar_user(current_user_id)
    query = (
        db.collection(ROTAS_COLLECTION)
          .where("motorista_id", "==", current_user_id)
          .where("status", "==", True)
          .limit(1)
    )
    docs = list(query.stream())
    if not docs:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma rota iniciada encontrada para este motorista."
        )

    rota_doc = docs[0]
    rota_data = rota_doc.to_dict()
    rota_data["id"] = rota_doc.id  

   
    direcionamento_rota = acompanhar_rota(rota_data)

    return {
        **rota_data,
        **direcionamento_rota
    }

#Falta verificar se o motorista tem acessoa essa rota p fazer isso ne
@motorista_router.post("/iniciar_rota/{rota_id}", status_code=HTTPStatus.CREATED)
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

@motorista_router.post("/finalizar_rota/{rota_id}", status_code=HTTPStatus.CREATED)
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
