from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from routes import auth
from firebase_admin import auth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    print(f"Token recebido: {token}") 
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token de autenticação inválido.")
    except Exception as e:
        print(f"Erro ao verificar token: {e}")  
        raise HTTPException(status_code=500, detail="Erro interno ao verificar o token.")

async def get_current_user_id(current_user: dict = Depends(get_current_user)):
    return current_user.get('uid')