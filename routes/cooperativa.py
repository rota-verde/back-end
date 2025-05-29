from http import HTTPStatus
from typing import List
from fastapi import APIRouter, HTTPException, Request
from firebase_config import db
from models.residencia import EnderecoModel, ResidenceModel
from models.rota import RotaModel
from schemas.cooperativa import RotaUpdate, CooperativaResponse
from schemas.motorista import MotoristaCreate, MotoristaResponse
from schemas.rota import RouteCreate, RouteResponse
from datetime import date
import uuid
from services.verificar_user import verificar_usuario


coop_router = APIRouter()

MOTORISTAS_COLLECTION = "motoristas"
ROTAS_COLLECTION = "rotas"
USUARIOS_COLLECTION = "usuarios"

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
    bairros_atendidos = coop_data.get("area_atuacao", [])

    if rota.bairro not in bairros_atendidos:
        raise HTTPException(status_code=400, detail="Bairro não atendido pela cooperativa.")


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

    pontos = []
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

@coop_router.get("/listar", response_model=List[CooperativaResponse])
async def listar_cooperativas():
    try:
        cooperativas = []
        # Query all users with role "cooperativa"
        query = db.collection(USUARIOS_COLLECTION).where("role", "==", "cooperativa")

        for doc in query.stream():
            data = doc.to_dict()
            # Only include required fields
            cooperativa = {
                "id": doc.id,
                "nome_usuario": data.get("nome_usuario", ""),
                "nome_cooperativa": data.get("nome_cooperativa", ""),
                "area_atuacao": data.get("area_atuacao", []),
                "location": data.get("location", {"latitude": 0, "longitude": 0}),
                "endereco": data.get("endereco", {}),
                "materiais_reciclaveis": data.get("materiais_reciclaveis", [])
            }
            cooperativas.append(cooperativa)

        return cooperativas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar cooperativas: {str(e)}")

#fetch a specific cooperativa by coop_id
@coop_router.get("/cooperativa/{coop_id}", response_model=CooperativaResponse)
async def listar_cooperativa(coop_id: str, request: Request):
    verificar_usuario(coop_id)

    coop_ref = db.collection(USUARIOS_COLLECTION).document(coop_id)
    coop_doc = coop_ref.get()

    if not coop_doc.exists:
        raise HTTPException(status_code=404, detail="Cooperativa não encontrada.")

    coop_data = coop_doc.to_dict()

    if coop_data.get("role") != "cooperativa":
        raise HTTPException(status_code=403, detail="Acesso negado. O ID fornecido não corresponde a uma cooperativa.")


    try:
        cooperativa_formatada = {
            "id": coop_doc.id,
            "nome_usuario": coop_data.get("nome_usuario", ""),
            "nome_cooperativa": coop_data.get("nome_cooperativa", ""),
            "area_atuacao": coop_data.get("area_atuacao", []),
            "location": coop_data.get("location", {"latitude": 0.0, "longitude": 0.0}),
            "endereco": coop_data.get("endereco", {}),
            "materiais_reciclaveis": coop_data.get("materiais_reciclaveis", [])
        }

        return CooperativaResponse(**cooperativa_formatada)

    except Exception as e:
        print(f"Erro ao formatar dados da cooperativa {coop_id}: {e}")
        print(f"Dados brutos que causaram o erro: {coop_data}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar dados da cooperativa: {str(e)}")


#fetch tds as residencias que estao na mesma area de atuacao/bairro que uma determinada coop
@coop_router.get("/residencias/{coop_id}", response_model=List[ResidenceModel])
async def listar_residencias_coop(coop_id: str, request: Request):
    verificar_usuario(coop_id)

    coop_ref = db.collection(USUARIOS_COLLECTION).document(coop_id)
    coop_doc = coop_ref.get()
    if not coop_doc.exists:
        raise HTTPException(status_code=404, detail="Cooperativa não encontrada.")

    coop_data = coop_doc.to_dict()
    area_atuacao = coop_data.get("area_atuacao", [])

    if not area_atuacao:
        raise HTTPException(status_code=404, detail="Nenhuma area encontrado.")

    residencias = []
    usuarios_ref = db.collection("usuarios").stream()

    for usuario in usuarios_ref:
        user_id = usuario.id
        residencias_ref = db.collection("usuarios").document(user_id).collection("residencias") \
            .where("endereco.bairro", "in", area_atuacao) \
            .stream()

        for r in residencias_ref:
            r_data = r.to_dict()
            residencias.append(EnderecoModel(**r_data.get("endereco", {})))

    return residencias

#fetch materias reciclaveis de uma cooperativa
@coop_router.get("/materiais_reciclaveis/{coop_id}", response_model=List[str])
async def listar_materiais_reciclaveis(coop_id: str, request: Request):
    verificar_usuario(coop_id)

    coop_ref = db.collection(USUARIOS_COLLECTION).document(coop_id)
    coop_doc = coop_ref.get()
    if not coop_doc.exists:
        raise HTTPException(status_code=404, detail="Cooperativa não encontrada.")

    coop_data = coop_doc.to_dict()
    materiais_reciclaveis = coop_data.get("materiais_reciclaveis", [])

    if not materiais_reciclaveis:
        raise HTTPException(status_code=404, detail="Nenhum material reciclável encontrado.")

    return materiais_reciclaveis

