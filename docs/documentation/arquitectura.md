# 🏗️ Arquitectura Técnica del Sistema

**Elaborado por:** Juan Montoro

---

### Nivel 1: Contexto del Sistema
Diagrama de alto nivel que muestra cómo el sistema interactúa con sus usuarios y sistemas externos.

```mermaid
flowchart TB
    %% Nivel 1: Contexto
    Analista("👤 Analista de Bienestar<br/><small>Ingresa solicitudes y gestiona aprobaciones</small>")
    
    subgraph Sistema["🏢 Sistema Agente HITL"]
        Agente("⚙️ Agente de Gestión de Cambios<br/><small>Orquesta validación y análisis</small>")
    end

    OpenAI("🧠 OpenAI GPT-4<br/><small>Razonamiento</small>")
    Firestore("🗄️ Google Firestore<br/><small>Persistencia</small>")

    Analista -->|1. Ingresa Solic. / Valida| Agente
    Agente -->|2. Consulta| OpenAI
    Agente -->|3. Lee/Escribe| Firestore
    
    classDef person fill:#08427b,color:#fff,stroke:#052e56;
    classDef system fill:#1168bd,color:#fff,stroke:#0b4884;
    classDef ext fill:#999999,color:#fff,stroke:#666;
    
    class Analista person;
    class Agente system;
    class OpenAI,Firestore ext;
```

### Nivel 2: Contenedores
Desglose de los componentes desplegables y sus interacciones.

```mermaid
flowchart TB
    %% Nivel 2: Contenedores
    Analista("👤 Analista<br/><small>Operador</small>")

    subgraph Sistema["🏢 Sistema Agente HITL"]
        direction TB
        Frontend("🖥️ Frontend App<br/><small>Streamlit (Python)</small>")
        Backend("🔌 API Gateway<br/><small>FastAPI (Python)</small>")
        Engine("⚙️ Agent Engine<br/><small>LangGraph</small>")
        DB[("🗄️ Base de Datos<br/><small>Firestore</small>")]
    end

    Analista -->|Usa| Frontend
    Frontend -->|HTTPS/JSON| Backend
    Backend -->|Invoca| Engine
    Engine -->|Lee/Escribe| DB

    classDef person fill:#08427b,color:#fff,stroke:#052e56;
    classDef container fill:#23a2f0,color:#fff,stroke:#1071a9;
    classDef db fill:#23a2f0,color:#fff,stroke:#1071a9; # Same basic color for containers
    
    class Analista person;
    class Frontend,Backend,Engine container;
    class DB db;
```

## 2. Detalle de Componentes (Nivel 2)

| Componente | Tecnología | Responsabilidad Principal |
| :--- | :--- | :--- |
| **Frontend App** | Streamlit | Proveer una interfaz unificada. Gestiona el estado de la sesión (`approval_required`) para bloquear el chat cuando se requiere intervención humana. |
| **API Backend** | FastAPI | Punto de entrada. Maneja las rutas `/chat` (interacción) y `/aprobar` (ejecución de escritura). Intercepta la intención de escritura del agente. |
| **Agent Engine** | LangGraph | Core lógico. Define el grafo de estados: `Agent` -> `Tools` -> `Agent`. Decide cuándo llamar a herramientas. |
| **Persistence** | Firestore | Persistencia de datos. Colecciones: `beneficiarios` (lectura) y `solicitudes_tramite` (escritura). |

---

## 3. Flujos de Interacción (Diagramas de Secuencia)

### Escenario A: Interacción Exitosa (HITL Activado)
El analista ingresa una solicitud válida en nombre del becario y luego la aprueba.

```mermaid
sequenceDiagram
    actor Analista
    participant FE as Frontend (Streamlit)
    participant BE as Backend (FastAPI)
    participant AG as Agent (LangGraph/LLM)
    participant DB as Firestore

    Analista->>FE: Ingresa: "El alumno Juan Perez (DNI: 12345678) desea cambio a Arquitectura"
    FE->>BE: POST /chat {message, thread_id}
    BE->>AG: Invoke Graph
    AG->>AG: Analizar Intención y DNI
    AG->>DB: Consultar Estado (tools.consultar_becario)
    DB-->>AG: {estado: "ACTIVO", carrera: "Ing. Sistemas"}
    AG->>AG: Validar Afinidad (OK)
    AG-->>BE: Tool Call: proponer_tramite(payload)
    
    Note over BE: INTERCEPCIÓN HITL
    BE-->>FE: Response {approval_required: true, payload: {...}}
    
    FE->>FE: Bloquear Chat / Mostrar Panel
    FE->>Analista: Mostrar Datos vs Propuesta para Validación
    Analista->>FE: Click "✅ Aprobar"
    
    FE->>BE: POST /aprobar {approved: true, payload}
    BE->>DB: INSERT into solicitudes_tramite
    DB-->>BE: Success (ID)
    BE-->>FE: {status: "APPROVED", id: "..."}
    
    FE-->>Analista: "Solicitud registrada con éxito. Notificar al alumno."
```

### Escenario B: Interacción Fallida (Validación Automática)
El analista ingresa una solicitud de un alumno no apto. El sistema rechaza automáticamente.

```mermaid
sequenceDiagram
    actor Analista
    participant FE as Frontend
    participant BE as Backend
    participant AG as Agent
    participant DB as Firestore

    Analista->>FE: Ingresa: "Solicitud de cambio para DNI: 87654321"
    FE->>BE: POST /chat
    BE->>AG: Invoke
    AG->>DB: Consultar Estado
    DB-->>AG: {estado: "EGRESADO"}
    
    Note over AG: Regla de Negocio: Solo Activos
    AG-->>BE: Response "El alumno no puede tramitar cambios siendo EGRESADO."
    BE-->>FE: Response {approval_required: false}
    FE-->>Analista: Muestra mensaje de rechazo (No se genera trámite)
```

---

## 4. Detalles del Agente y HITL

### Herramientas del Agente
El agente tiene acceso estricto a las siguientes herramientas (Tools):

1.  **`consultar_estado_becario(dni: str)`**
    *   **Propósito:** Lectura (Safe).
    *   **Cuándo se usa:** Siempre que se identifica un DNI en la solicitud.
    *   **Retorno:** Objeto JSON con estado, carrera actual, institución, etc.

2.  **`proponer_tramite(solicitud: Schema)`**
    *   **Propósito:** Escritura (Unsafe / Requires Approval).
    *   **Cuándo se usa:** Solo si el estado es `ACTIVO` y el análisis de afinidad es positivo.
    *   **Comportamiento:** No escribe en BD. Retorna un payload estructurado que el Backend intercepta.

### Activación del Human-in-the-Loop (HITL)
El mecanismo HITL no es una "herramienta" que el LLM decida usar para "pedir ayuda", sino una **regla de arquitectura**:
*   El Agente **NUNCA** tiene permiso de escritura directa en la base de datos de solicitudes.
*   Cualquier intento del Agente de ejecutar una acción de "escritura" (`proponer_tramite`) es detectado por el Backend.
*   El Backend detiene el flujo automático y delega la ejecución final a la API de `/aprobar`, que solo es invocada por el humano.

### Guía de Interpretación: Pantalla de Aprobación
Cuando el sistema activa el modo HITL, verás el siguiente panel:

| Sección | Descripción | Qué buscar |
| :--- | :--- | :--- |
| **Datos de la Solicitud (JSON)** | Información cruda que se guardará en BD. | Verifica que el DNI y la Carrera Destino sean correctos. |
| **Análisis del Agente** | Justificación generada por la IA sobre la afinidad. | Lee el razonamiento. ¿Tiene sentido el cambio pedagógicamente? |
| **Botones de Acción** | Controles de decisión. | **Aprobar:** Escribe en BD y notifica al alumno.<br>**Rechazar:** Cancela el flujo y el agente informa al alumno. |
