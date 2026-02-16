import sys
import os
import uuid
from datetime import datetime

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent_backend.infrastructure.repositories.firestore_db import FirestoreSolicitudRepository
from src.agent_backend.domain.models import SolicitudTramite
from dotenv import load_dotenv

load_dotenv()

def test_firestore_write():
    print("--- Testing Firestore Write (SolicitudTramite) ---")
    
    repo = FirestoreSolicitudRepository()
    
    test_id = uuid.uuid4()
    solicitud = SolicitudTramite(
        id_solicitud=test_id,
        dni_becario="99999999", # Test DNI
        carrera_destino="Ingeniería de Pruebas",
        justificacion_ia="Prueba de inserción automática",
        es_alumno_activo=True,
        fecha_solicitud=datetime.now(),
        estado_tramite="PENDIENTE_TEST"
    )
    
    print(f"Saving solicitud with ID: {test_id}")
    try:
        saved = repo.save(solicitud)
        print("✅ Solicitud saved successfully.")
        print(f"ID: {saved.id_solicitud}")
        
        # Verify read (optional, if repo had read method for solicitud)
        # For now, success means no exception during .set()
        
    except Exception as e:
        print(f"❌ Error saving solicitud: {e}")
        raise e

if __name__ == "__main__":
    test_firestore_write()
