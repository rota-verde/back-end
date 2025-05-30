from http import HTTPStatus
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
from firebase_config import firebase_instance, db
from schemas.user import UserCreate, UserLogin, UserResponse, UserBase

auth_router = APIRouter()


@auth_router.post(
    "/register", response_model=UserResponse, status_code=HTTPStatus.CREATED
)
async def register_user(user: UserCreate):
    try:
        firebase_user = firebase_instance.auth().create_user_with_email_and_password(
            email=user.email, password=user.senha
        )
        uid = firebase_user["localId"]
        user_data = user.model_dump(exclude={"senha"})
        user_data.update(
            {
                "uid": uid,
                "nome_usuario": user.nome_usuario,
                "telefone": user.telefone,
                "role": user.role,
                "cpf": user.cpf if user.role == "cidadao" else None,
                "cnpj": user.cnpj if user.role == "cooperativa" else None,
                "cnh": user.cnh if user.role == "motorista" else None,
                "nome_cooperativa": (
                    user.nome_cooperativa if user.role == "cooperativa" else None
                ),
                "area_atuacao": (
                    user.area_atuacao if user.role == "cooperativa" else None
                ),
                "endereco": user.endereco.model_dump() if user.endereco else None,
                "materiais_reciclaveis": (
                    user.materiais_reciclaveis if user.role == "cooperativa" else None
                ),
            }
        )

        db.collection("usuarios").document(uid).set(user_data)
        if user.role == "cidadao" and user.endereco:
            db.collection("usuarios").document(uid).collection("residencias").document(
                uid
            ).set(user.endereco.model_dump())

        return UserResponse(**user_data)
    except Exception as e:
        if "EMAIL_EXISTS" in str(e):
            raise HTTPException(
                status_code=400, detail=f"Conta com o email {user.email} já existe."
            )
        raise HTTPException(status_code=500, detail=f"Erro ao criar conta: {str(e)}")


@auth_router.post("/login", status_code=HTTPStatus.OK)
async def login_user(credentials: UserLogin):
    try:
        user = firebase_instance.auth().sign_in_with_email_and_password(
            email=credentials.email, password=credentials.senha
        )
        decoded_token = auth.verify_id_token(user["idToken"])
        user_uid = decoded_token["uid"]
        user_doc = db.collection("usuarios").document(user_uid).get()
        user_data = user_doc.to_dict()
        return JSONResponse(
            content={"token": user["idToken"], "role": user_data["role"]},
            status_code=200,
        )
    except FirebaseError:
        raise HTTPException(status_code=400, detail="Email ou senha inválidos.")


@auth_router.get("/user/{user_id}", response_model=UserBase, status_code=HTTPStatus.OK)
async def get_user(user_id: str):
    try:
        user_doc = db.collection("usuarios").document(user_id).get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        user_data = user_doc.to_dict()
        return UserBase(**user_data)
    except FirebaseError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuário: {str(e)}")


@auth_router.put("/user/update/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserCreate):
    try:
        update_args = {}
        if user.email:
            update_args["email"] = user.email
        if user.senha:
            update_args["password"] = user.senha
        if user.nome_usuario:
            update_args["display_name"] = user.nome_usuario
        if user.telefone:
            update_args["phone_number"] = user.telefone

        if update_args:
            auth.update_user(uid=user_id, **update_args)

        user_data = user.model_dump(exclude={"senha"})
        user_data.update(
            {
                "uid": user_id,
                "nome_usuario": user.nome_usuario,
                "telefone": user.telefone,
                "role": user.role,
                "cpf": user.cpf if user.role == "cidadao" else None,
                "cnpj": user.cnpj if user.role == "cooperativa" else None,
                "cnh": user.cnh if user.role == "motorista" else None,
                "nome_cooperativa": (
                    user.nome_cooperativa
                    if user.role in ["cooperativa", "motorista"]
                    else None
                ),
                "area_atuacao": (
                    user.area_atuacao if user.role == "cooperativa" else None
                ),
                "endereco": user.endereco.model_dump() if user.endereco else None,
                "materiais_reciclaveis": (
                    user.materiais_reciclaveis if user.role == "cooperativa" else None
                ),
            }
        )

        db.collection("usuarios").document(user_id).update(user_data)

        if user.role == "cidadao" and user.endereco:
            db.collection("usuarios").document(user_id).collection(
                "residencias"
            ).document(user_id).set(user.endereco.model_dump(), merge=True)

        updated_user_doc = db.collection("usuarios").document(user_id).get()
        if not updated_user_doc.exists:
            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado no Firestore após a atualização.",
            )

        updated_data = updated_user_doc.to_dict()
        updated_data["uid"] = user_id

        return UserResponse(**updated_data)

    # --- BLOCO DE EXCEÇÃO CORRIGIDO ---
    except FirebaseError as e:
        # Verifica se o erro é 'usuário não encontrado' pelo seu código
        if hasattr(e, "code") and e.code == "auth/user-not-found":
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        # Para todos os outros erros do Firebase, retorna um erro 500
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ocorreu um erro inesperado: {str(e)}"
        )


@auth_router.post("/forgot-password")
async def forgot_password(credentials: UserLogin):
    try:
        firebase_instance.auth().send_password_reset_email(credentials.email)
        return JSONResponse(
            content={"message": "Link de redefinição de senha enviado com sucesso."},
            status_code=200,
        )
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    except FirebaseError as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao enviar email de redefinição: {str(e)}"
        )


@auth_router.post("/reset-password")
async def reset_password(oobCode: str, new_password: str):
    try:
        auth.confirm_password_reset(oobCode, new_password)
        return JSONResponse(
            content={"message": "Senha redefinida com sucesso!"}, status_code=200
        )
    except auth.InvalidOobCodeError:
        raise HTTPException(
            status_code=400, detail="Código de redefinição inválido ou expirado."
        )
    except FirebaseError as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao redefinir senha: {str(e)}"
        )


@auth_router.delete("/delete-account/{user_id}")
async def delete_account(user_id: str):
    try:
        auth.delete_user(user_id)
        db.collection("usuarios").document(user_id).delete()
        return JSONResponse(
            content={"message": f"Usuário {user_id} deletado com sucesso."},
            status_code=200,
        )
    except FirebaseError as e:
        # A forma mais segura de verificar é pelo código do erro
        if e.code == "auth/user-not-found":
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        raise HTTPException(
            status_code=500, detail=f"Erro ao deletar usuário: {str(e)}"
        )


# Rotas placeholder
# @auth_router.post("/2fa/enable/{user_id}")
# async def enable_2fa(user_id: str):
#     raise HTTPException(status_code=501, detail="Funcionalidade não implementada.")


# @auth_router.post("/2fa/verify")
# async def verify_2fa():
#     raise HTTPException(status_code=501, detail="Funcionalidade não implementada.")


# @auth_router.get("/terms-of-service")
# async def get_terms_of_service():
#     raise HTTPException(status_code=501, detail="Funcionalidade não implementada.")


# @auth_router.get("/privacy-policy")
# async def get_privacy_policy():
#     raise HTTPException(status_code=501, detail="Funcionalidade não implementada.")
