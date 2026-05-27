"""
LinguaForge - Gradio Frontend (MVP)

A simple, local-first UI for the LinguaForge language learning backend.

Run with:
    python gradio_app.py

Make sure the FastAPI backend is running on the same machine.
"""

import gradio as gr
import requests
from typing import Optional, Dict, Any, List
from pathlib import Path

from app.services.pdf_grounding import get_pdf_grounding_service

# --------------------------- Configuration --------------------------- #

DEFAULT_API_BASE = "http://localhost:8000"


# --------------------------- API Client ------------------------------ #

class LinguaForgeClient:
    """Lightweight client for the LinguaForge API."""

    def __init__(self, base_url: str = DEFAULT_API_BASE):
        self.base_url = base_url.rstrip("/")

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        resp = requests.get(self._url(path), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, json: Optional[Dict] = None, params: Optional[Dict] = None) -> Any:
        resp = requests.post(self._url(path), json=json, params=params, timeout=60)
        resp.raise_for_status()
        return resp.json()

    # --- Profile ---
    def onboard(self, user_id: str, name: Optional[str] = None, target_language: str = "es") -> Dict:
        return self._post("/api/onboarding", json={
            "user_id": user_id,
            "name": name,
            "target_language": target_language
        })

    def get_profile(self, user_id: str) -> Optional[Dict]:
        try:
            return self._get(f"/api/profile/{user_id}")
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # --- Curriculum ---
    def seed_curriculum(self, user_id: str, language: str = "es") -> List[Dict]:
        return self._post(f"/api/curriculum/seed/{user_id}", params={"language": language})

    def get_active_block(self, user_id: str) -> Optional[Dict]:
        return self._get(f"/api/curriculum/active/{user_id}")

    def get_overview(self, user_id: str) -> Dict:
        return self._get(f"/api/curriculum/overview/{user_id}")

    def complete_block(self, block_id: int, user_id: str) -> Dict:
        return self._post(f"/api/curriculum/{block_id}/complete", params={"user_id": user_id})

    # --- Lessons ---
    def generate_lesson(self, user_id: str, language: str, topic: str, skill_level: str = "A1") -> Dict:
        return self._post("/api/lessons/generate", json={
            "user_id": user_id,
            "language": language,
            "topic": topic,
            "skill_level": skill_level
        })

    # --- Sessions & Observations ---
    def log_session(self, user_id: str, session_type: str, data: Dict, duration_minutes: int = 0) -> Dict:
        return self._post("/api/sessions/log", json={
            "user_id": user_id,
            "session_type": session_type,
            "data": data,
            "duration_minutes": duration_minutes
        })

    def get_observation(self, user_id: str, recent_limit: int = 3) -> Dict:
        return self._post(f"/api/sessions/{user_id}/observe", params={"recent_limit": recent_limit})


# --------------------------- Gradio UI -------------------------------- #

def create_app():
    with gr.Blocks(title="LinguaForge") as demo:
        gr.Markdown("# 🗣️ LinguaForge\n**Your fully local AI language tutor**")

        # Global state
        api_client = gr.State(lambda: LinguaForgeClient())

        with gr.Row():
            with gr.Column(scale=1):
                api_base = gr.Textbox(
                    value=DEFAULT_API_BASE,
                    label="API Base URL",
                    placeholder="http://localhost:8000"
                )
                user_id = gr.Textbox(
                    value="demo_user",
                    label="User ID",
                    placeholder="your_username"
                )
                language = gr.Dropdown(
                    ["es", "fr", "de", "it", "pt", "ja"],
                    value="es",
                    label="Target Language"
                )

            with gr.Column(scale=3):
                status_box = gr.Textbox(label="Status", interactive=False)

        # ------------------ Tabs ------------------ #
        with gr.Tabs():

            # === Tab 1: Profile ===
            with gr.Tab("👤 Profile & Onboarding"):
                with gr.Row():
                    name = gr.Textbox(label="Your Name (optional)")
                    onboard_btn = gr.Button("Onboard / Create Profile", variant="primary")

                profile_display = gr.JSON(label="Current Profile")

                def do_onboard(user_id_val, name_val, lang_val, base_url):
                    client = LinguaForgeClient(base_url)
                    try:
                        profile = client.onboard(user_id_val, name_val or None, lang_val)
                        return profile, f"✅ Profile ready for {user_id_val}"
                    except Exception as e:
                        return None, f"❌ Error: {str(e)}"

                onboard_btn.click(
                    fn=do_onboard,
                    inputs=[user_id, name, language, api_base],
                    outputs=[profile_display, status_box]
                )

                gr.Button("Refresh Profile").click(
                    fn=lambda uid, base: LinguaForgeClient(base).get_profile(uid),
                    inputs=[user_id, api_base],
                    outputs=[profile_display]
                )

            # === Tab 2: Curriculum ===
            with gr.Tab("📚 My Curriculum"):
                with gr.Row():
                    seed_btn = gr.Button("🌱 Seed Initial Curriculum", variant="primary")
                    refresh_curric_btn = gr.Button("Refresh")

                overview = gr.JSON(label="Curriculum Overview")
                active_block = gr.JSON(label="Current Active Block")

                def seed_curriculum(user_id_val, lang_val, base_url):
                    client = LinguaForgeClient(base_url)
                    try:
                        blocks = client.seed_curriculum(user_id_val, lang_val)
                        overview_data = client.get_overview(user_id_val)
                        active = client.get_active_block(user_id_val)
                        return overview_data, active, f"✅ Seeded {len(blocks)} blocks"
                    except Exception as e:
                        return None, None, f"❌ {str(e)}"

                seed_btn.click(
                    fn=seed_curriculum,
                    inputs=[user_id, language, api_base],
                    outputs=[overview, active_block, status_box]
                )

                def refresh_curriculum(user_id_val, base_url):
                    client = LinguaForgeClient(base_url)
                    try:
                        overview_data = client.get_overview(user_id_val)
                        active = client.get_active_block(user_id_val)
                        return overview_data, active
                    except Exception as e:
                        return None, None

                refresh_curric_btn.click(
                    fn=refresh_curriculum,
                    inputs=[user_id, api_base],
                    outputs=[overview, active_block]
                )

                complete_btn = gr.Button("✅ Mark Current Block as Complete")
                complete_btn.click(
                    fn=lambda uid, base: (
                        (client := LinguaForgeClient(base)).complete_block(
                            client.get_active_block(uid)["id"], uid
                        ) if client.get_active_block(uid) else None,
                        client.get_overview(uid),
                        client.get_active_block(uid)
                    ),
                    inputs=[user_id, api_base],
                    outputs=[status_box, overview, active_block]
                )

            # === Tab 3: Generate Lesson (Core Feature) ===
            with gr.Tab("✨ Generate Lesson"):
                with gr.Row():
                    with gr.Column(scale=3):
                        topic = gr.Textbox(
                            label="What do you want to learn?",
                            placeholder="ser vs estar, food vocabulary, past tense...",
                            lines=1
                        )
                    with gr.Column(scale=1):
                        level = gr.Dropdown(["A1", "A2", "B1", "B2"], value="A1", label="Your Level")

                generate_btn = gr.Button("🚀 Generate Lesson", variant="primary", size="lg")

                with gr.Accordion("📖 Lesson", open=True):
                    lesson_title = gr.Markdown()
                    lesson_explanation = gr.Markdown()

                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Examples")
                        examples_md = gr.Markdown()
                    with gr.Column():
                        gr.Markdown("### Practice")
                        practice_md = gr.Markdown()

                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Common Pitfalls")
                        pitfalls_md = gr.Markdown()
                    with gr.Column():
                        gr.Markdown("### Next Steps")
                        next_steps_md = gr.Markdown()

                def generate_lesson(user_id_val, lang_val, topic_val, level_val, base_url):
                    if not topic_val.strip():
                        return "Please enter a topic", "", "", "", "", "❌ Topic is required"
                    client = LinguaForgeClient(base_url)
                    try:
                        lesson = client.generate_lesson(user_id_val, lang_val, topic_val.strip(), level_val)

                        title = f"### {lesson.get('title', 'Lesson')}"
                        explanation = lesson.get('explanation', '')
                        examples = "\n".join([f"- {ex}" for ex in lesson.get('examples', [])]) or "_No examples generated._"
                        practice = "\n".join([f"- {p}" for p in lesson.get('practice_items', [])]) or "_No practice items._"
                        pitfalls = "\n".join([f"- {p}" for p in lesson.get('common_pitfalls', [])]) or "_None listed._"
                        next_steps = "\n".join([f"- {n}" for n in lesson.get('next_steps', [])]) or "_Keep practicing!_"

                        return title, explanation, examples, practice, pitfalls, next_steps, "✅ Lesson ready!"
                    except Exception as e:
                        return "", "", "", "", "", "", f"❌ Generation failed: {str(e)}"

                generate_btn.click(
                    fn=generate_lesson,
                    inputs=[user_id, language, topic, level, api_base],
                    outputs=[
                        lesson_title, lesson_explanation,
                        examples_md, practice_md,
                        pitfalls_md, next_steps_md,
                        status_box
                    ]
                )

                gr.Markdown("**Tip:** Good topics: *\"definite articles\"*, *\"ser vs estar\"*, *\"ordering at a restaurant\"*")

            # === Tab 4: Activity & Reflections ===
            with gr.Tab("📝 Activity & Reflections"):
                gr.Markdown("Log a study session and get an AI-powered reflection on your recent learning.")

                with gr.Row():
                    log_btn = gr.Button("📌 Log Study Session + Get Reflection", variant="primary")
                    observe_btn = gr.Button("🧠 Get Reflection Only")

                observation_md = gr.Markdown(label="AI Reflection")

                def format_observation(obs: dict) -> str:
                    if not obs or "error" in obs:
                        return f"**Error:** {obs.get('error', 'Unknown error')}"
                    md = f"### {obs.get('summary', '')}\n\n"
                    if obs.get("strengths"):
                        md += "**Strengths:**\n" + "\n".join([f"- {s}" for s in obs["strengths"]]) + "\n\n"
                    if obs.get("areas_for_improvement"):
                        md += "**Areas for Improvement:**\n" + "\n".join([f"- {s}" for s in obs["areas_for_improvement"]]) + "\n\n"
                    if obs.get("suggested_next_steps"):
                        md += "**Suggested Next Steps:**\n" + "\n".join([f"- {s}" for s in obs["suggested_next_steps"]])
                    return md

                def get_reflection(user_id_val, base_url):
                    client = LinguaForgeClient(base_url)
                    try:
                        obs = client.get_observation(user_id_val)
                        return format_observation(obs)
                    except Exception as e:
                        return f"**Error:** {str(e)}"

                observe_btn.click(
                    fn=get_reflection,
                    inputs=[user_id, api_base],
                    outputs=[observation_md]
                )

                def log_and_get_reflection(user_id_val, base_url):
                    client = LinguaForgeClient(base_url)
                    try:
                        client.log_session(
                            user_id_val,
                            "study",
                            {"source": "Gradio UI"},
                            duration_minutes=15
                        )
                        obs = client.get_observation(user_id_val)
                        return format_observation(obs), "✅ Session logged successfully!"
                    except Exception as e:
                        return f"**Error:** {str(e)}", f"❌ Failed: {str(e)}"

                log_btn.click(
                    fn=log_and_get_reflection,
                    inputs=[user_id, api_base],
                    outputs=[observation_md, status_box]
                )

            # === Tab 5: Admin - PDF Ingestion (RAG Seeding) ===
            with gr.Tab("⚙️ Admin - Seed Languages (RAG)"):
                gr.Markdown("""
                ### Admin: Ingest PDFs for RAG Grounding

                Upload CEFR or reference PDFs for a language. These files will be used by the Lesson Generator.

                **Warning:** This is an admin area. Only upload trusted PDFs.
                """)

                with gr.Row():
                    admin_lang = gr.Dropdown(
                        ["es", "fr", "de", "it", "pt", "ja", "other"],
                        value="es",
                        label="Language Code",
                        allow_custom_value=True
                    )
                    admin_source_name = gr.Textbox(
                        label="Source Name (optional)",
                        placeholder="CEFR A1 Grammar Notes"
                    )

                uploaded_files = gr.File(
                    label="Upload PDF(s)",
                    file_types=[".pdf"],
                    file_count="multiple"
                )

                ingest_btn = gr.Button("📥 Ingest PDFs into RAG", variant="primary")

                ingest_result = gr.JSON(label="Ingestion Result")

                def do_ingest_pdfs(lang_code: str, source_name: str, files):
                    if not files:
                        return {"error": "No files uploaded"}

                    service = get_pdf_grounding_service()
                    results = []

                    for file in files:
                        try:
                            file_path = file.name if hasattr(file, "name") else str(file)
                            result = service.ingest_language_pdf(
                                lang_code=lang_code.lower(),
                                pdf_path=file_path,
                                source_name=source_name or None
                            )
                            results.append(result)
                        except Exception as e:
                            results.append({"file": getattr(file, 'name', str(file)), "error": str(e)})

                    return {
                        "total_chunks": sum(r.get("chunks_ingested", 0) for r in results if isinstance(r, dict)),
                        "files_processed": len([r for r in results if "error" not in r]),
                        "details": results
                    }

                ingest_btn.click(
                    fn=do_ingest_pdfs,
                    inputs=[admin_lang, admin_source_name, uploaded_files],
                    outputs=[ingest_result]
                )

                gr.Markdown("---")

                with gr.Row():
                    list_langs_btn = gr.Button("🔄 List Ingested Languages")
                    delete_lang = gr.Textbox(label="Language to Delete", placeholder="es")

                current_languages = gr.JSON(label="Currently Ingested Languages")

                def list_ingested_languages():
                    service = get_pdf_grounding_service()
                    langs = service.list_languages()
                    details = {}
                    for lang in langs:
                        info = service.get_collection_info(lang)
                        details[lang] = info
                    return details

                list_langs_btn.click(
                    fn=list_ingested_languages,
                    outputs=[current_languages]
                )

                delete_btn = gr.Button("🗑️ Delete Language Collection", variant="stop")

                def delete_language_collection(lang_code: str):
                    if not lang_code:
                        return {"error": "Please provide a language code"}
                    service = get_pdf_grounding_service()
                    success = service.delete_language_collection(lang_code)
                    return {
                        "deleted": lang_code,
                        "success": success,
                        "remaining_languages": service.list_languages()
                    }

                delete_btn.click(
                    fn=delete_language_collection,
                    inputs=[delete_lang],
                    outputs=[current_languages]
                )

    return demo


# --------------------------- Entry Point ----------------------------- #

if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        theme=gr.themes.Soft()
    )
