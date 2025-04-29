from fastapi import APIRouter, HTTPException, Depends
from models import user
from models.rota import RotaCreate, RotaResponse
from models.user import UsuarioCooperativa
from services.firestore import db
from typing import List
import uuid

router = APIRouter(
    prefix="/rotas",
    tags=["rotas"]
)

@router.post("/criar_rota", response_model=RotaResponse)
def criar_rota(rota: RotaCreate, user=UsuarioCooperativa):
    if user.get("tipo") != "cooperativa":
        raise HTTPException(status_code=403, detail="Apenas cooperativas podem criar rotas.")
    if not user.get("id"):
        raise HTTPException(status_code=403, detail="Usuário não autenticado.")
    rota_id = str(uuid.uuid4())
    rota_dict = rota.dict()
    rota_dict["id"] = rota_id
    db.collection("rotas").document(rota_id).set(rota_dict)
    return rota_dict


@router.get("/list_rotas", response_model=List[RotaResponse])
def listar_rotas():
    rotas_ref = db.collection("rotas").stream()
    return [r.to_dict() for r in rotas_ref]


@router.get("/{rota_id}", response_model=RotaResponse)
def obter_rota(rota_id: str):
    doc = db.collection("rotas").document(rota_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Rota não encontrada")
    return doc.to_dict()


@router.patch("/{rota_id}/finalizar")
def finalizar_rota(rota_id: str, relatorio: str, user=UsuarioCooperativa):
    if user.get("tipo") != "cooperativa":
        raise HTTPException(status_code=403, detail="Apenas cooperativas podem finalizar rotas.")
    if not user.get("id"):
        raise HTTPException(status_code=403, detail="Usuário não autenticado.")
    doc_ref = db.collection("rotas").document(rota_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Rota não encontrada")

    doc_ref.update({
        "status": "finalizada",
        "relatorio_final": relatorio
    })
    return {"mensagem": "Rota finalizada com sucesso"}


@router.patch("/{rota_id}/feedback")
def adicionar_feedback(rota_id: str, feedback: str, user=UsuarioCooperativa):
    if user.get("tipo") != "cooperativa":
        raise HTTPException(status_code=403, detail="Apenas cooperativas podem adicionar feedbacks.")
    if not user.get("id"):
        raise HTTPException(status_code=403, detail="Usuário não autenticado.")
    doc_ref = db.collection("rotas").document(rota_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Rota não encontrada")

    rota_data = doc.to_dict()
    feedbacks = rota_data.get("feedbacks", [])
    feedbacks.append(feedback)
    doc_ref.update({"feedbacks": feedbacks})
    return {"mensagem": "Feedback adicionado com sucesso"}
