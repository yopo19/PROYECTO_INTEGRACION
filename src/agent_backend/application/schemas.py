from pydantic import BaseModel, Field

class RegistrarSolicitud(BaseModel):
    """Esquema para proponer un trámite de cambio de carrera."""
    dni: str = Field(..., description="DNI del becario validado en la base de datos")
    carrera_destino: str = Field(..., description="Nombre oficial de la carrera a la que se desea cambiar")
    analisis_afinidad: str = Field(..., description="Breve justificación de por qué las carreras son afines")
    es_alumno_activo: bool = Field(..., description="Confirmación de que el status en BD es ACTIVO")
