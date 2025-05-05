motorista_router = APIRouter()
from fastapi import APIRouter, Depends, HTTPException

@motorista_router.post("/iniciar_coleta")
async def iniciar_coleta():
    """
    Iniciar coleta de resíduos.
    """
    pass

@motorista_router.post("/finalizar_coleta")
async def finalizar_coleta():
    """
    Finalizar coleta de resíduos.
    """
    pass

@motorista_router.get("/rotas/hoje")
async def listar_rotas_hoje():
    """
    Listar rotas do dia.
    """
    pass

@motorista_router.get("/rotas/mapa")
async def listar_mapa():
    """
    Listar mapa das rotas.
    """
    passS