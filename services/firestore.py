import firebase_admin
from firebase_admin import credentials, firestore
import os

cred = credentials.Certificate("/home/gabriela/rotaVerde/rota-verde-ea753-firebase-adminsdk-fbsvc-68a9d2fdd2.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
