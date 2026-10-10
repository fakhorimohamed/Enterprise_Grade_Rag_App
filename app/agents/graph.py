import logfire 
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import START , END , StateGraph
from app.agents.state import AgentState

from app.agents.nodes.planner import planner_node
from app.agents.nodes.responder import responder_node
from app.agents.nodes.retrieve_agent import retrieve_node 


class Graph :
    def __init__(self):
        self._graph  :StateGraph |None =None
        self._checkpointer = BaseCheckpointSaver |None =None 


    def build_graph (self)-> StateGraph :
        """
        Build and compile the LangGraph RAG agent.
        Args :
            checkpointer: Optional checkpointer. If None, a Postgres-backed
            checkpointer is created. Pass a MemorySaver in tests.
        """
        if self._graph is not None :
            return self._graph 

        workflow =StateGraph(AgentState) 
        workflow.add_node ("planner" , planner_node) 
        workflow.add_node("responder" , responder_node)
        workflow.add_node()

