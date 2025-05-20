from fastapi import FastAPI, APIRouter
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_config import db
from routes.auth import auth_router
from routes.cidadao import cidadao_router
from routes.cooperativa import coop_router
from routes.motorista import motorista_router
from services import popular_bd

app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(cidadao_router, prefix="/cidadao", tags=["cidadao"])
app.include_router(coop_router, prefix="/cooperativa", tags=["cooperativa"])
app.include_router(motorista_router, prefix="/motorista", tags = ["motorista"])
#popular_bd.popular_bd_teste()

@app.get("/home")
def read_root():
    return {"message": "API funcionando!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
