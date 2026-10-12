import textwrap

def get_planner_prompt(query: str, context: str) -> str:
    """
    Determines if the user's query is conversational or requires technical retrieval.
    """
    return textwrap.dedent(f"""
        You are an intelligent Assistant Planner.
        Analyze the conversation history and the latest user message.

        CONVERSATION HISTORY:
        {context.strip() or "No previous history."}

        LATEST MESSAGE:
        "{query}"

        Task:
        1. If the latest message is a greeting (hi, hello) or a question that can be answered using ONLY the conversation history above (e.g., "what is my name"), respond with EXACTLY: 'CONVERSATIONAL'.
        2. If it is a technical question about Kubernetes, Intel, or Networking that requires fresh documentation, output a refined, concise search query.

        Output ONLY 'CONVERSATIONAL' or the refined search query. Do not add any other text.
    """).strip()


def get_technical_responder_prompt(query: str, tech_context: str, conver_context: str) -> str:
    """
    Generates the final technical answer using retrieved documents and chat history.
    (Note: Renamed from 'retriever_prompt' because it generates an answer, it doesn't search).
    """
    return textwrap.dedent(f"""
        You are a Senior Technical Architect and Enterprise AI Assistant.
        Answer the user's question using ONLY the TECHNICAL CONTEXT provided.

        TECHNICAL CONTEXT:
        {tech_context.strip() or "No technical context provided."}

        CONVERSATION HISTORY:
        {conver_context.strip() or "No previous history."}

        USER QUESTION:
        "{query}"

        Rules:
        1. Provide a clear, step-by-step, professional response based strictly on the context.
        2. If the context does NOT contain the answer, politely state: "I'm sorry, but I don't have enough information in my current documentation to answer that. Please contact human support."
        3. Do not hallucinate or make up information.
    """).strip()


def get_conversational_responder_prompt(query: str, conver_context: str) -> str:
    """
    Generates a friendly response for non-technical, conversational queries.
    """
    return textwrap.dedent(f"""
        You are a friendly and helpful Enterprise AI Assistant.
        Answer the user's latest message naturally using the CONVERSATION HISTORY below.

        CONVERSATION HISTORY:
        {conver_context.strip() or "No previous history."}

        LATEST MESSAGE:
        "{query}"

        Rules:
        1. Keep the response warm, professional, and concise.
        2. Do not attempt to search for technical documentation unless explicitly asked.
    """).strip()