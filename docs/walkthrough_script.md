# Christian AI Assistant — 5–8 Minute Walkthrough Script

> **Estimated time:** 6–7 minutes  
> **Audience:** Technical interviewer (SoluLab)  
> **Demo URL:** http://192.168.1.41:8000

---

## 🎬 OPENING (30 seconds)

> *"I built a Christian AI Assistant that answers theological questions, generates devotional content, and produces sacred art — all grounded in real scripture using a RAG pipeline with active hallucination prevention. Let me walk you through the system."*

---

## 🏗️ PART 1 — Architecture Overview (1 minute)

> *"The system has three main layers:"*

**Point to:** `docs/architecture_note.md`

1. **Frontend** — Pure Vanilla HTML/CSS/JS. Zero framework dependencies. Glassmorphic dark UI with premium animations.

2. **FastAPI Backend** — Handles routing, safety checks, session memory, and image generation.

3. **RAG + ChromaDB** — The entire KJV Bible (31,102 verses) is embedded using Gemini Embedding 001 and stored in ChromaDB. When a user asks a question, we do a semantic similarity search and pass the top 3–5 matching verses to the LLM as grounding context.

> *"Crucially — the LLM is instructed to only cite verses it was given. It cannot cite from memory. This is how we eliminate hallucinated scripture."*

---

## 🛡️ PART 2 — Safety System (1 minute)

> *"The system has a two-layer safety architecture:"*

**Open:** `backend/safety/moderator.py`

**Layer 1 — Pre-LLM (adversarial.py):**
> *"Before the user's message even reaches the LLM, it goes through an adversarial pattern classifier. This catches manipulation attempts like 'rewrite this verse to support X' or prompt injection attacks. If it's blocked, the LLM never sees the message."*

**Layer 2 — Post-Generation (verse_verifier.py):**
> *"After the LLM responds, we parse every Bible citation in the output using regex — for example `[John 3:16 (KJV)]`. Each citation is looked up directly in ChromaDB. If it doesn't exist in our verified corpus, it's flagged as `[UNVERIFIED CITATION]` and a disclaimer is shown. This catches subtle hallucinations that sounded confident."*

---

## ⛪ PART 3 — Denomination Routing (30 seconds)

**Click:** Tradition dropdown → switch from Generic to Catholic → ask a question

> *"Christianity isn't monolithic. Catholics include the Deuterocanon, Orthodox follow different liturgical traditions, Protestants hold Sola Scriptura. Rather than one-size-fits-all answers, the selected denomination gets injected into the system prompt, tailoring the LLM's theological frame while the same RAG engine runs underneath."*

---

## 💬 PART 4 — Live Chat Demo (1 minute)

**Type:** *"What does the Bible say about forgiveness?"*

> *"Watch what happens — the backend retrieves the most semantically relevant KJV verses, passes them to Gemini, and the response cites only those verses. Notice the purple citation badges — those are real, verified references."*

**Point out:**
- The **Gemini fallback chain** — 3 API keys × 4 model versions = 12 fallback combinations for zero downtime
- **Highlighted trigger words** — love, grace, faith, peace are clickable

**Click the word `love` in the response:**
> *"Clicking any highlighted theological term opens an inline Strong's Concordance card — right inside the chat bubble. You see the original Koine Greek root (ἀγάπη Agape vs φιλέω Phileo), the Strong's number, the phonetic pronunciation, and even a speaker button that plays the correct ancient pronunciation using the browser's speech synthesis API."*

---

## 📅 PART 5 — Sidebar Features (45 seconds)

**Scroll the sidebar:**

**Recent Chats:**
> *"Conversations are persisted in localStorage. Previous sessions appear here and can be restored with full context."*

**Daily Liturgy Widget:**
> *"This auto-updates based on the current date and selected tradition. Each reading is clickable and fires a pre-built query to the AI."*

**Scriptural Wisdom Quiz:**
> *"A gamified Bible quiz pulling from a 15-question pool. Each round randomly selects 5 different questions using a Fisher-Yates shuffle with a `.slice(0,5)`. On completion, a confetti particle animation fires on the canvas. This demonstrates clean game state management in pure JS."*

---

## 🎨 PART 6 — Image Generation (30 seconds)

**Type:** *"Draw a picture of the baptism of Jesus"*

> *"The message is routed to a separate `/api/image` endpoint. The backend sanitizes the prompt for content safety, sends it to Gemini Imagen, and returns the image as a URL. The frontend renders it as a styled sacred art card."*

---

## 📄 PART 7 — PDF Export & Voice (30 seconds)

**Click Export PDF:**
> *"Clicking Export PDF generates a fully styled HTML report of the entire conversation and opens the browser print dialog. This is entirely client-side — no server needed."*

**Click Microphone:**
> *"The mic button uses the browser's native Web Speech API. When active, it captures voice, transcribes it locally on the client, and places the transcript into the input field. No third-party transcription service required."*

---

## 🧪 PART 8 — Evaluation Suite (30 seconds)

**Open:** `eval/run_evals.py`

> *"The project includes an automated evaluation suite with test cases covering: correct scripture grounding, hallucination detection, adversarial prompt resistance, denomination routing accuracy, and edge cases like non-Christian topics or scripture modification requests. In a production system this would run in CI on every commit."*

---

## 🏁 CLOSING (30 seconds)

> *"To summarize the key engineering decisions:"*

1. **RAG over fine-tuning** — precise retrieval beats parametric memory for citation accuracy
2. **Two-layer safety** — pre and post generation catch different failure modes
3. **Denomination routing** — system prompt injection handles theological diversity
4. **Multi-model fallback** — 12 combinations ensure demo resilience
5. **Zero-framework frontend** — demonstrates raw CSS/JS proficiency, no abstraction layers

> *"The GitHub repo is at github.com/vishwapatel1234/Christian-AI-Assistant. The architecture note in `/docs` covers every decision in depth. Happy to go deeper on any layer — RAG retrieval strategy, the safety system, or the frontend concordance card implementation."*

---

## 📊 Quick Reference Card

| Component | Tech | Why |
|---|---|---|
| LLM | Gemini 2.5 Pro | Best instruction-following, safe outputs |
| Embeddings | Gemini Embedding 001 | Asymmetric retrieval task types |
| Vector DB | ChromaDB | Local, fast, no infra required |
| Backend | FastAPI | Async, type-safe, auto-docs |
| Frontend | Vanilla JS | Zero dependencies, max control |
| Bible Corpus | KJV (31,102 verses) | Public domain, complete coverage |

---

## ⚡ Questions You May Be Asked

**Q: Why not use OpenAI?**
> "Gemini was chosen for its native multimodal capabilities (text + image in one API), strong instruction-following, and generous free tier for prototyping. The fallback chain is model-agnostic — swapping to OpenAI or Claude would be a one-function change in `handler.py`."

**Q: How does RAG prevent hallucination?**
> "The system prompt explicitly forbids the LLM from citing scripture from memory. After generation, every `[Book Chapter:Verse]` citation is parsed and verified against ChromaDB. If it doesn't match, it's flagged. Three independent mechanisms make it extremely difficult to slip through a fabricated verse."

**Q: How would you scale this to production?**
> "Replace ChromaDB with Pinecone or Weaviate for distributed vector search. Move session storage from in-memory to Redis. Add a CDN for the frontend. Deploy FastAPI behind a load balancer. The RAG and safety layers are stateless and scale horizontally."

**Q: How does denomination routing work technically?**
> "The `denomination.py` module maps the user's selection to a denomination-specific context string — covering canonical differences, key doctrines, and theological emphasis. This string is injected into the system prompt before the retrieved verses. The LLM receives denomination context + verses + grounding rules as a single coherent system prompt."
