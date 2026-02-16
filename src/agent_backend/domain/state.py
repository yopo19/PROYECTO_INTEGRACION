from typing import TypedDict, Annotated, List, Optional
from langgraph.graph.message import add_messages
from src.agent_backend.domain.models import Becario

class AgentState(TypedDict):
    """Estado del Agente para el flujo de Cambio de Carrera."""
    messages: Annotated[List[dict], add_messages]
    dni_detectado: Optional[str]
    becario_data: Optional[dict] # Serialized Becario model
    intencion: Optional[str]
    analisis_completo: bool
    payload_solicitud: Optional[dict] # The proposed JSON for the transaction
    estado_validacion: str # 'PENDIENTE', 'VALIDO', 'INVALIDO', 'ERROR'
