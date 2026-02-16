from langchain_core.tools import tool
# from src.agent_backend.infrastructure.repositories.mock_db import beneficiario_repo
from src.agent_backend.infrastructure.repositories.firestore_db import FirestoreBeneficiarioRepository
from src.agent_backend.application.schemas import RegistrarSolicitud

beneficiario_repo = FirestoreBeneficiarioRepository()

@tool
def consultar_estado_becario(dni: str) -> dict:
    """
    Consulta el estado académico de un becario por su DNI en la base de datos institucional.
    Usa esta herramienta SIEMPRE que identifiques un DNI en la solicitud del usuario.
    Retorna los datos del becario (estado, carrera, etc.) o un error si no existe.
    """
    print(f"DEBUG: Consultando DNI: {dni}")
    becario = beneficiario_repo.get_by_dni(dni)
    if not becario:
        return {"error": "Becario no encontrado", "found": False}
    return {"found": True, "data": becario.model_dump()}

@tool
def proponer_tramite(solicitud: RegistrarSolicitud) -> dict:
    """
    Propone una solicitud de cambio de carrera.
    Usa esta herramienta cuando el usuario quiera proceder con el cambio y la validación sea exitosa.
    Retorna los datos estructurados para que el sistema HITL los procese.
    """
    print(f"DEBUG: Proponiendo trámite: {solicitud}")
    return {"payload": solicitud.model_dump(), "status": "PROPUESTO"}
