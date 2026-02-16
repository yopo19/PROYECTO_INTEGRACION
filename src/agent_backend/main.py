import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import uvicorn
from fastapi import FastAPI
from src.agent_backend.infrastructure.adapters.input.api import router

app = FastAPI(title="Agente HITL - Cambio de Carrera")

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("src.agent_backend.main:app", host="0.0.0.0", port=8000, reload=True)
