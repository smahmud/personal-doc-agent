# Personal Documentation Agent

A local, agentic system for retrieving, analyzing, and reasoning over personal documents.

## Features
- Upload and parse documents (PDF, MD, TXT, DOCX)
- Chat history analysis (Claude, Copilot, Gemini, Perplexity)
- Kiro IDE task tracking
- Car maintenance invoice analysis
- Unified agent interface

## Tech Stack
- Backend: Python + FastAPI
- Agent: LangChain
- LLM: Mistral 7B via Ollama
- Vectors: ChromaDB
- Frontend: Streamlit
- Containers: Docker

## Getting Started

### Prerequisites
- Docker Desktop
- Python 3.11+
- Ollama

### Installation
```bash
docker-compose up
```

## Access:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs


### Project Structure
```markdown
personal-doc-agent/
├── backend/
├── frontend/
├── data/
└── docker-compose.yml
```

### Development
See DEVELOPMENT.md for detailed setup.