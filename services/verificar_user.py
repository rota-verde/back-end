from fastapi import  HTTPException
from firebase_config import db

USUARIOS_COLLECTION = "usuarios"
RESIDENCIAS_COLLECTION = "residencias"

def verificar_usuario(uid: str):
    doc_ref = db.collection(USUARIOS_COLLECTION).document(uid)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")