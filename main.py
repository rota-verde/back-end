from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials, firestore
from services.firestore import db
from routes import rotaRoutes,  usersRoutes
from models.user import UsuarioCidadao, UsuarioCooperativa

app = FastAPI()

@app.get("/home")
def read_root():
    return {"message": "API funcionando!"}

app.include_router(usersRoutes.router)
app.include_router(rotaRoutes.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
