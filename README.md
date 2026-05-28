# Christian AI Assistant

## Quick Start
1. Clone repo
2. `pip install -r requirements.txt`
3. Copy `.env.example` → `.env`, add API keys
4. `python backend/rag/embedder.py`  # one-time Bible embedding
5. `uvicorn backend.main:app --reload`
6. `cd frontend && npm install && npm run dev`

## Architecture
See `docs/architecture_note.md`

## Running Evaluations
`python eval/run_evals.py`

## Environment Variables
- `ANTHROPIC_API_KEY` — Claude API
- `OPENAI_API_KEY` — Embeddings + DALL-E 3 + Moderation
- `REDIS_URL` — Optional session persistence
