from fastapi import APIRouter, HTTPException
from src.agent_backend.infrastructure.adapters.input.schemas import ChatRequest, ChatResponse, ApprovalRequest, ApprovalResponse
from src.agent_backend.application.graph import app as graph_app
from src.agent_backend.application.schemas import RegistrarSolicitud
# from src.agent_backend.infrastructure.repositories.mock_db import solicitud_repo
from src.agent_backend.infrastructure.repositories.firestore_db import FirestoreSolicitudRepository
from src.agent_backend.domain.models import SolicitudTramite
import uuid
import json

solicitud_repo = FirestoreSolicitudRepository()

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    
    # Run the graph
    inputs = {"messages": [("user", request.message)]}
    # Using invoke directly (not streaming for simplicity in this prototype)
    result = graph_app.invoke(inputs, config=config)
    
    # Extract last message
    last_message = result['messages'][-1]
    response_text = last_message.content
    
    # Check for approval requirement
    # We look if 'proponer_tramite' was called in the recent history and resulted in "PROPUESTO"
    approval_required = False
    approval_payload = None
    
    # Iterate backwards to find tool calls
    for msg in reversed(result['messages']):
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tool_call in msg.tool_calls:
                if tool_call['name'] == 'proponer_tramite':
                    # Found a proposal. Now find the output for this tool call?
                    # Actually, the AgentState doesn't easily map tool_call to output in 'messages' 
                    # unless we search for ToolMessage with artifact.
                    pass
        if msg.type == 'tool':
            # Check if this tool message corresponds to proponer_tramite
            # ToolMessage content is stringified dict
            try:
                content = json.loads(msg.content)
                if content.get("status") == "PROPUESTO":
                    approval_required = True
                    approval_payload = content.get("payload")
                    break
            except:
                pass
                
    return ChatResponse(
        response=response_text,
        thread_id=request.thread_id,
        approval_required=approval_required,
        approval_payload=approval_payload
    )

@router.post("/aprobar", response_model=ApprovalResponse)
async def aprobar_endpoint(request: ApprovalRequest):
    if not request.approved:
        return ApprovalResponse(status="REJECTED", message="Solicitud rechazada por el operador.")
    
    try:
        data = request.payload
        # Convert to Domain Entity
        solicitud = SolicitudTramite(
            dni_becario=data["dni"],
            carrera_destino=data["carrera_destino"],
            justificacion_ia=data["analisis_afinidad"],
            es_alumno_activo=data["es_alumno_activo"],
            estado_tramite="APROBADO" 
        )
        saved = solicitud_repo.save(solicitud)
        return ApprovalResponse(
            status="APPROVED", 
            solicitud_id=str(saved.id_solicitud), 
            message="Solicitud registrada exitosamente en DB."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
