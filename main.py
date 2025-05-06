from fastapi import FastAPI, APIRouter
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_config import db
from routes.auth import auth_router
from routes.cidadao import cidadao_router
from routes.cooperativa import coop_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(cidadao_router, prefix="/cidadao", tags=["cidadao"])
app.include_router(coop_router, prefix="/cooperativa", tags=["cooperativa"])


@app.get("/home")
def read_root():
    return {"message": "API funcionando!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
