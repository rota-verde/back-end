import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pyrebase
load_dotenv()

firebaseConfig = {
  "apiKey": os.environ.get("FIREBASE_API_KEY"),
  "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
  "databaseURL": os.environ.get("FIREBASE_DATABASE_URL"),
  "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
  "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
  "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
  "appId": os.environ.get("FIREBASE_APP_ID"),
  "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID") 
}

firebase_instance = pyrebase.initialize_app(firebaseConfig)
#cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
cred_path = './rota-verde-ea753-firebase-adminsdk-fbsvc-68a9d2fdd2.json'
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()
