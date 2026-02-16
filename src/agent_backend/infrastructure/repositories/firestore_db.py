import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional
from src.agent_backend.domain.models import Becario, SolicitudTramite
from src.agent_backend.domain.ports import BeneficiarioRepository, SolicitudRepository
import os

# Initialize Firebase
# Ensure GOOGLE_APPLICATION_CREDENTIALS points to the JSON key file
if not firebase_admin._apps:
    try:
        # If running locally with .env
        cred = credentials.ApplicationDefault()
        if os.getenv("FIREBASE_CREDENTIALS_PATH"):
             cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
        
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Warning: Firebase Auth failed: {e}. Ensure GOOGLE_APPLICATION_CREDENTIALS is set.")

db = firestore.client()

class FirestoreBeneficiarioRepository(BeneficiarioRepository):
    def __init__(self):
        self.collection = db.collection('beneficiarios')

    def get_by_dni(self, dni: str) -> Optional[Becario]:
        doc_ref = self.collection.document(dni)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            # Ensure dni is in the data if it was stored as document ID
            data['dni'] = dni 
            return Becario(**data)
        return None

class FirestoreSolicitudRepository(SolicitudRepository):
    def __init__(self):
        self.collection = db.collection('solicitudes_tramite')

    def save(self, solicitud: SolicitudTramite) -> SolicitudTramite:
        # Save validation
        data = solicitud.dict()
        # Convert UUID to str
        data['id_solicitud'] = str(data['id_solicitud'])
        
        self.collection.document(str(solicitud.id_solicitud)).set(data)
        return solicitud

# Conditional export
# You would swap this in your Dependency Injection container or simple factory
