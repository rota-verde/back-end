from fastapi import APIRouter

from schemas.cooperativa import MotoristaCreate, RotaCreate, RotaUpdate


coop_router = APIRouter()

@coop_router.post("/cadastrar_motoristas")
async def cadastrar_motoristas(motorista: MotoristaCreate):
    """
    Cadastrar motoristas.
    """
    pass

@coop_router.get("/motoristas")
async def listar_motoristas():
    """
    Listar motoristas.
    """
    pass

@coop_router.get("/motoristas/{motorista_id}")
async def listar_motorista(motorista_id: str):
    """
    Listar motorista específico.
    """
    pass

@coop_router.get("/rotas")
async def listar_rotas():
    """
    Listar rotas.
    """
    pass

@coop_router.get("/rotas/{rota_id}")
async def listar_rota(rota_id: str):
    """
    Listar rota específica.
    """
    pass

@coop_router.post("/rotas")
async def cadastrar_rotas(rota: RotaCreate):
    """
    Cadastrar rotas.
    """
    pass

@coop_router.patch("/rotas/{rota_id}")
async def editar_rotas(rota_id: str, rota: RotaUpdate):
    """
    Editar rotas.
    """
    pass

@coop_router.delete("/rotas/{rota_id}")
async def deletar_rotas(rota_id: str):
    """
    Deletar rotas.
    """
    pass

@coop_router.get("/rotas/hoje")
async def listar_rotas_hoje():
    """
    Listar rotas do dia.
    """
    pass