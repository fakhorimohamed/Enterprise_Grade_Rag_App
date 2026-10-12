import logfire 
from app.agents.state import AgentState
from app.Gateway.client import PortkeyClient 
from app.prompts.planner_prompt import get_planner_prompt



portkey_client = PortkeyClient()

llm = portkey_client.get_langchain_llm(feature ="planner") 


def planner_node (state: AgentState) -> dict:
    """
    Generates a plan for the agent to follow based on the current query and context.
    """
    history = "" 
    for msg in state["messages"][:-1] : 
        role = "User" if msg["role"] == "user" else "Assistant"
        history += f"{role}: {msg['content']}\n"
    
    user_message = state["messages"][:-1]["content"] if state["messages"] else "" 

    prompt = get_planner_prompt(query=user_message , context=history)

    with logfire.span("Planner Decision") : 
        decision = llm.invoke(prompt).content.strip()
        logfire.info(f"Planner decision: {decision}")

        if decision == "CONVERSATIONAL" :
             return {
                "current_query": "CONVERSATIONAL",
                "status": "Handling conversationally (using memory)...",
                "plan": ["Intent: Conversational/Memory", "Retrieval: Skipped"],
                }
        
        return {
            "current_query": decision,
            "status": f"Technical research needed. Searching for: {decision}",
            "plan": ["Intent: Technical", f"Search Term: {decision}"],
    }
