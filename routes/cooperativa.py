from typing import List
from fastapi import APIRouter, Depends, HTTPException
from firebase_config import db
from models.rota import RotaModel
from schemas.cooperativa import RotaUpdate
import uuid
from schemas.motorista import MotoristaCreate, MotoristaResponse
from schemas.rota import RouteCreate, RouteResponse
from datetime import date
from services.auth_service import get_current_user_id

coop_router = APIRouter()

COOPERATIVAS_COLLECTION = "cooperativas"
MOTORISTAS_COLLECTION = "motoristas"
ROTAS_COLLECTION = "rotas"


@coop_router.post("/cadastrar_motoristas", response_model=MotoristaResponse, status_code=201)
async def cadastrar_motoristas(motorista: MotoristaCreate, coop_id : str):
    """Cadastrar motoristas para a cooperativa."""
    motorista_id = str(uuid.uuid4())
    motorista_data = motorista.model_dump()
    motorista_data["id"] = motorista_id
    motorista_data["rotas"] = []  
    motorista_data["coop_id"] = coop_id

    db.collection(MOTORISTAS_COLLECTION).document(motorista_id).set(motorista_data)
    return MotoristaResponse(**motorista_data)

@coop_router.get("/motoristas", response_model=List[MotoristaResponse])
async def listar_motoristas(coop_id: str ):
    """Listar motoristas da cooperativa."""
    motoristas = []
    query = db.collection(MOTORISTAS_COLLECTION).where("coop_id", "==", coop_id)
    for doc in query.stream():
        motoristas.append(MotoristaResponse(**doc.to_dict()))
    return motoristas

@coop_router.get("/motoristas/{coop_id}/{motorista_id}", response_model=MotoristaResponse)
async def listar_motorista(motorista_id: str, coop_id: str):
    """Listar motorista específico da cooperativa."""
    motorista_ref = db.collection(MOTORISTAS_COLLECTION).document(motorista_id)
    doc = motorista_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Motorista não encontrado.")
    motorista_data = doc.to_dict()
    if motorista_data.get("coop_id") != coop_id:
        print (motorista_data.get("coop_id"))
        print (coop_id)
        
        raise HTTPException(status_code=403, detail="Você não tem permissão para acessar este motorista.")
    return MotoristaResponse(**motorista_data)

@coop_router.post("/criar_rotas", response_model=RouteResponse, status_code=201)
async def cadastrar_rotas(rota: RouteCreate, current_user_id: str):
    """Cadastrar rotas para a cooperativa."""
    rota_id = str(uuid.uuid4())
    rota_data = rota.model_dump()
    rota_data["cooperativa_id"] = current_user_id
    rota_data["id"] = rota_id
    rota_data["feedbacks"] = 0  
    rota_data["data"] = date.today()
    rota_data["motoristas"] = []
    rota_data["residencias"] = []
    await db.collection(ROTAS_COLLECTION).document(rota_id).set(rota_data)
    return RouteResponse(**rota_data)

@coop_router.get("/rotas", response_model=List[RouteResponse])
async def listar_rotas(current_user_id: str = Depends(get_current_user_id)):
    """Listar rotas da cooperativa."""
    rotas = []
    query = db.collection(ROTAS_COLLECTION).where("cooperativa_id", "==", current_user_id)
    async for doc in query.stream():
        rotas.append(RouteResponse(**doc.to_dict()))
    return rotas

@coop_router.get("/rotas/{rota_id}", response_model=RouteResponse)
async def listar_rota(rota_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Listar rota específica da cooperativa."""
    rota_ref = db.collection(ROTAS_COLLECTION).document(rota_id)
    doc = await rota_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Rota não encontrada.")
    rota_data = doc.to_dict()
    if rota_data.get("cooperativa_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para acessar esta rota.")
    return RouteResponse(**rota_data)

@coop_router.patch("/rotas/{rota_id}", response_model=RouteResponse)
async def editar_rotas(rota_id: str, rota: RotaUpdate, current_user_id: str = Depends(get_current_user_id)):
    """Editar rota específica da cooperativa."""
    rota_ref = db.collection(ROTAS_COLLECTION).document(rota_id)
    doc = await rota_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Rota não encontrada.")
    rota_data = doc.to_dict()
    if rota_data.get("cooperativa_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para editar esta rota.")

    rota_update_data = rota.model_dump(exclude_unset=True)
    await rota_ref.update(rota_update_data)
    updated_doc = await rota_ref.get()
    return RouteResponse(**updated_doc.to_dict())

@coop_router.delete("/rotas/{rota_id}", status_code=204)
async def deletar_rotas(rota_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Deletar rota específica da cooperativa."""
    rota_ref = db.collection(ROTAS_COLLECTION).document(rota_id)
    doc = await rota_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Rota não encontrada.")
    rota_data = doc.to_dict()
    if rota_data.get("cooperativa_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para deletar esta rota.")

    await rota_ref.delete()
    return {"message": f"Rota {rota_id} deletada com sucesso!"}

@coop_router.get("/rotas/hoje", response_model=List[RouteResponse])
async def listar_rotas_hoje(current_user_id: str = Depends(get_current_user_id)):
    """Listar rotas do dia da cooperativa."""
    hoje = date.today()
    rotas_hoje = []
    query = db.collection(ROTAS_COLLECTION).where("cooperativa_id", "==", current_user_id).where("data", "==", hoje)
    async for doc in query.stream():
        rotas_hoje.append(RouteResponse(**doc.to_dict()))
    return rotas_hoje

@coop_router.get("/feedbacks/{rota_id}", response_model= RouteResponse)
async def coletar_feedbacks_diario(user_id: str, rota : RotaModel):
    #Coletar todos os feedbacks do dia que estao na coleção feedbacks_coleta com o id da rota e dentro tds os feedbacks de tds as residencias

    pass