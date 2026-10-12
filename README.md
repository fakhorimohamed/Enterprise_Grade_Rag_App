# Enterprise Agentic RAG (Scalable Pipeline)

A production-grade, enterprise-level RAG system built with **LangGraph**, **Portkey LLM Gateway**, **OpenAI**, and **Jina AI Embeddings/Reranker**. The system distinguishes between technical "True Data" and random "Noisy Data" using semantic re-ranking, history-aware planning, and NeMo Guardrails for input/output safety.

## Key Features

- **Agentic Intelligence**: LangGraph for cyclic reasoning, multi-step planning, and conversation memory.
- **Guardrails**: NeMo Guardrails gate blocks off-topic, jailbreak, and injection inputs before any retrieval.
- **LLM Gateway**: Portkey routes all LLM calls with automatic fallback between OpenAI and Anthropic via your configured Portkey virtual providers.
- **Enterprise Search**: Qdrant Cloud for high-performance vector search + Jina AI Reranker API for semantic reranking.
- **Jina AI Embeddings**: `jina-embeddings-v3` (1024-dim) via Jina API, with local `mxbai-embed-large-v1` fallback.
- **Local Document Parsing**: PDF, HTML, TXT, DOCX, PPTX parsed entirely on-device — no external OCR service.
- **Observability**: Full trace nesting with **Pydantic Logfire** and **LangSmith** across every agent node.
- **Metrics**: Prometheus `/metrics` endpoint with custom RAG and guardrails counters.
- **Synchronous `/query`**: The LangGraph pipeline runs directly inside the `/query` endpoint and returns the final answer.
- **API Key & Rate Limiting**: Optional bearer-token auth and Redis-backed (or in-memory) rate limiting.
- **Evaluation Suite**: RAGAS-powered eval pipeline (6 metrics) with a dedicated Streamlit demo app and a headless `evals/run_evals.py` script.

---

## Agent Intelligence Flow

```mermaid
graph TD
    User((User)) --> UI[Streamlit UI]
    UI --> API[FastAPI /query]
    API --> Guard{NeMo Guardrails}
    Guard -->|Blocked| UI
    Guard -->|Pass| Planner{Planner Node}
    Planner -->|Conversational| Responder[Responder Node]
    Planner -->|Technical| Retriever[Retriever Node]
    Retriever --> Reranker[Jina AI Reranker API]
    Reranker --> Responder
    Responder --> UI
    Responder -.-> Memory[(LangGraph MemorySaver)]
```

---

## Project Structure

```text
Enterprise_Grade_Rag_App/
├── app/
│   ├── agents/
│   │   ├── nodes/       # Planner, Retriever, Responder LangGraph nodes
│   │   ├── __init__.py
│   │   ├── graph.py     # LangGraph workflow definition
│   │   └── state.py     # Shared agent state schema
│   ├── configs/         # Configuration files
│   ├── core/            # Core application logic
│   ├── gateway/         # Portkey LLM gateway — primary + fallback routing
│   ├── guardrails/      # NeMo Guardrails input/output filtering
│   ├── ingestion/       # Local parsers (PDF, HTML, TXT, DOCX, PPTX) + chunking
│   ├── prompts/         # Prompt templates
│   ├── services/        # Jina AI embeddings + Qdrant search + Jina AI reranking
│   └── __init__.py
├── DATA/                # Sample datasets (True vs Noisy documentation)
├── evals/               # RAGAS evaluation suite + Streamlit 3-tab demo
├── notebook/            # Experiments and exploration notebooks
├── processed_data/      # Auto-generated — parsed & chunked JSON output per document
├── scripts/             # Utility scripts
├── tests/               # Unit tests
├── .env                 # Environment variables (not committed)
├── .gitignore
├── pyproject.toml       # Project metadata and dependencies (uv)
├── README.md
├── requirements.txt     # Pinned dependencies
└── uv.lock              # uv lockfile
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Orchestration | LangChain + LangGraph |
| LLMs | OpenAI `gpt-5-mini` + Anthropic fallback via **Portkey** gateway |
| Guardrails | NeMo Guardrails |
| Vector DB | Qdrant Cloud |
| Reranking | Jina AI Reranker API (`jina-reranker-v3`) |
| Embeddings | Jina AI `jina-embeddings-v3` (1024-dim) + local mxbai fallback |
| Document Parsing | pypdf + pdfplumber (local, no OCR service) |
| Observability | Pydantic Logfire + LangSmith |
| Evaluation | RAGAS + custom Tool Correctness (Jaccard) |

---

## Getting Started

### 1. Install dependencies

```powershell
uv python -m venv tenvv
.\tenvv\Scripts\activate
 uv add -r requirements.txt
```

### 2. Configure environment

Create a `.env` file with the following keys:

```env
# Gemini LLM
Gemini_API_KEY = "..."

# LLM Gateway
PORTKEY_API_KEY = "..."

# Jina AI Embeddings + Reranker API
JINA_API_KEY = "..."

# Vector DB
QDRANT_API_KEY = "..."
QDRANT_CLUSTER_ENDPOINT = "https://your-cluster.cloud.qdrant.io:6333"

# Production persistence (Neon) & cache (Upstash Redis)
NEON_DB_URL = "postgresql://user:password@host.neon.tech/enterprise_rag?sslmode=require"
UPSTASH_REDIS_REST_URL = "https://your-db.upstash.io"
UPSTASH_REDIS_REST_TOKEN = "your-upstash-token"

# API safety
RAG_API_KEY = ""                       # set in production to require bearer auth
RATE_LIMIT_PER_MINUTE = 20

# Observability
LOGFIRE_TOKEN = "..."
LANGSMITH_API_KEY = "..."
LANGSMITH_PROJECT = "enterprise_rag"
LANGSMITH_TRACING = true
LANGSMITH_ENDPOINT = https://api.smith.langchain.com



```

### 3. Run data ingestion

Parses all documents in `DATA/`, chunks them, saves metadata to `processed_data/`, and indexes vectors into Qdrant.

```powershell
python -m app.ingestion.processor DATA/true_data --wipe
```

> Pass `--wipe` to drop and recreate the Qdrant collection. Omit it to append to an existing collection.

# Terminal 2 — Streamlit UI
streamlit run ui/app.py
```



*Built for High-Scale Enterprise Document Intelligence.*
