import firebase_admin
from firebase_admin import credentials, firestore
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pyrebase

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