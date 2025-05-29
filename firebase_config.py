import json
import os
from pathlib import Path
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

FIREBASE_CREDS_ENV_VAR = "FIREBASE_CREDENTIALS_JSON"
# Caminho temporário para o arquivo de credenciais dentro do contêiner
TEMP_FIREBASE_CREDENTIALS_FILE = Path("/tmp/firebase_credentials.json")

# Flag para verificar se o Firebase foi inicializado
firebase_initialized = False

# Verifica se a variável de ambiente existe
if os.getenv(FIREBASE_CREDS_ENV_VAR):
    try:
        # Pega o conteúdo JSON da variável de ambiente
        credentials_json_content = os.getenv(FIREBASE_CREDS_ENV_VAR)

        # Salva o conteúdo em um arquivo temporário
        TEMP_FIREBASE_CREDENTIALS_FILE.write_text(credentials_json_content)

        print(f"Credenciais do Firebase carregadas da variável de ambiente '{FIREBASE_CREDS_ENV_VAR}' e salvas em '{TEMP_FIREBASE_CREDENTIALS_FILE}'")

        # Inicializa o Firebase Admin SDK usando o arquivo temporário
        cred = credentials.Certificate(str(TEMP_FIREBASE_CREDENTIALS_FILE))
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        firebase_initialized = True
        print("Firebase Admin SDK inicializado com sucesso!")

    except json.JSONDecodeError:
        print(f"Erro: O conteúdo da variável de ambiente '{FIREBASE_CREDS_ENV_VAR}' não é um JSON válido.")
        raise ValueError(f"Firebase credentials JSON is invalid in env var {FIREBASE_CREDS_ENV_VAR}")
    except Exception as e:
        print(f"Erro ao inicializar Firebase Admin SDK: {e}")
        raise RuntimeError(f"Failed to initialize Firebase Admin SDK: {e}")
else:
    print(f"Variável de ambiente '{FIREBASE_CREDS_ENV_VAR}' não encontrada. Firebase Admin SDK NÃO será inicializado.")


