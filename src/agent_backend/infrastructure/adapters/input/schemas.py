from pydantic import BaseModel
from typing import List, Optional, Any

class ChatRequest(BaseModel):
    message: str
    thread_id: str

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    approval_required: bool = False
    approval_payload: Optional[dict] = None

class ApprovalRequest(BaseModel):
    payload: dict # RegistroSolicitud payload
    approved: bool

class ApprovalResponse(BaseModel):
    status: str
    solicitud_id: Optional[str]
    message: str
