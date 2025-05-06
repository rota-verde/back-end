from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
from services.auth_service import get_current_user
from firebase_config import firebase_instance, db
from schemas.user import UserCreate, UserLogin, UserResponse, UserBase

auth_router = APIRouter()
firebase_auth = firebase_instance.auth()
@auth_router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(user: UserCreate):
    try:
        firebase_user = firebase_auth.create_user_with_email_and_password(
            email=user.email,
            password=user.senha
        )
        uid = firebase_user['localId']
        user_data = user.model_dump(exclude={"senha"})
        user_data["uid"] = uid
        user_data["nome_usuario"] = user.nome_usuario  
        user_data["telefone"] = user.telefone      
        user_data["role"] = user.role                

        # # Definir custom claim para o role
        # firebase_instance.auth().set_custom_user_claims(uid, {"role": user.role})

        try:
            db.collection("usuarios").document(uid).set(user_data)
        except FirebaseError as e:
            raise HTTPException(status_code=500, detail=f"Erro ao salvar usuário no Firestore: {str(e)}")

        return UserResponse(**user_data)
    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail=f"Conta com o email: {user.email} já existe.")
    except FirebaseError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar conta: {str(e)}")

@auth_router.post("/login")
async def login_user(credentials: UserLogin):
    try:
        user = firebase_instance.auth().sign_in_with_email_and_password(
            email=credentials.email,
            password=credentials.senha
        )
        token = user['idToken']
        return JSONResponse(content={"token": token}, status_code=200)
    except FirebaseError:
        raise HTTPException(status_code=400, detail="Email ou senha inválidos.")

@auth_router.get("/user/{user_id}", response_model=UserBase)
async def get_user(user_id: str, current_user_id: str = Depends(get_current_user)):
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para acessar este usuário.")

    try:
        firebase_user = firebase_instance.auth().get_user(user_id)
        firestore_user = db.collection("usuarios").document(user_id).get()

        if not firestore_user.exists:
            raise HTTPException(status_code=404, detail="Dados do usuário não encontrados.")

        user_data = firestore_user.to_dict()
        return UserBase(uid=firebase_user.uid, **user_data, role=firebase_user.custom_claims.get("role"))
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    except FirebaseError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuário: {str(e)}")

@auth_router.put("/user/update/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserCreate, current_user_id: str = Depends(get_current_user)):
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para atualizar este usuário.")

    try:
        user_updates_auth = {
            "display_name": user.nome_usuario,
            "email": user.email,
            "phone_number": user.telefone,
            "password": user.senha  # Considere se a senha deve ser atualizada aqui
        }
        auth.update_user(user_id, **user_updates_auth)

        user_updates_firestore = user.model_dump(exclude={"senha"})
        db.collection("usuarios").document(user_id).update(user_updates_firestore)

        # Obter os dados atualizados do Firestore para a resposta
        updated_user_data = db.collection("usuarios").document(user_id).get().to_dict()
        return UserResponse(uid=user_id, **updated_user_data, role=user.role)

    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    except FirebaseError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")

@auth_router.post("/forgot-password")
async def forgot_password(credentials: UserLogin):
    try:
        reset_link = auth.generate_password_reset_link(credentials.email)
        return JSONResponse(content={"message": "Link de redefinição de senha gerado com sucesso.", "reset_link": reset_link}, status_code=200)
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="Usuário com este email não encontrado.")
    except FirebaseError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar email de redefinição: {str(e)}")

@auth_router.post("/reset-password")
async def reset_password(oobCode: str, new_password: str):
    try:
        auth.confirm_password_reset(oobCode, new_password)
        return JSONResponse(content={"message": "Senha redefinida com sucesso!"}, status_code=200)
    except auth.InvalidOobCodeError:
        raise HTTPException(status_code=400, detail="Código de redefinição de senha inválido ou expirado.")
    except FirebaseError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao redefinir senha: {str(e)}")

@auth_router.delete("/delete-account/{user_id}")
async def delete_account(user_id: str, current_user_id: str = Depends(get_current_user)):
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para deletar esta conta.")

    try:
        auth.delete_user(user_id)
        db.collection("usuarios").document(user_id).delete()
        return JSONResponse(content={"message": f"Usuário {user_id} deletado com sucesso."}, status_code=200)
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    except FirebaseError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar usuário: {str(e)}")

# Placeholder para as rotas restantes
@auth_router.post("/2fa/enable/{user_id}")
async def enable_2fa(user_id: str):
    raise HTTPException(status_code=501, detail="Funcionalidade não implementada.")

@auth_router.post("/2fa/verify")
async def verify_2fa():
    raise HTTPException(status_code=501, detail="Funcionalidade não implementada.")

@auth_router.get("/terms-of-service")
async def get_terms_of_service():
    raise HTTPException(status_code=501, detail="Funcionalidade não implementada.")

@auth_router.get("/privacy-policy")
async def get_privacy_policy():
    raise HTTPException(status_code=501, detail="Funcionalidade não implementada.")


@auth_router.post("/2fa/enable/{user_id}")
async def enable_2fa(user_id: str): ...

@auth_router.post("/2fa/verify")
#async def verify_2fa(data: TwoFAVerification): ... # type: ignore

@auth_router.get("/terms-of-service")
async def get_terms_of_service(): ...

@auth_router.get("/privacy-policy")
async def get_privacy_policy(): ...





