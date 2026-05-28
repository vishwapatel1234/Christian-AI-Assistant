### Why RAG over fine-tuning?

Fine-tuning an LLM on the Bible would still hallucinate verse references — the model learns patterns, not an indexed lookup. RAG with a verified Bible corpus means every verse returned can be checked against the source. Hallucination is caught at the retrieval layer, not hoped away at generation.

### Why two-layer moderation?

A single post-generation filter is too late for adversarial prompts that steer the LLM mid-generation. The pre-LLM classifier catches intent early (e.g., "rewrite scripture to support X") before the model even processes it. The post-generation layer catches subtle failures that slipped through (e.g., a fabricated citation that sounded confident).

### Why denomination-aware routing via system prompt injection?

Denominations differ on canon (Catholic includes Deuterocanon), authority (Sola Scriptura vs. Tradition + Scripture), and doctrine (purgatory, saints, sacraments). Rather than one-size-fits-all answers, routing the denomination context into the system prompt lets the LLM tailor its frame while using the same underlying grounding engine.

### Hallucination prevention strategy

Three mechanisms work together:
1. **Retrieval constraint** — system prompt instructs the LLM to only cite verses it was given in context
2. **Post-generation verification** — every cited reference is parsed and looked up in the Bible corpus
3. **Uncertainty expression** — the LLM is instructed to say "I don't have a verse for that" rather than generate one
