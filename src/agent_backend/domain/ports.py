from abc import ABC, abstractmethod
from typing import Optional
from src.agent_backend.domain.models import Becario, SolicitudTramite

class BeneficiarioRepository(ABC):
    @abstractmethod
    def get_by_dni(self, dni: str) -> Optional[Becario]:
        pass

class SolicitudRepository(ABC):
    @abstractmethod
    def save(self, solicitud: SolicitudTramite) -> SolicitudTramite:
        pass
