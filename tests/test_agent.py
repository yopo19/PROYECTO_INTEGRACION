import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent_backend.application.graph import app
from src.agent_backend.infrastructure.repositories.mock_db import SEED_BECARIOS
import json

def test_happy_path():
    print("--- Testing Happy Path (Juan Perez - ACTIVO) ---")
    dni = "12345678" # Juan Perez (ACTIVO in seed)
    input_msg = f"Hola, deseo cambiarme de carrera a Arquitectura. Mi DNI es {dni}."
    
    print(f"User Input: {input_msg}")
    
    config = {"configurable": {"thread_id": "test-thread-1"}}
    
    # First turn
    result = app.invoke({"messages": [("user", input_msg)]}, config=config)
    
    last_msg = result['messages'][-1]
    print(f"Agent Response: {last_msg.content}")
    
    # Check if tool was called
    tool_calls = [m for m in result['messages'] if hasattr(m, 'tool_calls') and m.tool_calls]
    if tool_calls:
        print(f"Tool Calls detected: {len(tool_calls)}")
        for tc in tool_calls:
            for call in tc.tool_calls:
                print(f"  - {call['name']}: {call['args']}")

if __name__ == "__main__":
    test_happy_path()
