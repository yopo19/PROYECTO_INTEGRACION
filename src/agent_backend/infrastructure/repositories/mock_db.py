from typing import Dict, Optional, List
import random
from src.agent_backend.domain.models import Becario, SolicitudTramite
from src.agent_backend.domain.ports import BeneficiarioRepository, SolicitudRepository

# Helper for random generation
CARRERAS = ["Ingeniería de Sistemas", "Ingeniería Civil", "Ingeniería Industrial", "Ingeniería Mecánica", "Ingeniería Electrónica", "Ingeniería de Software", "Ingeniería Ambiental", "Ingeniería de Minas"]
INSTITUCIONES = ["Universidad Nacional de Ingeniería (UNI)", "Pontificia Universidad Católica del Perú (PUCP)", "Universidad Nacional Mayor de San Marcos (UNMSM)", "Universidad Peruana de Ciencias Aplicadas (UPC)", "Universidad de Lima", "Universidad Nacional de San Agustín (UNSA)", "Universidad Nacional de Trujillo (UNT)"]
ESTADOS = ["ACTIVO", "OBSERVADO", "EGRESADO"]

def generate_seed_data() -> List[Becario]:
    data = []
    # Specific known cases
    data.append(Becario(dni="12345678", nombre_completo="Juan Perez", estado="ACTIVO", carrera_actual="Ingeniería de Sistemas", institucion="UNI", promedio_ponderado=15.5))
    data.append(Becario(dni="87654321", nombre_completo="Maria Lopez", estado="EGRESADO", carrera_actual="Ingeniería Industrial", institucion="PUCP", promedio_ponderado=18.0))
    data.append(Becario(dni="11223344", nombre_completo="Carlos Ruiz", estado="OBSERVADO", carrera_actual="Ingeniería Civil", institucion="UPCH", promedio_ponderado=12.5))
    
    # Generate 7 more to reach 10
    nombres_base = ["Ana", "Luis", "Elena", "Pedro", "Sofia", "Miguel", "Lucia"]
    apellidos_base = ["Gomez", "Torres", "Vargas", "Rojas", "Mendoza", "Castillo", "Flores"]
    
    for i in range(7):
        dni = f"{random.randint(10000000, 99999999)}"
        nombre = f"{nombres_base[i]} {apellidos_base[i]}"
        estado = random.choices(ESTADOS, weights=[0.7, 0.2, 0.1])[0] # Mostly active
        carrera = random.choice(CARRERAS)
        uni = random.choice(INSTITUCIONES)
        promedio = round(random.uniform(12.0, 20.0), 2)
        
        data.append(Becario(
            dni=dni,
            nombre_completo=nombre,
            estado=estado,
            carrera_actual=carrera,
            institucion=uni,
            promedio_ponderado=promedio
        ))
    return data

SEED_BECARIOS = generate_seed_data()

class InMemoryBeneficiarioRepository(BeneficiarioRepository):
    def __init__(self):
        self.db: Dict[str, Becario] = {b.dni: b for b in SEED_BECARIOS}

    def get_by_dni(self, dni: str) -> Optional[Becario]:
        return self.db.get(dni)

# Global instances
beneficiario_repo = InMemoryBeneficiarioRepository()

class InMemorySolicitudRepository(SolicitudRepository):
    def __init__(self):
        self.db: List[SolicitudTramite] = []

    def save(self, solicitud: SolicitudTramite) -> SolicitudTramite:
        self.db.append(solicitud)
        return solicitud

solicitud_repo = InMemorySolicitudRepository()
