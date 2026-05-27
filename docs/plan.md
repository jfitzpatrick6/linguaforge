# LinguaForge Development Plan

**Goal**: Build a fully local, agentic language learning tool using any OpenAI-compatible local LLM server (vLLM, llama.cpp, Ollama, etc.).

**Last Updated**: June 2026 (post Phase 4 implementation)

---

## Current Status

The project has made **very strong progress**. The core backend is now functional:

### What is Working Well
- **Tool Layer**: Complete and solid
  - `ProfileTool`, `SkillTool`, `HistoryTool`, `CurriculumTool` (full implementation with seeding, remedial blocks, progress tracking)
  - All follow `BaseTool` async patterns with safe transactions

- **RAG / Grounding**: Production-ready local PDF grounding service
  - Real `pymupdf` parsing
  - Persistent Chroma at `CHROMA_PATH`
  - `sentence-transformers` embeddings (multilingual by default)
  - Rich metadata + good chunking
  - Fully tested

- **Agent Layer**: Significantly advanced
  - Agents converted to proper classes with dependency injection
  - Structured Pydantic outputs (`Lesson`, `CurriculumRecommendation`, etc.)
  - `LessonGeneratorAgent` now actually uses `PDFGrounding` + RAG
  - `CurriculumAgent`, `ObserverAgent`, and `ReviewerAgent` produce structured output

- **API Layer** (Phase 4 complete)
  - Real FastAPI routers with proper dependency injection
  - Key working flows:
    - Onboarding + profile management
    - Curriculum seeding, active block, overview, completion, remedial creation
    - Lesson generation (`POST /api/lessons/generate`) — the core experience
    - Session logging + AI-generated observation via ObserverAgent

- **Testing**: Strong coverage (37+ passing tests). Most logic is unit-testable without a running LLM.

- **Architecture**: Clean separation (core → tools → services → agents → routers)

### What is Still Missing / Rough

- No user-facing interface (you currently interact via API or Python)
- Generated lessons are not persisted
- Agents are capable but orchestration is still mostly manual (no deep "study session" loop yet)
- Minimal error handling and user-friendly responses in some endpoints
- No real content (you must ingest your own PDFs)
- Documentation is minimal
- No frontend
- Voice is untouched (as planned)
- Test API integration tests are flaky due to test DB model registration

---

## MVP Vision (Target for "Usable Prototype")

A user should be able to:

1. Onboard with a target language
2. Have an initial curriculum automatically seeded
3. Generate real, grounded lessons on demand (using their PDFs)
4. Log practice sessions and receive useful AI reflections
5. See progress and get adaptive recommendations

All running **100% locally**.

---

## Revised Phased Roadmap

### Completed
- **Phase 0**: Stabilization & Consistency
- **Phase 1**: Curriculum Domain (CurriculumTool + seeding)
- **Phase 2**: PDF Grounding Service (real RAG)
- **Phase 3**: Agent Layer (structured agents + RAG integration)
- **Phase 4**: API Layer (real routers + key flows)

### Phase 5: Usable MVP Loop (Current Priority)

**Goal**: Turn the backend into something a real person can use without writing Python.

**Tasks**:
- [ ] Build a simple frontend (strongly recommended: **Gradio** first for speed, or Streamlit)
  - Onboarding screen
  - View current curriculum + seed button
  - "Generate Lesson" interface (topic + level → nice lesson card)
  - Log practice / "I studied this" button
  - Recent sessions + AI observations
- [ ] Persist generated lessons (lightweight — add a `GeneratedLesson` model or store in `SessionLog`)
- [ ] Improve lesson generation UX (better prompts, length control, save/share)
- [ ] Basic admin/ingestion UI or CLI for uploading grounding PDFs
- [ ] Better error handling + friendly messages across the API
- [ ] Add a "Study Session" endpoint or frontend flow that chains:
  CurriculumAgent → LessonGenerator → (user studies) → ObserverAgent

**Success Criteria**: A non-developer can run the app locally and complete a full learning loop.

### Phase 6: Polish & Hardening

- [ ] Comprehensive README + setup guide (including local LLM recommendations)
- [ ] Prompt engineering / few-shot improvements for agents
- [ ] Optional: Docker Compose setup (app + optional local LLM)
- [ ] Better chunking strategies and retrieval quality in grounding service
- [ ] Admin protection for PDF ingestion endpoints
- [ ] More robust structured output (retry logic, better fallbacks)
- [ ] User progress analytics dashboard (simple)
- [ ] Voice chat skeleton (STT/TTS) — only if desired

### Phase 7: Stretch / Future Ideas (Post-MVP)

- Multi-language support with better UX
- Spaced repetition integration (Anki export or built-in)
- User-contributed grounding content
- More sophisticated agent memory / long-term user model
- Evaluation harness for lesson quality

---

## Recommended Next Steps (Immediate)

1. **Build a Gradio frontend** (highest leverage right now)
   - This will surface real usability issues and make the project feel alive.
2. Persist generated lessons and improve the `/lessons/generate` experience.
3. Create a proper `README.md` with:
   - How to run locally
   - How to set up a local LLM
   - How to ingest grounding PDFs
   - Current capabilities + limitations
4. Add a simple "Start Study Session" flow that ties the agents together.

---

## Development Guardrails (Still Valid)

- Keep files small and focused
- Every major feature should have tests
- Use `BaseTool` inheritance for all DB access
- Prioritize **stability and usability** over new features
- Prefer simple, explicit orchestration over heavy agent frameworks for now
- All LLM calls should go through the central client factory

---

## Notes on Architecture Decisions

- **No heavy frameworks** (LangChain, etc.) unless they provide clear value. Current explicit agent classes + dependency injection has worked well.
- **Lessons are generated on demand** (with optional persistence later).
- **Curriculum is hybrid** (seed blocks + agent-created remedial/advancement) — this model has held up.
- **Local-first RAG** using sentence-transformers + Chroma is working reliably.

---

**This document is now the source of truth** for the project plan. The old session plan can be treated as historical.

Let's ship something people can actually use.