import firebase_admin
from firebase_admin import credentials, firestore
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("./rota-verde-ea753-firebase-adminsdk-fbsvc-bf3cc22a45.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://rota-verde-ea753-default-rtdb.firebaseio.com/'  
# })

# ref = db.reference('/') #referencia para a raiz
