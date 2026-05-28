# Christian AI Assistant

> A scripture-grounded, hallucination-safe AI assistant for Christian faith, theology, and devotional content — built with RAG, multi-layer safety, and denomination-aware routing.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-orange)](https://ai.google.dev)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple)](https://www.trychroma.com)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **RAG-Grounded Answers** | Retrieves real KJV verses from 31,102-verse ChromaDB before generating |
| 🛡️ **Two-Layer Safety** | Pre-LLM adversarial filter + post-generation citation verifier |
| ⛪ **Denomination Routing** | Tailored responses for Catholic, Protestant, Orthodox, Baptist, Lutheran |
| 🏛️ **Greek/Hebrew Concordance** | Click theological words (love, grace, faith) for inline Strong's etymology |
| 📅 **Liturgical Calendar** | Live daily readings widget synced to selected tradition |
| 📖 **Wisdom Quiz** | 15-question pool, randomized 5-per-round with scoring & celebrations |
| 🎨 **Sacred Image Generation** | AI-generated Christian artwork via Gemini Imagen |
| 🎙️ **Voice Input** | Web Speech API for hands-free query input |
| 📄 **PDF Export** | One-click styled conversation report |
| 💬 **Session History** | LocalStorage-persisted past conversations |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- A Google Gemini API key ([get one free](https://aistudio.google.com))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/vishwapatel1234/Christian-AI-Assistant.git
cd Christian-AI-Assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY_1

# 4. Build the Bible vector database (one-time, ~5 minutes)
python backend/rag/embedder.py

# 5. Start the server
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 6. Open in browser
# → http://localhost:8000
# → http://<your-local-ip>:8000  (for network access)
```

---

## 🏗️ Architecture

```
Browser (Vanilla HTML/CSS/JS)
         │
         │ REST API
         ▼
FastAPI Backend
    ├── Pre-LLM Safety Filter
    ├── RAG Retriever (ChromaDB)
    ├── Denomination Context Injector
    ├── Gemini LLM (multi-model fallback)
    └── Post-Generation Citation Verifier
         │
         ▼
ChromaDB — 31,102 KJV verses (Gemini embeddings)
```

See [`docs/architecture_note.md`](docs/architecture_note.md) for the full engineering breakdown.

---

## 📁 Project Structure

```
christian-ai-assistant/
├── backend/
│   ├── main.py                  # FastAPI entrypoint & API routes
│   ├── chat/
│   │   ├── handler.py           # Chat pipeline + multi-model fallback
│   │   ├── prompts.py           # System prompt templates
│   │   └── denomination.py      # Denomination-aware context builder
│   ├── rag/
│   │   ├── embedder.py          # One-time Bible corpus embedding
│   │   └── retriever.py         # Semantic verse search (ChromaDB)
│   ├── safety/
│   │   ├── moderator.py         # Two-layer safety orchestrator
│   │   ├── verse_verifier.py    # Citation hallucination detector
│   │   └── adversarial.py       # Pre-LLM adversarial pattern filter
│   ├── image/
│   │   └── generator.py         # Sacred image generation pipeline
│   └── memory/
│       └── session_store.py     # In-memory conversation history
├── frontend/
│   └── index.html               # Complete UI (zero framework dependencies)
├── data/
│   └── bible_kjv.json           # Full KJV Bible corpus (31,102 verses)
├── docs/
│   └── architecture_note.md     # Detailed engineering decisions
├── eval/
│   └── run_evals.py             # Automated evaluation suite
├── .env.example                 # Environment variable template
└── requirements.txt
```

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
GEMINI_API_KEY_1=your_gemini_api_key_here
GEMINI_API_KEY_2=optional_second_key_for_fallback
GEMINI_API_KEY_3=optional_third_key_for_fallback
REDIS_URL=redis://localhost:6379/0  # Optional: for persistent sessions
```

---

## 🧪 Running Evaluations

```bash
python eval/run_evals.py
```

Tests include: grounding accuracy, hallucination detection, adversarial prompt resistance, denomination routing, and edge cases.

---

## 🛡️ Hallucination Prevention

Three mechanisms work together:
1. **Retrieval Constraint** — LLM is only allowed to cite verses given in context
2. **Post-Generation Verification** — Every citation is checked against ChromaDB
3. **Uncertainty Expression** — LLM instructed to admit gaps rather than fabricate

---

## 📄 License

MIT License — built for educational and demonstration purposes.
