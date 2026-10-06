import logfire

from app.services.retrieval.qdrant_service import retrieve_service 
from app.services.retrieval.ranking_service import rerank_service 
from app.agents.state import AgentState 


def retrieve_node (state: AgentState) ->dict:
    """
    Performs vector search and semantic reranking for technical queries.
    
    """

    query = state["current_query"] 

    with logfire.span ("Knowledge Retrieval") :
        logfire.info(f"Searching Qdrant for: {query}")
        raw_docs = retrieve_service.search_enterprise_knowledge(query=query , limit=15) 
        logfire.info(f"Retrieved {len(raw_docs)} candidates from Vector DB")

        doc_contents =[ doc["content"] for doc in raw_docs ]

        with logfire.span("Semantic Reranking") :
            reranked_contents = rerank_service.rank(query=query , documents=doc_contents , top_n=5) 
            logfire.info("Reranking complete. Kept top 5 most relevant chunks.")

        formatted_docs =[f"content : {doc}" for doc in  reranked_contents ]
    return {
        "documents" : formatted_docs , 
        "status"  : "Found technical context.",
        "plan"    : state["plan"] + ["Context Retrieved"]
    }