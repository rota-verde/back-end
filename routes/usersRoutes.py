from typing import Literal, Union
from fastapi import APIRouter, Body, Depends, HTTPException
from services.auth import verify_token
from services.firestore import db
from models.user import UsuarioCidadao, UsuarioCooperativa,  UsuarioCreateCidadao, UsuarioCreateCooperativa

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/cadastro")
def register(usuario: Union[UsuarioCreateCidadao, UsuarioCreateCooperativa]):
    existing_user = db.collection("usuarios").document(usuario.tipo).collection("dados").where("email", "==", usuario.email).get()
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuário já cadastrado.")
    tipo = usuario.tipo.lower()

    if tipo == "cidadao":
        db.collection("usuarios").document("cidadao").collection("dados").document(usuario.id).set(usuario.dict())
    
    elif tipo == "cooperativa":
        if not usuario.cnpj or not usuario.nome_cooperativa:
            raise HTTPException(status_code=400, detail="CNPJ e Nome da Cooperativa são obrigatórios para o tipo 'cooperativa'.")
        
        db.collection("usuarios").document("cooperativa").collection("dados").document(usuario.id).set(usuario.dict())

    else:
        raise HTTPException(status_code=400, detail="Tipo de usuário inválido")

    return {"mensagem": f"Usuário do tipo {tipo} cadastrado com sucesso"}


@router.post("/login")
def login(user: Union[UsuarioCidadao, UsuarioCooperativa]):
    users_ref = db.collection("usuarios")
    query = users_ref.where("email", "==", user.email).get()
    if not query:
        query = users_ref.where("telefone", "==", user.telefone).get()
    if not query:
        raise HTTPException(status_code=400, detail="Email ou senha incorretos.")

    user_doc = query[0]
    return {"mensagem": "Login bem-sucedido", "user_id": user_doc.id}


@router.get("/perfil")
#Autenticação off por enquanto = Depends(verify_token)
def perfil_usuario(usuario: dict):
    return {
        "mensagem": f"Olá, {usuario.get('name', 'usuário')}!",
        "uid": usuario["uid"],
        "email": usuario.get("email")
    }

@router.put("/perfil/atualizar")
def atualizar_perfil(
    tipo: Literal["cidadao", "cooperativa"],
    user_data: dict,
    dados_atualizados: dict = Body(...)
):
    try:
        doc_ref = (
            db.collection("usuarios")
            .document(tipo)
            .collection("dados")
            .document(user_data["uid"])
        )
        doc_ref.update(dados_atualizados)
        return {"mensagem": "Perfil atualizado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar: {e}")
    
@router.post("/cadastro/residencia")
#token: str = Depends(verify_token)
def cadastrar_residencia(usuario: UsuarioCidadao, endereco: str):
    existing_residence = db.collection("usuarios").document(usuario.id).collection("residencias").where("endereco", "==", endereco).get()
    if existing_residence:
        raise HTTPException(status_code=400, detail="Residência já cadastrada.")
    
    db.collection("usuarios").document(usuario.id).collection("residencias").add({"endereco": endereco})
    return {"message": "Residência cadastrada com sucesso!"}

@router.get("/rotas_publicadas")
#, token: str = Depends(verify_token)
def visualizar_rotas_publicadas(usuario: UsuarioCidadao):
    rotas = db.collection("rotas").where("data", "==", "hoje").where("residencias", "array_contains", usuario.endereco).get()
    if not rotas:
        raise HTTPException(status_code=404, detail="Nenhuma rota encontrada para o dia de hoje.")
    rotas_info = []
    for rota in rotas:
        rotas_info.append(rota.to_dict())
    
    return {"rotas": rotas_info}

# Cidadão: Confirmar se o caminhão passou
@router.post("/confirmar_coleta")
def confirmar_coleta(usuario: UsuarioCidadao, endereco: str, coleta_confirmada: bool):
    # Verifica se a residência existe
    residencia_ref = db.collection("usuarios").document(usuario.id).collection("residencias").where("endereco", "==", endereco).get()
    if not residencia_ref:
        raise HTTPException(status_code=400, detail="Residência não encontrada.")
    
    db.collection("usuarios").document(usuario.id).collection("residencias").document(residencia_ref[0].id).update({"coleta_confirmada": coleta_confirmada})
    return {"message": "Coleta confirmada com sucesso!"}

@router.post("/adicionar_lixo_reciclavel")
def adicionar_lixo_reciclavel(usuario: UsuarioCidadao, endereco: str, reciclavel: bool):
    residencia_ref = db.collection("usuarios").document(usuario.id).collection("residencias").where("endereco", "==", endereco).get()
    if not residencia_ref:
        raise HTTPException(status_code=400, detail="Residência não encontrada.")
    
    db.collection("usuarios").document(usuario.id).collection("residencias").document(residencia_ref[0].id).update({"reciclavel": reciclavel})
    return {"message": "Informação sobre lixo reciclável atualizada com sucesso!"}
