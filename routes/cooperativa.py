from http import HTTPStatus
from typing import List
from fastapi import APIRouter, HTTPException, Request
from firebase_config import db
from models.residencia import EnderecoModel
from models.rota import RotaModel
from schemas.cooperativa import RotaUpdate
from schemas.motorista import MotoristaCreate, MotoristaResponse
from schemas.rota import RouteCreate, RouteResponse
from datetime import date
import uuid
from services.verificar_user import verificar_usuario


coop_router = APIRouter()

MOTORISTAS_COLLECTION = "motoristas"
ROTAS_COLLECTION = "rotas"

@coop_router.put("/cadastrar_bairros/{user_id}", response_model= EnderecoModel, status_code=201)
async def atualizar_bairros_atendidos(coop_id: str, endereco: EnderecoModel):
    user_ref = db.collection("usuarios").document(coop_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    user_data = user_doc.to_dict()
    if user_data.get("role") != "cooperativa":
        raise HTTPException(status_code=403, detail="Usuário não é uma cooperativa.")

    if not endereco.bairros_atendidos:
        raise HTTPException(status_code=400, detail="Campo 'bairros_atendidos' está vazio.")

    user_ref.update({
        "endereco.bairros_atendidos": endereco.bairros_atendidos
    })

    return {
        "message": "Bairros atendidos atualizados com sucesso.",
        "bairros_atendidos": endereco.bairros_atendidos
    }


    
@coop_router.post("/cadastrar_motoristas/{user_id}", response_model=MotoristaResponse, status_code=201)
async def cadastrar_motoristas(motorista: MotoristaCreate, request: Request, coop_id : str):
    verificar_usuario(coop_id)

    motorista_id = str(uuid.uuid4())
    motorista_data = motorista.model_dump()
    motorista_data.update({
        "id": motorista_id,
        "rotas": [],
        "coop_id": coop_id
    })

    db.collection(MOTORISTAS_COLLECTION).document(motorista_id).set(motorista_data)
    return MotoristaResponse(**motorista_data)


@coop_router.get("/motoristas/{user_id}", response_model=List[MotoristaResponse])
async def listar_motoristas(request: Request, coop_id: str):
    verificar_usuario(coop_id)

    motoristas = []
    query = db.collection(MOTORISTAS_COLLECTION).where("coop_id", "==", coop_id)
    for doc in query.stream():
        motoristas.append(MotoristaResponse(**doc.to_dict()))
    return motoristas


@coop_router.get("/motoristas/{motorista_id}", response_model=MotoristaResponse)
async def listar_motorista(motorista_id: str, request: Request, user_id : str):
    user_id = user_id
    verificar_usuario(user_id)

    doc = db.collection(MOTORISTAS_COLLECTION).document(motorista_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Motorista não encontrado.")
    motorista_data = doc.to_dict()
    if motorista_data.get("coop_id") != user_id:
        raise HTTPException(status_code=403, detail="Acesso negado.")
    return MotoristaResponse(**motorista_data)

#Falta deletar e editar motorista mas deixa p depois

from datetime import datetime, timedelta

@coop_router.post("/criar_rota/{coop_id}", response_model=RouteResponse, status_code=HTTPStatus.CREATED)
async def criar_rota(rota: RouteCreate, coop_id: str):
    verificar_usuario(coop_id)  

    now = datetime.now()
    uma_hora_atras = now - timedelta(hours=1)
    rota_id = str(uuid.uuid4())

    coop_doc = db.collection("usuarios").document(coop_id).get()
    if not coop_doc.exists or coop_doc.to_dict().get("role") != "cooperativa":
        raise HTTPException(status_code=404, detail="Cooperativa não encontrada.")

    coop_data = coop_doc.to_dict()
    endereco_data = coop_data.get("endereco", {})
    bairros_atendidos = endereco_data.get("area_atuacao", [])

    if rota.bairro not in bairros_atendidos:
        raise HTTPException(status_code=400, detail="Bairro não atendido pela cooperativa.")

    pontos_fixos = [
        {"latitude": -9.649848, "longitude": -35.708949},
        {"latitude": -9.660184, "longitude": -35.735163}
    ]

    residencias = []
    usuarios_ref = db.collection("usuarios").stream()

    for usuario in usuarios_ref:
        user_id = usuario.id
        residencias_ref = db.collection("usuarios").document(user_id).collection("residencias") \
            .where("coletavel", "==", True) \
            .where("endereco.bairro", "==", rota.bairro) \
            .stream()

        for r in residencias_ref:
            r_data = r.to_dict()
            location = r_data.get("location")
            if location and "latitude" in location and "longitude" in location:
                residencias.append({
                    "id": r.id,
                    "location": {
                        "latitude": location["latitude"],
                        "longitude": location["longitude"]
                    }
                })

    pontos = {f"fixo_{i}": p for i, p in enumerate(pontos_fixos)}
    for residencia in residencias:
        pontos[residencia["id"]] = residencia["location"]

    residencias_ids = [r["id"] for r in residencias]

    rota_data = {
        "id": rota_id,
        "cooperativa_id": coop_id,
        "motorista_id": rota.motorista_id,
        "residencias_incluidas_ids": residencias_ids,
        "bairro": rota.bairro,
        "data": rota.data.isoformat(),
        "hora_inicio": rota.hora_inicio.isoformat(),
        "status": True,
        "pontos": pontos,
    }

    db.collection("rotas").document(rota_id).set(rota_data)
    return RouteResponse(**rota_data)



@coop_router.get("/rotas", response_model=List[RouteResponse])
async def listar_rotas(request: Request):
    user_id = request.headers.get("Authorization")
    verificar_usuario(user_id)

    rotas = []
    query = db.collection(ROTAS_COLLECTION).where("cooperativa_id", "==", user_id)
    async for doc in query.stream():
        rotas.append(RouteResponse(**doc.to_dict()))
    return rotas


@coop_router.get("/rotas/{rota_id}", response_model=RouteResponse)
async def listar_rota(rota_id: str, request: Request):
    user_id = request.headers.get("Authorization")
    verificar_usuario(user_id)

    rota_ref = db.collection(ROTAS_COLLECTION).document(rota_id)
    doc = await rota_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Rota não encontrada.")
    rota_data = doc.to_dict()
    if rota_data.get("cooperativa_id") != user_id:
        raise HTTPException(status_code=403, detail="Acesso negado.")
    return RouteResponse(**rota_data)


@coop_router.patch("/rotas/{rota_id}", response_model=RouteResponse)
async def editar_rotas(rota_id: str, rota: RotaUpdate, request: Request):
    user_id = request.headers.get("Authorization")
    verificar_usuario(user_id)

    rota_ref = db.collection(ROTAS_COLLECTION).document(rota_id)
    doc = await rota_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Rota não encontrada.")
    rota_data = doc.to_dict()
    if rota_data.get("cooperativa_id") != user_id:
        raise HTTPException(status_code=403, detail="Acesso negado.")

    rota_update_data = rota.model_dump(exclude_unset=True)
    await rota_ref.update(rota_update_data)
    updated_doc = await rota_ref.get()
    return RouteResponse(**updated_doc.to_dict())


@coop_router.delete("/rotas/{rota_id}", status_code=204)
async def deletar_rotas(rota_id: str, request: Request):
    user_id = request.headers.get("Authorization")
    verificar_usuario(user_id)

    rota_ref = db.collection(ROTAS_COLLECTION).document(rota_id)
    doc = await rota_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Rota não encontrada.")
    rota_data = doc.to_dict()
    if rota_data.get("cooperativa_id") != user_id:
        raise HTTPException(status_code=403, detail="Acesso negado.")

    await rota_ref.delete()
    return {"message": f"Rota {rota_id} deletada com sucesso!"}


@coop_router.get("/rotas/hoje", response_model=List[RouteResponse])
async def listar_rotas_hoje(request: Request):
    user_id = request.headers.get("Authorization")
    verificar_usuario(user_id)

    hoje = date.today()
    rotas_hoje = []
    query = db.collection(ROTAS_COLLECTION).where("cooperativa_id", "==", user_id).where("data", "==", hoje)
    async for doc in query.stream():
        rotas_hoje.append(RouteResponse(**doc.to_dict()))
    return rotas_hoje


@coop_router.get("/feedbacks/{rota_id}", response_model=RouteResponse)
async def coletar_feedbacks_diario(rota_id: str,user_id: str, request: Request):

    verificar_usuario(user_id)
    

    # A lógica para coletar feedbacks será implementada depois
    pass
