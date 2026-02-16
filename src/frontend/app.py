import streamlit as st
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import uuid
from src.frontend.api_client import send_chat, approve_request

st.set_page_config(page_title="Agente de Bienestar", layout="wide")

# Session State Initialization
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# HITL State Machine: ESPERANDO_INPUT -> REVISANDO_BORRADOR -> CONFIRMANDO_ACCION
if "hitl_state" not in st.session_state:
    st.session_state.hitl_state = "ESPERANDO_INPUT" 

if "approval_payload" not in st.session_state:
    st.session_state.approval_payload = None

st.title("🎓 Agente HITL para Gestión de Cambios de Carrera")

# Sidebar
with st.sidebar:
    st.header("Debug Info")
    st.write(f"Session ID: {st.session_state.thread_id}")
    st.write(f"State: `{st.session_state.hitl_state}`")
    
    if st.button("Reiniciar Sesión"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.hitl_state = "ESPERANDO_INPUT"
        st.session_state.approval_payload = None
        st.rerun()

# --- HITL Workflow Logic ---

# 1. ESTADO: REVISANDO_BORRADOR
if st.session_state.hitl_state == "REVISANDO_BORRADOR":
    st.info("📝 ESTADO: REVISIÓN DE BORRADOR (Agente Propone Trámite)")
    
    with st.container(border=True):
        st.subheader("Borrador de Solicitud")
        payload = st.session_state.approval_payload
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Datos Propuestos")
            st.json(payload)
        with col2:
            st.markdown("### Análisis del Agente")
            analysis = payload.get("justificacion_ia", payload.get("analisis_afinidad", "Sin análisis"))
            st.write(analysis)
            
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Continuar a Confirmación ➡️", type="primary", use_container_width=True):
                st.session_state.hitl_state = "CONFIRMANDO_ACCION"
                st.rerun()
        with c2:
            if st.button("❌ Descartar Borrador", type="secondary", use_container_width=True):
                st.session_state.hitl_state = "ESPERANDO_INPUT"
                st.session_state.approval_payload = None
                st.session_state.messages.append({"role": "assistant", "content": "❌ Borrador descartado."})
                st.rerun()

# 2. ESTADO: CONFIRMANDO_ACCION
elif st.session_state.hitl_state == "CONFIRMANDO_ACCION":
    st.warning("⚠️ ESTADO: CONFIRMACIÓN FINAL (Acción Irreversible)")
    
    with st.container(border=True):
        st.markdown("### ¿Estás seguro de registrar este cambio?")
        st.write("Esta acción escribirá permanentemente en la base de datos de Firestore.")
        
        # Resumen breve
        p = st.session_state.approval_payload
        
        st.markdown(f"**Alumno:** {p.get('dni')}")
        st.markdown(f"**Carrera Destino:** :blue-background[{p.get('carrera_destino')}]")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ SÍ, REGISTRAR EN BD", type="primary", use_container_width=True):
                with st.spinner("Escribiendo en Firestore..."):
                    res = approve_request(st.session_state.approval_payload, True)
                
                if res.get("status") == "APPROVED":
                    st.success(f"Solicitud Aprobada! ID: {res.get('solicitud_id')}")
                    st.session_state.messages.append({"role": "assistant", "content": f"✅ Solicitud aprobada y registrada con ID: {res.get('solicitud_id')}"})
                    st.session_state.hitl_state = "ESPERANDO_INPUT"
                    st.session_state.approval_payload = None
                    st.rerun()
                else:
                    st.error(f"Error: {res.get('message', 'Desconocido')}")
        
        with c2:
            if st.button("🔙 Volver a Revisión", use_container_width=True):
                st.session_state.hitl_state = "REVISANDO_BORRADOR"
                st.rerun()

# 3. ESTADO: ESPERANDO_INPUT (Chat)
else:
    # Chat Interface
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    if prompt := st.chat_input("Escribe tu consulta aquí..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process
        with st.spinner("El agente está pensando..."):
            response_data = send_chat(prompt, st.session_state.thread_id)
            
            if "error" in response_data:
                st.error(f"Error del sistema: {response_data['error']}")
            else:
                bot_msg = response_data.get("response", "")
                st.session_state.messages.append({"role": "assistant", "content": bot_msg})
                with st.chat_message("assistant"):
                    st.markdown(bot_msg)
                
                # Check for HITL trigger
                if response_data.get("approval_required"):
                    st.session_state.hitl_state = "REVISANDO_BORRADOR"
                    st.session_state.approval_payload = response_data.get("approval_payload")
                    st.rerun()
