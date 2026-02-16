# 🧪 Plan de Pruebas de Aceptación

**Elaborado por:** Juan Montoro

Este documento detalla los 3 casos de uso principales para validar el correcto funcionamiento del Agente HITL.

---

## Caso 1: Solicitud Exitosa (Happy Path)
**Objetivo:** Verificar que una solicitud válida activa el flujo HITL y permite el registro en base de datos.

| Paso | Acción / Input | Resultado Esperado |
| :--- | :--- | :--- |
| 1 | **Analista ingresa:**<br>*"El alumno Juan Perez (DNI: 12345678) desea cambiarse de Ing. Sistemas a Ing. de Software porque quiere especializarse en desarrollo backend."* | El sistema procesa la solicitud ("Energy" / Spinner activo). |
| 2 | **Agente (Backend):** | 1. Consulta Firestore y confirma estado `ACTIVO`.<br>2. Valida afinidad (Sistemas -> Software: ✅).<br>3. Genera propuesta JSON. |
| 3 | **Interfaz (Frontend):** | **Bloquea el chat** y muestra el Panel de Aprobación con:<br>- Datos del alumno.<br>- Análisis de afinidad.<br>- Botones Aprobar/Rechazar. |
| 4 | **Analista confirma:**<br>Clic en "✅ Aprobar". | 1. El sistema muestra mensaje de éxito con ID de transacción.<br>2. Se crea un registro en la colección `solicitudes_tramite` de Firestore. |

---

## Caso 2: Rechazo Automático por Estado (Regla de Negocio)
**Objetivo:** Verificar que el agente bloquea solicitudes de alumnos no aptos (Egresados/Observados) sin molestar al humano.

| Paso | Acción / Input | Resultado Esperado |
| :--- | :--- | :--- |
| 1 | **Analista ingresa:**<br>*"Solicitud de cambio de carrera para la alumna Maria Lopez, DNI 87654321."* | El sistema procesa la solicitud. |
| 2 | **Agente (Backend):** | 1. Consulta Firestore y detecta estado `EGRESADO` o `OBSERVADO`.<br>2. **Detiene el flujo.** No llama a la herramienta de propuesta. |
| 3 | **Interfaz (Frontend):** | El chat **NO** se bloquea. El agente responde: *"Lo siento, la alumna Maria Lopez tiene el estado EGRESADO, por lo cual no aplica para cambio de carrera según el reglamento."* |

---

## Caso 3: Rechazo por Falta de Afinidad o Justificación (IA)
**Objetivo:** Verificar la capacidad de razonamiento del LLM para filtrar solicitudes sin sustento académico.

| Paso | Acción / Input | Resultado Esperado |
| :--- | :--- | :--- |
| 1 | **Analista ingresa:**<br>*"El alumno Juan Perez (DNI: 12345678) quiere cambiarse a Gastronomía porque le gusta cocinar."* | El sistema procesa la solicitud. |
| 2 | **Agente (Backend):** | 1. Confirma estado `ACTIVO`.<br>2. Evalúa Afinidad: Ing. Sistemas vs Gastronomía -> ❌ **No afín**.<br>3. Evalúa Justificación: "Le gusta cocinar" -> ❌ **Insuficiente para cambio académico**. |
| 3 | **Interfaz (Frontend):** | El chat **NO** se bloquea. El agente responde explicando el rechazo:<br>*"La solicitud no procede. La carrera de destino (Gastronomía) no es afín a la actual (Ing. Sistemas) y la justificación presentada no cumple con los criterios académicos requeridos."* |
