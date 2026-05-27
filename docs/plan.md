# LinguaForge Development Plan

**This document is historical.** The authoritative, up-to-date implementation plan is maintained in the active Grok session plan file.

See the detailed living plan (with current status, architectural decisions, and phased tasks):

`~/.grok/sessions/.../019e6a1b-b0dc-7751-8d5d-1098e6133628/plan.md`

---

**Goal**: Build a fully local, agentic language learning tool using vLLM (OpenAI-compatible local server).

**Current Status**: Phase 0 (Stabilization) largely complete as of this update.
- All critical imports now resolve
- Central LLM client factory in place (`app/core/llm.py`)
- All agents updated to use local model (no more hardcoded gpt-4o)
- Curriculum model + CurriculumTool skeleton implemented (hybrid seed + agent approach)
- SkillTool now has full test coverage + a bug was fixed during testing
- Routers mounted in main.py
- Timezone-aware datetimes throughout (no more utcnow deprecation warnings)
- 20+ tests passing

**Next**: Phase 1 (real CurriculumTool methods + seed data) after any final Phase 0 polish.

See the full session plan for the complete revised roadmap, decisions, and guardrails.

---

## MVP Features (Target)

1. User profiles
2. Skill mastery tracking + adaptive recommendations
3. Dynamic curriculum with remedial lessons
4. Lesson generation with grounding PDFs
5. Basic conversation (text first, voice later)
6. Simple FastAPI backend

---

## Remaining Tasks (Prioritized)

### Phase 2: Tool Layer (Current)

- [ ] **CurriculumTool** — Manage monthly blocks, remedial lessons, progress-driven advancement
- [ ] Add more tests for SkillTool & HistoryTool

### Phase 3: Grounding & Content

- [ ] **PDF Grounding Service** (`services/pdf_grounding.py`)
- [ ] Language onboarding flow (upload CEFR PDFs)

### Phase 4: Agent Layer (Core Intelligence)

- [ ] **Observer Agent** — Analyzes session results and suggests micro-lessons
- [ ] **Lesson Generator Agent** — Creates lessons with RAG from grounding PDFs
- [ ] **Curriculum Agent** — Decides when to add remedial content or advance
- [ ] **Reviewer Agent** — Handles tool errors gracefully

### Phase 5: API Layer

- [ ] FastAPI routers (`profile_router`, `lesson_router`, `curriculum_router`, `chat_router`)
- [ ] Basic endpoints for testing tools and agents

### Phase 6: Polish & MVP Release

- [ ] Simple frontend (Gradio or Streamlit for quick testing)
- [ ] Voice chat skeleton (text → STT/TTS later)
- [ ] Documentation + README
- [ ] Docker setup (optional)

---

## Recommended Next Steps (Next Session)

1. **CurriculumTool** (most important remaining piece)
2. PDF Grounding Service
3. Observer Agent
4. Lesson Generator Agent

---

**Development Rules**
- Keep files small and focused
- Every major feature should have tests
- Use `BaseTool` inheritance
- Prioritize stability over features

---

**Next Prompt Ready**: Tell me when you want to start with **CurriculumTool**.