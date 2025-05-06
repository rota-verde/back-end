from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from firestore import db, get_current_user_id
from schemas.motorista import IniciarColetaRequest, FinalizarColetaRequest
from schemas.rota import RouteResponse, FeedbackSchema

motorista_router = APIRouter()

ROTAS_COLLECTION = "rotas"

@motorista_router.get("/rotas/hoje", response_model=List[RouteResponse])
async def listar_rotas_hoje_motorista(current_user_id: str = Depends(get_current_user_id)):
    """Listar as rotas do motorista para o dia de hoje."""
    hoje = date.today()
    rotas = []
    query = db.collection(ROTAS_COLLECTION).where("motorista_id", "==", current_user_id).where("data", "==", hoje)
    async for doc in query.stream():
        rotas.append(RouteResponse(**doc.to_dict()))
    return rotas

@motorista_router.post("/rotas/{rota_id}/iniciar_coleta")
async def iniciar_coleta_motorista(rota_id: str, payload: IniciarColetaRequest, current_user_id: str = Depends(get_current_user_id)): ...
    # ... (lógica semelhante à rota da cooperativa, mas verificando se o current_user_id é o motorista da rota)

@motorista_router.post("/rotas/{rota_id}/finalizar_coleta")
async def finalizar_coleta_motorista(rota_id: str, payload: FinalizarColetaRequest, current_user_id: str = Depends(get_current_user_id)): ...
    # ... (lógica semelhante à rota da cooperativa, com verificação de permissão)

@motorista_router.post("/rotas/{rota_id}/feedback")
async def enviar_feedback_coleta_motorista(rota_id: str, feedback: List[FeedbackSchema], current_user_id: str = Depends(get_current_user_id)): ...
    # ... (lógica para o motorista enviar feedback sobre a coleta)