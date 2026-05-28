# Christian AI Assistant — Architecture Note

## Overview

A scripture-grounded Christian AI assistant built with a **Retrieval-Augmented Generation (RAG)** pipeline, multi-layer safety system, denomination-aware routing, and a premium glassmorphic web interface. The system is designed to answer theological questions, generate devotional content, and produce Christian-themed sacred art — while actively preventing hallucinated scripture citations.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Browser (Vanilla HTML/CSS/JS)             │
│  Chat UI · Concordance Cards · Quiz · Liturgical Calendar   │
│  PDF Export · Voice Input · Sacred Image Generation         │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (HTTP/JSON)
┌────────────────────────▼────────────────────────────────────┐
│                  FastAPI Backend (Python)                    │
│                                                             │
│  ┌─────────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Chat Handler   │  │ Safety Layer │  │  Image Gen    │  │
│  │  + Memory       │  │ (2-layer)    │  │  Pipeline     │  │
│  └────────┬────────┘  └──────┬───────┘  └───────────────┘  │
│           │                  │                              │
│  ┌────────▼──────────────────▼──────────────────────────┐  │
│  │              Grounding Engine                        │  │
│  │    Scripture Retriever → Verse Verifier              │  │
│  └────────────────────┬─────────────────────────────────┘  │
└───────────────────────┼─────────────────────────────────────┘
                        │
       ┌────────────────▼────────────────┐
       │  ChromaDB Vector Store          │
       │  31,102 KJV Bible verses        │
       │  Embedded via Gemini Embedding  │
       └─────────────────────────────────┘
                        │
       ┌────────────────▼────────────────┐
       │  Gemini LLM (Multi-model        │
       │  fallback: 2.5 Pro → 2.5 Flash  │
       │  → 2.0 Flash → 1.5 Pro)         │
       └─────────────────────────────────┘
```

---

## Core Engineering Decisions

### 1. Why RAG over Fine-Tuning?

Fine-tuning an LLM on the Bible teaches it *patterns* — it cannot look up an exact verse. RAG with a verified Bible corpus means every verse returned is pulled directly from indexed source text and can be checked character-by-character for accuracy. **Hallucination is caught at the retrieval layer, not hoped away at generation.**

| Approach | Hallucination Risk | Updatable | Cost |
|---|---|---|---|
| Fine-tuning | High (confident but wrong) | Expensive retrain | High |
| RAG (this system) | Low (citation-verified) | Update corpus only | Low |

### 2. Two-Layer Safety Moderation

A single post-generation filter is too late for adversarial prompts that steer the LLM mid-generation.

```
User Input
    │
    ▼
[Layer 1: Pre-LLM Classifier]          ← catches: "rewrite scripture to justify X"
    │ passes only safe inputs
    ▼
[Gemini LLM + RAG Grounding]
    │
    ▼
[Layer 2: Post-Generation Verifier]    ← catches: fabricated citations that slipped through
    │
    ▼
Final Response
```

- **Layer 1 (adversarial.py):** Pattern-matches known manipulation tactics before the LLM ever sees the input.
- **Layer 2 (verse_verifier.py):** Parses every `[Book Chapter:Verse]` citation from the LLM output and checks it against ChromaDB. Unverified citations are flagged with `[UNVERIFIED CITATION]` and a disclaimer is appended.

### 3. Denomination-Aware Routing

Denominations differ on canon (Catholic includes Deuterocanon), authority (Sola Scriptura vs. Tradition + Scripture), and doctrine (purgatory, saints, sacraments). Rather than one-size-fits-all answers, the user's selected tradition (Catholic / Protestant / Orthodox / Baptist / Lutheran) is injected into the system prompt, letting the LLM tailor its theological frame while using the same underlying grounding engine.

### 4. Multi-Model API Fallback Chain

The system cycles through multiple Gemini model versions across multiple API keys. If one model hits a rate limit or fails, it automatically falls back to the next. This ensures **zero downtime for the user** in demo scenarios.

```python
API_KEYS = [KEY_1, KEY_2, KEY_3]
MODELS   = [gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash, gemini-1.5-pro]
# → 12 total fallback combinations
```

### 5. Embedding Strategy

Bible verses are embedded at ingestion time using `gemini-embedding-001` with `task_type="retrieval_document"`. At query time, the user's question is embedded with `task_type="retrieval_query"` — this asymmetric embedding approach is specifically designed for document retrieval and significantly outperforms symmetric cosine similarity for Q&A tasks.

---

## Data Flow — Single Chat Request

```
1. User types: "What does the Bible say about forgiveness?"
2. Frontend → POST /api/chat { message, session_id, denomination }
3. Backend: pre_llm_check() → passes (no adversarial pattern)
4. BibleRetriever.search("forgiveness", top_k=3)
   → ChromaDB cosine similarity → returns top 3 KJV verses
5. build_system_prompt(denomination_context, retrieved_verses)
6. Gemini LLM generates response, citing only provided verses
7. post_llm_check() → parses citations, verifies each in ChromaDB
8. Response returned to frontend
9. Frontend renderBubble() → formats citations, highlights
   concordance trigger words (love, grace, faith, peace...)
10. User can click highlighted words → inline Greek/Hebrew
    Concordance Card slides open with Strong's numbers
```

---

## Frontend Engineering Highlights

| Feature | Implementation |
|---|---|
| **Inline Concordance Cards** | Event delegation on `chatWindow`, dynamic DOM insertion, CSS `max-height` transition |
| **Scriptural Wisdom Quiz** | Fisher-Yates shuffle over 15-question pool, slices 5 random per round, canvas particle celebration |
| **Liturgical Calendar Widget** | Date-indexed lookup across 6 tradition databases, clickable reading links that auto-query the AI |
| **PDF Export** | `window.open` + `window.print()` with a styled report template, renders entire conversation |
| **Voice Input** | Web Speech API (`SpeechRecognition`) with visual feedback states |
| **Conversation History** | `localStorage` session persistence, up to 5 past sessions with restore |
| **Sacred Image Generation** | Backend pipeline → Gemini Imagen, returned as base64 URL |

---

## Technology Stack

| Layer | Technology |
|---|---|
| **LLM** | Google Gemini (2.5 Pro / 2.5 Flash / 2.0 Flash) |
| **Embeddings** | Gemini Embedding 001 |
| **Vector Store** | ChromaDB (local persistent) |
| **Backend** | FastAPI + Python 3.11 |
| **Frontend** | Vanilla HTML5 / CSS3 / JavaScript (zero frameworks) |
| **Session Memory** | In-memory store + localStorage |
| **Bible Corpus** | KJV — 31,102 verses |

---

## Hallucination Prevention — Three Mechanisms

1. **Retrieval Constraint** — System prompt explicitly instructs the LLM: *"Only cite verses provided in context. Never cite from memory."*
2. **Post-Generation Verification** — Every `[Book Chapter:Verse (Translation)]` citation is parsed by regex and looked up in ChromaDB. Failures are flagged visually.
3. **Uncertainty Expression** — The LLM is instructed to say *"I don't have a retrieved verse for that"* rather than generate one from parametric memory.

---

## Security Considerations

- API keys stored only in `.env` (excluded from git via `.gitignore`)
- Pre-LLM adversarial filter blocks prompt injection attempts
- No user data stored server-side beyond in-memory session (cleared on restart)
- CORS configured for controlled origins in production
