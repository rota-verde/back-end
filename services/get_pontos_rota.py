from fastapi import HTTPException
from routes.cooperativa import ROTAS_COLLECTION


def get_pontos_rota(rota_id: str, current_user_id: str):
    """Obter os pontos PARA CRIAR rota específica."""
    rota_ref = db.collection(ROTAS_COLLECTION).document(rota_id)
    doc =rota_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Rota não encontrada.")
    rota_data = doc.to_dict()
    if rota_data.get("cooperativa_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para acessar esta rota.")
    return rota_data.get("pontos", [])