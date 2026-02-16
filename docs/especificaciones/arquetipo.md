Documentación de Referencia: Estructura de Proyecto con Arquitectura Hexagonal
Este documento describe la estructura de directorios y los principios de diseño aplicados en el servicio de Orquestador, sirviendo como guía base para la implementación de microservicios bajo el patrón de Arquitectura Hexagonal (Puertos y Adaptadores).

1. Objetivo de la Arquitectura
El objetivo principal es desacoplar la lógica de negocio (Dominio y Aplicación) de los detalles técnicos y servicios externos (Infraestructura). Esto permite:

Testabilidad: Probar la lógica de negocio sin depender de bases de datos o APIs externas.
Mantenibilidad: Cambiar tecnologías (e.g., cambiar de base de datos o proveedor de LLM) sin afectar las reglas de negocio.
Independencia: El núcleo del sistema no depende de frameworks o librerías externas.
2. Estructura de Directorios Estándar
La estructura se divide en tres capas principales dentro de src/: Domain, Application, e Infrastructure.

service_name/
├── src/
│   ├── domain/                 # CAPA 1: El Núcleo (Pura lógica de negocio, sin dependencias externas)
│   │   ├── models.py           # Entidades y objetos de valor del dominio
│   │   ├── state.py            # Definición de estados (ej. AgentState)
│   │   └── ports/              # Interfaces (contratos) que deben cumplir los adaptadores
│   │       └── llm_service.py  # Ejemplo: Interfaz para servicio de LLM
│   │
│   ├── application/            # CAPA 2: Casos de Uso (Orquestación del dominio)
│   │   ├── engine.py           # Lógica principal de flujos/workflows (Orquestador)
│   │   ├── workflow_services.py# Servicios de aplicación específicos
│   │   └── prompts/            # Gestión de prompts y plantillas
│   │
│   └── infrastructure/         # CAPA 3: El Mundo Exterior (Implementaciones concretas)
│       ├── adapters/           # Adaptadores que implementan los puertos o exponen la app
│       │   ├── input/          # DRIVING ADAPTERS (Entrada: API, CLI, Event Consumers)
│       │   │   ├── api.py      # Rutas FastAPI / Controladores
│       │   │   └── schemas.py  # DTOs para la API
│       │   │
│       │   └── output/         # DRIVEN ADAPTERS (Salida: DB, APIs externas, LLMs)
│       │       ├── persistence.py    # Implementación de repositorios (DB)
│       │       ├── tools.py          # Herramientas para el agente
│       │       ├── reranker.py       # Cliente para servicio de Rerank
│       │       ├── pdf_generator.py  # Generación de documentos
│       │       └── profile_service.py# Cliente de API de perfil de usuario
│       │
│       ├── config/             # Configuración y variables de entorno
│       └── container.py        # Inyección de Dependencias (DI Container)
│
├── tests/                      # Tests unitarios e integración
├── .env                        # Variables de entorno locales
├── Dockerfile                  # Definición de imagen del servicio
└── pyproject.toml / requirements.txt # Gestión de dependencias
3. Descripción de las Capas
🟢 Capa de Dominio (src/domain)
Es el corazón del software. Contiene las reglas de negocio fundamentales.

Regla de Oro: NO puede importar nada de application ni de infrastructure. No debe haber referencias a bases de datos, frameworks (FastAPI) o librerías específicas de terceros (OpenAI SDK).
Componentes:
models.py
: Clases de datos (Dataclasses, Pydantic models puros) que representan conceptos del negocio.
ports/: Clases abstractas o Protocolos que definen qué necesita el dominio hacer (ej. save_user, generate_text), sin definir cómo.
🟡 Capa de Aplicación (src/application)
Contiene los Casos de Uso del sistema. Orquesta las entidades del dominio para cumplir una tarea específica.

Dependencias: Puede importar de domain. No debe importar de infrastructure (excepto interfaces puras si es estrictamente necesario, pero idealmente solo usa las abstracciones del dominio).
Componentes:
engine.py
 / services: Implementan la lógica de los flujos. Reciben las implementaciones de los puertos a través de Inyección de Dependencias.
prompts/: Los textos y plantillas usados por la lógica de aplicación.
🔴 Capa de Infraestructura (src/infrastructure)
Contiene los detalles técnicos y la "suciedad" del mundo real.

Componentes:
Adapters Input (Driving): Quien conduce la aplicación (ej. un usuario vía API REST). 
api.py
 traduce peticiones HTTP a llamadas a la capa de Aplicación.
Adapters Output (Driven): A quien la aplicación conduce. Implementaciones concretas de los puertos definidos en el dominio (ej. PostgresRepository, OpenAILLMService).
Container (
container.py
): El punto de composición. Aquí se "cablean" las dependencias, inyectando los adaptadores concretos (
persistence.py
) en los servicios de aplicación (
engine.py
).
4. Flujo de Control vs. Flujo de Dependencias
Flujo de Control: API (Infra) -> Application Case -> Domain -> Database Adapter (Infra).
Flujo de Dependencias: Todo apunta hacia adentro.
Infraestructura depende de Aplicación y Dominio.
Aplicación depende de Dominio.
Dominio no depende de nadie.
Esta inversión de dependencias se logra mediante los Puertos (Interfaces) definidos en el Dominio e implementados en la Infraestructura.

Generado por Antigravity - Referencia de Arquitectura