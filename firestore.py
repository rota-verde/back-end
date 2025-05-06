from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import firebase_admin
from firebase_admin import credentials, firestore
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from jwt import InvalidTokenError
import pyrebase
from routes import auth
from firebase_admin import auth



cred = credentials.Certificate("./rota-verde-ea753-firebase-adminsdk-fbsvc-bf3cc22a45.json")
firebase_admin.initialize_app(cred)

firebaseConfig = {
  "apiKey": "AIzaSyBiAxQppDfYxUpWytRjfb_Mo_6fkNKvtb4",
  "authDomain": "rota-verde-ea753.firebaseapp.com",
  "databaseURL": "https://rota-verde-ea753-default-rtdb.firebaseio.com",
  "projectId": "rota-verde-ea753",
  "storageBucket": "rota-verde-ea753.firebasestorage.app",
  "messagingSenderId": "578295814689",
  "appId": "1:578295814689:web:c0de33ea82560918f0e160",
  "measurementId": "G-W99FZCEJS3"
}

firebase = pyrebase.initialize_app(firebaseConfig)

db = firestore.client()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
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