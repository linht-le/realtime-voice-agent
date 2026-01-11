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

### 2. Setup Development Environment

#### Option A: DevContainer (Recommended for VS Code)

1. Open project in VS Code
2. Install "Dev Containers" extension
3. Press `F1` → "Dev Containers: Reopen in Container"
4. Wait for container to build

#### Option B: Docker Compose

```bash
# Start containers
docker compose up -d

# Exec into container
docker exec -it voice-agent-dev bash
```

### 3. Run Application

After setting up environment (Option A or B):

```bash
# Install dependencies
make install

# Terminal 1 - Run backend
make run-be

# Terminal 2 - Run frontend (for development)
make run-fe
```

**Access:**
- Frontend (dev): `http://localhost:5173` - Vue.js dev server with hot-reload
- Backend API: `http://localhost:8000` - Serves built frontend in production

**Important:** Always use `http://localhost:5173` for development to enable microphone access.

### 4. Upload Documents & Access Dashboard

Upload DOCX files to the vector database:

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@your-document.docx"
```

Or use FastAPI Swagger UI: `http://localhost:8000/docs`

View Qdrant dashboard: `http://localhost:6333/dashboard`

## Tech Stack

**Backend:**
- FastAPI
- OpenAI Realtime API
- LangGraph
- Qdrant

**Frontend:**
- Vue.js 3
- Pinia

**Infrastructure:**
- Docker
