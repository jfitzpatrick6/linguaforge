"""
Tests for the PDF Grounding / RAG service.

These tests create small synthetic PDFs on the fly using pymupdf so they
run reliably without shipping binary fixtures.
"""
import pytest
from pathlib import Path
import tempfile
import fitz  # pymupdf

from app.services.pdf_grounding import PDFGrounding, _chunk_text


def _make_temp_pdf(pages: list[str]) -> str:
    """Create a temporary PDF with the given page texts. Returns the path."""
    fd, path = tempfile.mkstemp(suffix=".pdf")
    import os
    os.close(fd)

    doc = fitz.open()
    for page_text in pages:
        page = doc.new_page()
        page.insert_text((72, 72), page_text, fontsize=11)

    doc.save(path)
    doc.close()
    return path


@pytest.fixture
def grounding_service(tmp_path):
    """Fresh grounding service pointing at a temp Chroma directory."""
    service = PDFGrounding(
        persist_dir=str(tmp_path / "chroma_test"),
        embedding_model="all-MiniLM-L6-v2",  # small & fast for tests
    )
    yield service


def test_chunk_text_basic():
    text = "Paragraph one.\n\nParagraph two is longer and talks about things.\n\n" + ("More content. " * 30)
    chunks = _chunk_text(text, chunk_size=120, overlap=30)
    assert len(chunks) >= 2
    assert all(len(c) > 20 for c in chunks)


def test_ingest_and_query_basic(grounding_service):
    service = grounding_service

    # Create a tiny test PDF
    pdf_pages = [
        "Hello and welcome to basic Spanish greetings. Buenos días means good morning.",
        "Adiós is goodbye. Por favor means please. Gracias is thank you.",
        "Numbers are important too. Uno, dos, tres. Cuatro, cinco, seis.",
    ]
    pdf_path = _make_temp_pdf(pdf_pages)

    try:
        result = service.ingest_language_pdf("es", pdf_path, source_name="Test Spanish Basics")
        assert result["lang"] == "es"
        assert result["chunks_ingested"] > 0

        # Query for something that should match
        hits = service.query_grounding("es", "how do you say good morning", k=3)
        assert len(hits) > 0
        assert any("Buenos" in h["text"] or "good morning" in h["text"].lower() for h in hits)

        # Check metadata
        first = hits[0]
        assert first["metadata"]["lang"] == "es"
        assert "page" in first["metadata"]
        assert first["score"] > 0.1
    finally:
        Path(pdf_path).unlink(missing_ok=True)


def test_query_with_where_filter(grounding_service):
    service = grounding_service

    pdf1 = _make_temp_pdf(["Food vocabulary: manzana is apple, pan is bread."])
    pdf2 = _make_temp_pdf(["Numbers again: siete, ocho, nueve, diez."])

    try:
        service.ingest_language_pdf("es", pdf1, source_name="Food PDF")
        service.ingest_language_pdf("es", pdf2, source_name="Numbers PDF")

        # Filter by source
        food_results = service.query_grounding(
            "es",
            "what is apple",
            k=5,
            where={"source": "Food PDF"},
        )
        assert len(food_results) > 0
        assert all(r["metadata"]["source"] == "Food PDF" for r in food_results)
    finally:
        Path(pdf1).unlink(missing_ok=True)
        Path(pdf2).unlink(missing_ok=True)


def test_collection_info_and_reset(grounding_service):
    service = grounding_service

    pdf_path = _make_temp_pdf(["Test content for collection management."])
    try:
        service.ingest_language_pdf("de", pdf_path)
        info = service.get_collection_info("de")
        assert info["document_count"] > 0

        deleted = service.delete_language_collection("de")
        assert deleted is True

        info_after = service.get_collection_info("de")
        assert info_after.get("document_count", 0) == 0 or "error" in info_after
    finally:
        Path(pdf_path).unlink(missing_ok=True)
