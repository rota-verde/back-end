from fastapi import APIRouter, HTTPException, Depends
from services.auth import verify_token
from models import UsuarioCooperativa, UsuarioCidadao
from models.rota import RotaCreate, RotaResponse
from typing import List
import uuid
from services.firestore import db
router = APIRouter(
    prefix="/config",
    tags=["config"]
)

@router.post("/redefinir_senha")
def redefinir_senha(usuario: UsuarioCidadao | UsuarioCooperativa, nova_senha: str, token: str = Depends(verify_token)):
    user_ref = db.collection("usuarios").document("cidadao").collection("dados").document(usuario.id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    user_ref.update({"senha": nova_senha})
    
    return {"mensagem": "Senha redefinida com sucesso!"}

@router.post("/atualizar_email")
def atualizar_email(usuario: UsuarioCidadao | UsuarioCooperativa, novo_email: str, token: str = Depends(verify_token)):
    user_ref = db.collection("usuarios").document("cidadao").collection("dados").document(usuario.id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    user_ref.update({"email": novo_email})
    
    return {"mensagem": "Email atualizado com sucesso!"}

@router.post("/atualizar_telefone")
def atualizar_telefone(usuario: UsuarioCidadao | UsuarioCooperativa, novo_telefone: str, token: str = Depends(verify_token)):
    user_ref = db.collection("usuarios").document("cidadao").collection("dados").document(usuario.id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    user_ref.update({"telefone": novo_telefone})
    
    return {"mensagem": "Telefone atualizado com sucesso!"}

@router.post("/esqueci_senha")
def esqueci_senha(usuario: UsuarioCidadao | UsuarioCooperativa, token: str = Depends(verify_token)):
    user_ref = db.collection("usuarios").document("cidadao").collection("dados").document(usuario.id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    # VER COMO FAZ P MANDAR EMAIL COM NOVA SENHA
    return {"mensagem": "Instruções para redefinir a senha foram enviadas para o seu email."}
