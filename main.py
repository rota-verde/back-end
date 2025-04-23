from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials, firestore
from services.firestore import db
from routes import rotaRoutes,  usersRoutes
from services.auth import verify_token
from models.user import UsuarioCidadao, UsuarioCooperativa, UsuarioCreate

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API funcionando!"}

app.include_router(usersRoutes.router)
app.include_router(rotaRoutes.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
