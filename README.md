# Enterprise Agentic RAG

A scalable, production-oriented **Agentic Retrieval-Augmented Generation (RAG)** system built with LangGraph, designed to provide accurate, context-aware answers while ensuring security, observability, and reliability.

The system combines multi-step agentic reasoning, semantic retrieval, document reranking, and security guardrails to distinguish relevant information from noisy or irrelevant data.

## Features

* **Agentic Workflow:** LangGraph orchestrates multi-step reasoning, query planning, and conversational memory.
* **Security Guardrails:** NVIDIA NeMo Guardrails protects against prompt injection, jailbreak attempts, and off-topic queries.
* **LLM Gateway:** Portkey manages LLM requests and supports automatic fallback between OpenAI and Anthropic.
* **Vector Database:** Qdrant Cloud provides scalable vector storage and semantic retrieval.
* **Semantic Reranking:** Jina AI Reranker improves retrieval relevance by reordering retrieved documents.
* **Embeddings:** Jina AI `jina-embeddings-v3` generates 1024-dimensional embeddings, with a local `mxbai-embed-large-v1` fallback.
* **Document Processing:** Local parsing of PDF, HTML, TXT, DOCX, and PPTX files without relying on external OCR services.
* **Observability:** Pydantic Logfire and LangSmith provide tracing and monitoring across agent workflows.
* **Metrics:** Prometheus exposes custom RAG and guardrails metrics through a `/metrics` endpoint.
* **REST API:** A synchronous `/query` endpoint executes the LangGraph pipeline and returns the generated answer.
* **Authentication:** Optional API key authentication and Redis-backed or in-memory rate limiting.
* **Evaluation:** RAGAS-based evaluation with six metrics, a Streamlit demo, and a headless evaluation script.

## Architecture

The system follows a modular architecture composed of the following components:

1. **Document Ingestion:** Loads and parses documents locally, preparing them for indexing.
2. **Embedding Generation:** Converts document chunks into vector representations using Jina AI or a local embedding model.
3. **Vector Storage:** Stores document embeddings and metadata in Qdrant Cloud.
4. **Query Processing:** Validates incoming queries through NeMo Guardrails before retrieval.
5. **Agentic Orchestration:** LangGraph coordinates query planning, retrieval, reranking, and answer generation.
6. **Semantic Retrieval:** Retrieves relevant documents from Qdrant and reranks them using Jina AI.
7. **Answer Generation:** Uses the configured LLM through Portkey to generate context-aware responses.
8. **Observability and Evaluation:** Tracks execution, collects metrics, and evaluates retrieval and generation quality.

## Technology Stack

| Component           | Technology                  |
| ------------------- | --------------------------- |
| Agent Orchestration | LangGraph                   |
| LLM Gateway         | Portkey                     |
| Language Models     | OpenAI, Anthropic           |
| Embeddings          | Jina AI, mxbai              |
| Reranking           | Jina AI Reranker            |
| Vector Database     | Qdrant Cloud                |
| Guardrails          | NVIDIA NeMo Guardrails      |
| API                 | FastAPI                     |
| Observability       | Pydantic Logfire, LangSmith |
| Metrics             | Prometheus                  |
| Evaluation          | RAGAS                       |
| Demo Interface      | Streamlit                   |
| Rate Limiting       | Redis                       |

## Project Structure

```text
enterprise-agentic-rag/
│
├── app/
│   ├── api/                 # FastAPI endpoints
│   ├── agents/              # LangGraph agents and workflows
│   ├── ingestion/           # Document loading and processing
│   ├── retrieval/           # Vector search and reranking
│   ├── guardrails/          # Input and output validation
│   ├── llm/                 # LLM gateway configuration
│   └── core/                # Application configuration
│
├── evals/                   # RAGAS evaluation scripts
│   └── run_evals.py
│
├── frontend/                # Streamlit demo application
│
├── tests/                   # Unit and integration tests
├── data/                    # Local document storage
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── README.md
```

*Note: The directory structure above is a suggested organization and should be adjusted to match the actual repository.*

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd enterprise-agentic-rag
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment:

**Windows**

```powershell
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a
