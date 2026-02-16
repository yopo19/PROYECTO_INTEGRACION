from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class Becario(BaseModel):
    dni: str
    nombre_completo: str
    estado: str  # 'ACTIVO', 'OBSERVADO', 'EGRESADO'
    carrera_actual: str
    institucion: str
    promedio_ponderado: Optional[float] = None

class SolicitudTramite(BaseModel):
    id_solicitud: UUID = Field(default_factory=uuid4)
    dni_becario: str
    tipo_tramite: str = "CAMBIO_CARRERA"
    carrera_destino: str
    justificacion_ia: str
    fecha_solicitud: datetime = Field(default_factory=datetime.now)
    estado_tramite: str = "PENDIENTE_APROBACION_COMITE"
    es_alumno_activo: bool
