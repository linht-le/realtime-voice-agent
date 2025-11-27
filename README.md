# Realtime Voice Agent

A real-time voice assistant powered by OpenAI Realtime API, LangGraph, and RAG capabilities.

## Quick Start

### 1. Configure Environment Variables

```bash
cp .env.example .env
```

Edit [.env](.env) and add your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 2. Setup & Run

#### Option A: DevContainer (Recommended for VS Code)

1. Open project in VS Code
2. Install "Dev Containers" extension
3. Press `F1` → "Dev Containers: Reopen in Container"
4. Wait for container to build
5. Run: `make run`
6. Open **`http://localhost:8000`** in your browser

#### Option B: Docker Compose

```bash
# Start containers
docker compose -f docker-compose-dev.yml up -d

# Exec into container
docker exec -it voice-agent-dev bash

# Inside container, run:
make install
make run
```

Then open **`http://localhost:8000`** in your browser

**Important:** Always use `http://localhost:8000` in your browser (not `http://0.0.0.0:8000`) to enable microphone access for voice features.

### 3. Upload Documents & Access Dashboard

Upload DOCX files to the vector database:

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@your-document.docx"
```

Or use FastAPI Swagger UI: `http://localhost:8000/docs`

View Qdrant dashboard: `http://localhost:6333/dashboard`

## Tech Stack

- FastAPI
- OpenAI Realtime API
- LangGraph
- Qdrant
- Docker
