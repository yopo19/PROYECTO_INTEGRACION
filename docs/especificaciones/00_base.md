
# Documento de Proyecto Final: Agente HITL para Gestión de Cambios de Carrera

**Curso:** Integraciones Empresariales con LLMs
[cite_start]**Patrón de Arquitectura:** Human-in-the-Loop (HITL) [cite: 7]
**Caso de Uso:** Validación y Registro de Solicitudes de Cambio de Carrera para Becarios.

---

## 1. Definición del Caso de Uso y Matriz de Riesgo (Fase 1)

### 1.1 Descripción General
El sistema es un **Agente de IA Integrado** que actúa como un primer filtro para las solicitudes de cambio de carrera de los becarios. [cite_start]El agente lee correos electrónicos o cartas de solicitud (no estructurados), verifica el estado del estudiante en la base de datos institucional y evalúa la "afinidad" académica de la nueva carrera solicitada antes de proponer la creación de un trámite formal[cite: 6, 11, 12].

### [cite_start]1.2 Matriz de Riesgo [cite: 10, 14]

| Componente | Definición para el Proyecto |
| :--- | :--- |
| **Rol del Agente** | [cite_start]Analista Junior de Bienestar del Becario[cite: 16]. |
| **Entrada (Input)** | [cite_start]Correo electrónico o carta de motivación del becario (Texto No Estructurado) solicitando el cambio[cite: 12]. |
| **Sistema de Lectura (Safe)** | Tabla de `Beneficiarios` (PostgreSQL/Firebase). [cite_start]Fuente de verdad sobre el estado actual[cite: 17, 40]. |
| **Sistema de Escritura (Unsafe)** | Tabla de `Solicitudes_Tramite` (PostgreSQL/Firebase). [cite_start]Donde se registran los trámites oficiales[cite: 18, 41]. |
| **El Riesgo (Why HITL?)** | **Alucinación de Afinidad / Fraude:** El LLM podría aprobar un cambio a una carrera no afín (ej. de "Ingeniería" a "Artes Culinarias") violando el reglamento, o tramitar una solicitud para un alumno "Observado" o expulsado. [cite_start]Esto requiere validación humana obligatoria[cite: 9, 13, 19]. |

---

## 2. Diseño de Arquitectura y Datos (Fase 2)

### [cite_start]2.1 Diagrama de Flujo de Datos [cite: 22, 23]

1.  **Ingesta:** El usuario (simulado o real) envía el texto de la solicitud.
2.  [cite_start]**Orquestador (FastAPI):** Recibe el texto y mantiene el historial del chat[cite: 32, 44].
3.  **Razonamiento (LLM):** Analiza la intención y extrae el DNI.
4.  [cite_start]**Tool Calling (Lectura):** Ejecuta `consultar_estado_becario(dni)` automáticamente[cite: 40].
5.  **Evaluación:** El LLM cruza la información recuperada con la solicitud. Si es válido, estructura los datos para el trámite.
6.  **Tool Calling (Escritura):** El LLM intenta ejecutar `registrar_solicitud(...)`.
7.  [cite_start]**Interceptor (Middleware):** El backend detecta el intento de escritura, **bloquea** la ejecución y retorna un estado `APPROVAL_REQUIRED` junto con el payload JSON[cite: 7, 24, 47].
8.  [cite_start]**Interfaz HITL (Streamlit):** Muestra los datos al humano para su confirmación[cite: 58].
9.  [cite_start]**Ejecución Final:** Solo tras el clic humano, se escribe en la BD[cite: 64].

### [cite_start]2.2 Esquema de Base de Datos (Las 2 Tablas) [cite: 71]

Para este prototipo, utilizaremos dos estructuras de datos principales (pueden ser colecciones en Firebase o tablas SQL).

#### Tabla A: `Beneficiarios` (Lectura / Read-Only para el Agente)
*Esta tabla contiene la "verdad" sobre el estudiante.*

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `dni` | String (PK) | Identificador único. |
| `nombre_completo` | String | Nombre del becario. |
| `estado` | String | 'ACTIVO', 'OBSERVADO', 'EGRESADO'. |
| `carrera_actual` | String | Ej. 'Ingeniería de Sistemas'. |
| `institucion` | String | Ej. 'Universidad Nacional de Ingeniería'. |
| `promedio_ponderado`| Float | Dato extra para evaluar rendimiento (opcional). |

#### Tabla B: `Solicitudes_Tramite` (Escritura / Write)
*Esta tabla almacena las acciones que el agente propone y el humano aprueba.*

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id_solicitud` | UUID | Generado automáticamente. |
| `dni_becario` | String (FK) | DNI del solicitante. |
| `tipo_tramite` | String | 'CAMBIO_CARRERA'. |
| `carrera_destino` | String | La carrera a la que se quiere cambiar. |
| `justificacion_ia` | String | Resumen del análisis de afinidad hecho por el LLM. |
| `fecha_solicitud` | Timestamp | Fecha del registro. |
| `estado_tramite` | String | 'PENDIENTE_APROBACION_COMITE'. |

---

## [cite_start]3. Definición de Schemas para el Agente (Pydantic) [cite: 26, 27]

Estos esquemas definen estrictamente cómo el LLM debe comunicarse con el backend.

#### Input Schema (Lo que el agente necesita extraer del texto)
```json
{
  "dni": "string (Extraído del correo o buscado por nombre)",
  "intencion": "string (Debe ser 'CAMBIO_CARRERA')",
  "carrera_deseada": "string"
}

```

Output Schema (Tool Definition: `registrar_solicitud`) 

Este es el JSON exacto que el agente debe generar para proponer la acción.

```python
class RegistrarSolicitud(BaseModel):
    dni: str = Field(..., description="DNI del becario validado en la base de datos")
    carrera_destino: str = Field(..., description="Nombre oficial de la carrera a la que se desea cambiar")
    analisis_afinidad: str = Field(..., description="Breve justificación de por qué las carreras son afines")
    es_alumno_activo: bool = Field(..., description="Confirmación de que el status en BD es ACTIVO")

```

---

4. Estrategia de Implementación HITL (Frontend) 

La interfaz en Streamlit gestionará el estado de la sesión para guiar al operador humano.

4.1 Estados de la Sesión (`st.session_state`) 

1. **`ESPERANDO_INPUT`**: El chat está activo, esperando el correo del becario.
2. **`PROCESANDO`**: El agente está consultando la Tabla A y razonando.
3. **`REVISANDO_BORRADOR`**: El agente ha propuesto una acción (JSON). Se bloquea el chat y se muestra el panel de validación.
4. **`ACCION_CONFIRMADA`**: El humano aprobó. Se muestra el ID de la solicitud creada en la Tabla B.

4.2 Componentes Visuales de Validación ("La Interfaz de la Verdad") 

El panel de aprobación debe mostrar lado a lado:

* **Datos del Agente (Propuesta):** "Cambio a Ingeniería de Software".
* **Datos de la BD (Realidad):** "Alumno: Juan Perez, Estado: ACTIVO, Carrera Actual: Ing. Sistemas".
* **Advertencias:** Si el estado no es ACTIVO, el sistema debe resaltar esto en rojo, aunque el LLM diga que proceda.

---

## 5. Requerimientos Funcionales para "Antigravity" (Desarrollo)

Para iniciar el desarrollo, se requiere configurar:

1. **Backend (FastAPI):**
* Endpoint `/chat`: Manejo de historial y llamadas a OpenAI/LangChain.


* Dummy DB / Firebase: Cargar datos semilla ("Seed Data") en la Tabla A para pruebas.




2. **Tools:**
* Implementar `tool_consultar_becario` (lectura directa).
* Implementar `tool_proponer_tramite` (retorna el payload, no escribe).


3. **Endpoint de Ejecución:**
* Endpoint `/aprobar_tramite`: Este es el único que tiene permiso de escritura (`INSERT`) en la Tabla B.




