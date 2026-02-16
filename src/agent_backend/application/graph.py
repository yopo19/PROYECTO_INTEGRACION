from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from src.agent_backend.domain.state import AgentState
from src.agent_backend.application.nodes import agent_node, tools

def should_continue(state: AgentState) -> Literal["tools", END]:
    messages = state['messages']
    last_message = messages[-1]
    if not last_message.tool_calls:
        return END
    return "tools"

# Workflow Definition
workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

# Edges
workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
)

workflow.add_edge("tools", "agent")

# Persistence
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

# Compile
app = workflow.compile(checkpointer=checkpointer)
