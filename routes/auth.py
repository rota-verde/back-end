from typing import Literal
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import JSONResponse
from firestore import db, firebase
from firebase_admin import auth
from schemas.user import UserCreate, UserLogin

auth_router = APIRouter()

@auth_router.post("/register")
async def register_user(user: UserCreate):
        name = user.nome_usuario
        email = user.email
        phone = user.telefone
        password = user.senha
        role = user.role #criar os usuarios baseados no tipo

        try:
            user = auth.create_user(
                display_name=name,
                email=email,
                phone_number=phone,
                password=password
            )

            return JSONResponse(content={"message": f"Conta criada com sucesso para o usuario: {user.uid}"}, status_code=201)
        except auth.EmailAlreadyExistsError:
            raise HTTPException(status_code=400, detail= f"Conta com o email: {email} ja existe.")

@auth_router.post("/login")
async def login_user(credentials: UserLogin):
        email = credentials.email
        password = credentials.senha

        try:
            user = firebase.auth().sign_in_with_email_and_password(
                email = email,
                password = password
            )

            token = user['idToken']
            
            return JSONResponse(content={"token": token}, status_code=200)
        except:
             raise HTTPException(status_code=400, detail="Email ou senha invalidos.")

@auth_router.post("/forgot-password")
async def forgot_password(telefone: str): ...

@auth_router.post("/reset-password")
async def reset_password(token: str, new_password: str): ...

@auth_router.delete("/delete-account/{user_id}")
async def delete_account(user_id: str): ...

@auth_router.post("/2fa/enable/{user_id}")
async def enable_2fa(user_id: str): ...

@auth_router.post("/2fa/verify")
#async def verify_2fa(data: TwoFAVerification): ... # type: ignore

@auth_router.get("/terms-of-service")
async def get_terms_of_service(): ...

@auth_router.get("/privacy-policy")
async def get_privacy_policy(): ...

# VER PERFIL

@auth_router.get("/perfil")

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

@auth_router.put("/perfil/atualizar")

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

