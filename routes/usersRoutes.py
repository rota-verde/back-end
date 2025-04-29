from typing import List, Literal, Optional, Union
import uuid
from fastapi import APIRouter, Body, Depends, HTTPException
from services.auth import verificar_token
from services.firestore import db
from models.user import UsuarioCidadao, UsuarioCooperativa,  UsuarioCreateCidadao, UsuarioCreateCooperativa, UsuarioEntrar

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

#CADASTRAR USUARIOS
@router.post("/cadastro")
def register(usuario: Union[UsuarioCreateCidadao, UsuarioCreateCooperativa]):
    existing_user = db.collection("usuarios").document(usuario.tipo).collection("dados")\
        .where("telefone", "==", usuario.telefone).get()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuário com esse telefone já cadastrado.")
    
    tipo = usuario.tipo.lower()
    user_dict = usuario.model_dump()
    user_id = str(uuid.uuid4())
    user_dict["id"] = user_id
    

    if tipo == "cidadao":
        db.collection("usuarios").document("cidadao").collection("dados").document(user_id).set(user_dict)
    
    elif tipo == "cooperativa":
        if not getattr(usuario, "cnpj", None) or not getattr(usuario, "nome_cooperativa", None):
            raise HTTPException(status_code=400, detail="CNPJ e Nome da Cooperativa são obrigatórios para o tipo 'cooperativa'.")
        
        db.collection("usuarios").document("cooperativa").collection("dados").document(user_id).set(user_dict)

    else:
        raise HTTPException(status_code=400, detail="Tipo de usuário inválido")

    return {"mensagem": f"Usuário do tipo {tipo} cadastrado com sucesso"}


#LOGIN
@router.post("/login")
def login(user: UsuarioEntrar):
    tipos = ["cidadao", "cooperativa"] 
    user_data = None
    user_id = None

    for tipo in tipos:
        users_ref = db.collection("usuarios").document(tipo).collection("dados")
        query = users_ref.where("telefone", "==", user.telefone).get()
        if query:
            user_data = query[0].to_dict()
            user_id = query[0].id
            break

    if not user_data:
        raise HTTPException(status_code=400, detail="Telefone não encontrado.")
    
    if user_data.get("senha") != user.senha:
        raise HTTPException(status_code=400, detail="Senha incorreta.")
    
    return {"mensagem": "Login bem-sucedido", "user_id": user_id}

# VER PERFIL
@router.get("/perfil")
def perfil_usuario(id: str):
    id = str(id)
    tipos = ["cidadao", "cooperativa"]
    user_data = None

    for tipo in tipos:
        users_ref = db.collection("usuarios").document(tipo).collection("dados")
        query = users_ref.where("id", "==", id).get()
        if query:
            user_data = query[0].to_dict()
            break

    if not user_data:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    tipo = user_data.get("tipo")
    resposta = {
        "mensagem": f"Olá, {user_data.get('username') or user_data.get('nome_cooperativa')}!",
        "id": id,
        "email": user_data.get("email"),
        "telefone": user_data.get("telefone"),
        "endereco": user_data.get("endereco"),
        "bairro": user_data.get("bairro"),
        "tipo": tipo,
        "cpf": user_data.get("cpf") if tipo == "cidadao" else None,
        "cnpj": user_data.get("cnpj") if tipo == "cooperativa" else None
    }

    return resposta
# ATUALIZAR PERFIL
@router.put("/perfil/atualizar")
def atualizar_perfil(
    tipo: Literal["cidadao", "cooperativa"],
    user_id: str,
    dados_atualizados: dict = Body(...)
):
    if tipo not in ["cidadao", "cooperativa"]:
        raise HTTPException(status_code=400, detail="Tipo de usuário inválido.")
    
    try:
        doc_ref = (
            db.collection("usuarios")
            .document(tipo)
            .collection("dados")
            .document(user_id)
        )
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        
        doc_ref.update(dados_atualizados)
        return {"mensagem": "Perfil atualizado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar perfil: {str(e)}")

#ADD NOVOS ENDERECOS - CIDADÃO (estabelecimento, outra residencia, etc)
@router.post("/perfil/adicionar_endereco")
def cadastrar_endereco(payload: dict = Body(...)):
    user_id = str(payload["id"])
    novo_endereco = payload["endereco"]

    doc_ref = db.collection("usuarios").document("cidadao")\
        .collection("dados").document(user_id)

    doc = doc_ref.get()
    if doc.exists:
        dados = doc.to_dict()
        enderecos = dados.get("enderecos", [])
        if novo_endereco in enderecos:
            raise HTTPException(status_code=400, detail="Endereço já cadastrado.")
        enderecos.append(novo_endereco)
    else:
        enderecos = [novo_endereco]

    doc_ref.set({"enderecos": enderecos}, merge=True)
    return {"message": "Endereço adicionado com sucesso!"}

#VISUALIZAR ENDERECOS - CIDADÃO
@router.get("/perfil/enderecos")
def visualizar_enderecos(id: str):
    id = str(id)
    doc_ref = db.collection("usuarios").document("cidadao").collection("dados").document(id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    dados = doc.to_dict()
    enderecos = dados.get("enderecos", [])

    return {"enderecos": enderecos}

#APAGAR ENDERECOS - CIDADÃO
@router.delete("/perfil/apagar_endereco")
def apagar_endereco(dados: dict = Body(...)):
    id = str(dados["id"])
    endereco = dados["endereco"]

    dados_ref = db.collection("usuarios").document("cidadao").collection("dados").document(id).collection("enderecos")
    matching = dados_ref.where("endereco", "==", endereco).get()

    if not matching:
        raise HTTPException(status_code=400, detail="Endereço não encontrado.")

    for doc in matching:
        dados_ref.document(doc.id).delete()

    return {"message": "Endereço apagado com sucesso!"}


# @router.get("/rotas_publicadas")
# #, token: str = Depends(verify_token)
# def visualizar_rotas_publicadas(usuario: UsuarioCidadao):
#     rotas = db.collection("rotas").where("data", "==", "hoje").where("residencias", "array_contains", usuario.endereco).get()
#     if not rotas:
#         raise HTTPException(status_code=404, detail="Nenhuma rota encontrada para o dia de hoje.")
#     rotas_info = []
#     for rota in rotas:
#         rotas_info.append(rota.to_dict())
    
#     return {"rotas": rotas_info}

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
