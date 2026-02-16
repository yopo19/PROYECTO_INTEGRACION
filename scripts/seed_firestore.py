import sys
import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent_backend.infrastructure.repositories.mock_db import SEED_BECARIOS

def seed_firebase():
    print("Iniciando carga de datos a Firestore...")
    
    # Auth
    if not firebase_admin._apps:
        try:
            key_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            if key_path:
                cred = credentials.Certificate(key_path)
            else:
                cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"Error autenticando: {e}")
            return

    db = firestore.client()
    batch = db.batch()
    
    collection_ref = db.collection('beneficiarios')
    
    for becario in SEED_BECARIOS:
        print(f"Agregando: {becario.nombre_completo} ({becario.dni})")
        doc_ref = collection_ref.document(becario.dni)
        batch.set(doc_ref, becario.dict())
    
    batch.commit()
    print("✅ Carga masiva completada exitosamente.")

if __name__ == "__main__":
    if not os.getenv("FIREBASE_CREDENTIALS_PATH") and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("⚠️ ERROR: Debes configurar la variable de entorno FIREBASE_CREDENTIALS_PATH o GOOGLE_APPLICATION_CREDENTIALS")
        sys.exit(1)
        
    seed_firebase()
