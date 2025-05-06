from fastapi import FastAPI, APIRouter
import firebase_admin
from firebase_admin import credentials, firestore
from firestore import db
from routes.auth import auth_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.get("/home")
def read_root():
    return {"message": "API funcionando!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
