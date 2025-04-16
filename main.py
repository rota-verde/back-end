from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials, firestore
from models import Usuario
from services.firestore import db
from routes import userRoutes

app = FastAPI()
app.include_router(Usuario.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "API funcionando!"}

app.include_router(userRoutes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
