# RAG Financial Research Agent

A Retrieval-Augmented Generation (RAG) agent for OpenBB Workspace that indexes
financial documents (SEC filings, earnings transcripts, research reports) and
combines retrieved context with live OpenBB widget data to answer complex
financial research questions.

## Features

- 📚 Index and search SEC filings (10-K, 10-Q, 8-K) via SEC EDGAR
- 🎙️ Index earnings call transcripts
- 📄 Index PDF research reports
- 🔍 Semantic search with vector embeddings via ChromaDB
- 📊 Combine document context with live OpenBB widget data
- 📝 Automatic source citations with relevance scores
- ⚡ Streaming responses with reasoning steps
- 🤖 **Multi-LLM support** (OpenAI, Ollama, Azure, and more)

## How It Works

### RAG Pipeline

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Embed Query     │───▶│  Vector Search  │
│                 │    │  (OpenAI/Ollama) │    │  (ChromaDB)     │
└─────────────────┘    └──────────────────┘    └────────┬────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Stream Response│◀───│  Generate Answer │◀───│ Retrieved Docs  │
│  + Citations    │    │  (LLM)           │    │ + Widget Data   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

1. **Query Embedding**: User question is converted to a vector using the embedding model
2. **Semantic Search**: ChromaDB finds the most relevant document chunks
3. **Context Assembly**: Retrieved documents + live widget data are combined
4. **LLM Generation**: The LLM generates an answer grounded in the retrieved context
5. **Citation**: Sources are automatically cited with relevance scores

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      OpenBB Workspace                            │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐   │
│  │  User Query   │───▶│  RAG Agent    │◀──▶│ Widget Data   │   │
│  └───────────────┘    └───────────────┘    └───────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG Agent Server                            │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐   │
│  │ FastAPI       │    │ Vector Store  │    │ LLM           │   │
│  │ Endpoints     │───▶│ (ChromaDB)    │───▶│ (OpenAI/      │   │
│  │               │    │               │    │  Ollama/etc)  │   │
│  └───────────────┘    └───────────────┘    └───────────────┘   │
│          │                    ▲                                  │
│          │            ┌───────┴───────┐                         │
│          │            │  Embeddings   │                         │
│          │            │  (OpenAI/     │                         │
│          │            │   Ollama)     │                         │
│          │            └───────────────┘                         │
│          ▼                                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Document Ingestion                      │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │  │
│  │  │ SEC     │  │Earnings │  │Research │  │ Custom  │      │  │
│  │  │ Filings │  │Transcr. │  │ Reports │  │ Docs    │      │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## LLM Provider Support

The agent uses the **OpenAI SDK with configurable `base_url`**, supporting any OpenAI-compatible API:

| Provider | LLM | Embeddings | Configuration |
|----------|-----|------------|---------------|
| **OpenAI** | ✅ GPT-4o, GPT-4 | ✅ text-embedding-3-* | Default |
| **Ollama** | ✅ Llama, Qwen, Mistral | ✅ nomic-embed-text | `OPENAI_BASE_URL=http://localhost:11434/v1` |
| **Azure OpenAI** | ✅ | ✅ | Custom base_url + API key |
| **Together AI** | ✅ Llama, Mixtral | ✅ | `base_url=https://api.together.xyz/v1` |
| **Groq** | ✅ Llama 3 (fast) | ❌ | `base_url=https://api.groq.com/openai/v1` |
| **Fireworks AI** | ✅ | ✅ | `base_url=https://api.fireworks.ai/inference/v1` |
| **vLLM** | ✅ Any HF model | ✅ | Self-hosted |
| **LM Studio** | ✅ | ✅ | `base_url=http://localhost:1234/v1` |
| **LocalAI** | ✅ | ✅ | Drop-in replacement |
| **OpenRouter** | ✅ 100+ models | ❌ | `base_url=https://openrouter.ai/api/v1` |

### Using with Ollama (Local LLMs)

```bash
# 1. Install Ollama and pull models
ollama pull llama3.2
ollama pull nomic-embed-text

# 2. Configure .env
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
LLM_MODEL=llama3.2
EMBEDDING_MODEL=nomic-embed-text

# 3. Run the agent
poetry run uvicorn rag_financial_research_agent.main:app --port 7777
```

## Quick Start

### Prerequisites

- Python 3.10+
- Poetry
- OpenAI API key (or Ollama for local LLMs)

### Installation

```bash
cd examples/rag-financial-research-agent
poetry install
```

### Configuration

```bash
cp .env.example .env
# Edit .env with your API key and model preferences
```

**OpenAI Configuration:**
```bash
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
```

**Ollama Configuration:**
```bash
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
LLM_MODEL=llama3.2
EMBEDDING_MODEL=nomic-embed-text
```

### Ingest Sample Documents

```bash
# Ingest SEC filings for AAPL, MSFT, GOOGL
poetry run python scripts/ingest_sample_docs.py
```

### Run the Agent

```bash
poetry run uvicorn rag_financial_research_agent.main:app --port 7777 --reload
```

### Connect to OpenBB Workspace

1. Open OpenBB Workspace
2. Add custom agent with URL: `http://localhost:7777/agents.json`
3. Start asking questions!

## Example Queries

- "What are the key risk factors mentioned in Apple's latest 10-K?"
- "Compare revenue growth between MSFT and GOOGL based on their filings"
- "What did management say about AI in the last earnings call?"
- "Summarize Apple's R&D spending and focus areas"

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents.json` | GET | Agent descriptor for OpenBB Workspace |
| `/v1/query` | POST | Main query endpoint (SSE streaming) |
| `/health` | GET | Health check |
| `/stats` | GET | Vector store statistics |

### Query Example

```bash
curl -N http://localhost:7777/v1/query \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"human","content":"What are Apple'\''s key risks?"}]}'
```

**Response (SSE stream):**
```
event: copilotStatusUpdate
data: {"eventType":"INFO","message":"Searching financial documents..."}

event: copilotStatusUpdate
data: {"eventType":"INFO","message":"Found 5 relevant documents"}

event: copilotMessageChunk
data: {"delta":"Based on Apple's 10-K filing..."}

event: copilotCitationCollection
data: {"citations":[{"source_info":{"name":"AAPL_10-K_2023"}}]}
```

## Testing

```bash
poetry run pytest -v
```

## Linting

```bash
poetry run ruff check .
poetry run mypy rag_financial_research_agent
```

## Project Structure

```
rag-financial-research-agent/
├── rag_financial_research_agent/
│   ├── main.py                        # FastAPI application
│   ├── config.py                      # Configuration settings
│   ├── embeddings.py                  # Embedding generation (OpenAI/Ollama)
│   ├── vector_store.py                # ChromaDB operations
│   ├── retriever.py                   # RAG retrieval logic
│   ├── ingestion/
│   │   ├── base.py                    # Base ingestion interface
│   │   ├── sec_filings.py             # SEC EDGAR ingestion
│   │   ├── earnings_transcripts.py    # Earnings call ingestion
│   │   └── pdf_documents.py           # Generic PDF ingestion
│   └── utils/
│       ├── text_splitter.py           # Document chunking
│       └── prompts.py                 # System prompts
├── tests/                             # Test suite (19 tests)
├── scripts/
│   ├── ingest_sample_docs.py          # Sample ingestion script
│   └── health_check.py                # Health check script
├── data/                              # Document storage
├── pyproject.toml                     # Dependencies
└── .env.example                       # Environment template
```

## Key Components

### Document Ingestion

- **SEC Filings**: Downloads 10-K, 10-Q, 8-K from SEC EDGAR, chunks into ~1000 token segments
- **Earnings Transcripts**: Parses quarterly earnings call transcripts
- **PDF Documents**: Extracts text from research reports via pdfplumber

### Vector Store (ChromaDB)

- Persistent local storage in `./chroma_db`
- Cosine similarity search
- Metadata filtering by ticker, document type, date

### Retrieval

- Top-K semantic search (default: 5 documents)
- Metadata-based filtering (ticker, document type)
- Context formatting with source attribution

### LLM Generation

- Streaming responses via SSE
- Reasoning steps exposed to UI
- Automatic citation generation

## License

MIT
