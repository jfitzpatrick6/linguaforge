"""
PDF Grounding Service — Local RAG for language learning content.

Provides ingestion of CEFR/reference PDFs per language and semantic retrieval
of relevant chunks for the LessonGeneratorAgent (and other consumers).

Design goals:
- Fully local (no external embedding APIs)
- Persistent vector store (Chroma at CHROMA_PATH)
- Real PDF parsing via pymupdf (fitz)
- Good multilingual chunking + rich metadata
- Easy to use from agents and routers

Admin / write protection:
    Ingestion methods are powerful. Protection should be applied at the
    router layer (FastAPI Depends + admin check), not inside this service.
    The old monkey-patched decorator has been removed.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any, Optional
import re

import chromadb
from chromadb.utils import embedding_functions
import fitz  # PyMuPDF

from app.core.config import settings


def _clean_text(text: str) -> str:
    """Basic cleanup of extracted PDF text."""
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_structured_blocks(page: fitz.Page) -> List[Dict[str, Any]]:
    """
    Extract text blocks from a page while trying to identify headings.

    Uses fitz's dict output for richer structure than plain text.
    """
    blocks = []
    page_dict = page.get_text("dict")

    current_heading = None

    for block in page_dict.get("blocks", []):
        if "lines" not in block:
            continue  # Skip images / non-text blocks

        block_text = ""
        max_font_size = 0
        is_bold = False

        for line in block["lines"]:
            line_text = "".join([span["text"] for span in line["spans"]])
            block_text += line_text + " "

            for span in line["spans"]:
                size = span.get("size", 0)
                if size > max_font_size:
                    max_font_size = size
                    is_bold = "bold" in span.get("font", "").lower() or span.get("flags", 0) & 16 != 0

        block_text = _clean_text(block_text)

        if not block_text:
            continue

        # Simple heuristic for headings
        is_likely_heading = (
            max_font_size > 12 and
            (len(block_text) < 120) and
            (is_bold or max_font_size > 14)
        )

        if is_likely_heading:
            current_heading = block_text.strip()

        blocks.append({
            "text": block_text.strip(),
            "bbox": block.get("bbox"),
            "is_heading": is_likely_heading,
            "heading": current_heading,
            "font_size": max_font_size,
        })

    return blocks


def _chunk_text(
    text: str,
    chunk_size: int = 450,
    overlap: int = 80,
) -> List[str]:
    """
    Split text into overlapping chunks.

    Tries to respect paragraph boundaries when possible.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: List[str] = []
    current_chunk: List[str] = []
    current_len = 0

    for para in paragraphs:
        para_len = len(para)

        if current_len + para_len + 1 > chunk_size and current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunks.append(chunk_text)

            # Overlap: keep the last part of the previous chunk
            if overlap > 0 and len(chunk_text) > overlap:
                overlap_text = chunk_text[-overlap:]
                current_chunk = [overlap_text]
                current_len = len(overlap_text)
            else:
                current_chunk = []
                current_len = 0

        current_chunk.append(para)
        current_len += para_len + 2

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    # Fallback: hard split any remaining huge chunks
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= chunk_size * 1.5:
            final_chunks.append(chunk)
        else:
            for i in range(0, len(chunk), chunk_size - overlap):
                final_chunks.append(chunk[i : i + chunk_size])

    # Final quality filter
    return [c.strip() for c in final_chunks if len(c.strip()) > 25]


class PDFGrounding:
    """
    Local PDF ingestion + semantic retrieval service.

    Collections are named: grounding_{lang_code}
    (e.g. "grounding_es", "grounding_fr")
    """

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        embedding_model: Optional[str] = None,
    ):
        self.persist_dir = persist_dir or settings.CHROMA_PATH
        self.embedding_model = embedding_model or settings.EMBEDDING_MODEL

        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=self.persist_dir)

        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.embedding_model
        )

    def _get_collection(self, lang_code: str):
        """Get or create the collection for a language with proper embedding function."""
        collection_name = f"grounding_{lang_code.lower()}"
        return self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------ #
    # Ingestion
    # ------------------------------------------------------------------ #

    def ingest_language_pdf(
        self,
        lang_code: str,
        pdf_path: str,
        *,
        source_name: Optional[str] = None,
        reset_collection: bool = False,
    ) -> Dict[str, Any]:
        """
        Parse a PDF and ingest its content into the language-specific collection.

        Args:
            lang_code: Target language code (e.g. "es", "fr", "de")
            pdf_path: Path to the PDF file
            source_name: Human-friendly name for the source (defaults to filename)
            reset_collection: If True, delete existing collection for this lang first

        Returns:
            Summary dict with counts
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if reset_collection:
            collection_name = f"grounding_{lang_code.lower()}"
            try:
                self.client.delete_collection(collection_name)
            except Exception:
                pass  # collection didn't exist

        collection = self._get_collection(lang_code)

        doc = fitz.open(pdf_file)
        source_label = source_name or pdf_file.name
        page_count = len(doc)

        total_chunks = 0
        added_ids: List[str] = []

        for page_num, page in enumerate(doc, start=1):
            structured_blocks = _extract_structured_blocks(page)

            # Group blocks into logical sections based on headings
            page_text_with_context = []
            current_section = None

            for block in structured_blocks:
                if block["is_heading"]:
                    current_section = block["text"]

                text = block["text"]
                if current_section and not block["is_heading"]:
                    text = f"[{current_section}] {text}"

                page_text_with_context.append(text)

            full_page_text = "\n\n".join(page_text_with_context)
            cleaned = _clean_text(full_page_text)

            if not cleaned:
                continue

            chunks = _chunk_text(cleaned)

            for idx, chunk in enumerate(chunks):
                chunk_id = f"{lang_code}:{pdf_file.stem}:p{page_num}:c{idx}"

                # Try to extract the most relevant heading for this chunk
                chunk_heading = None
                for block in structured_blocks:
                    if block["heading"] and block["heading"] in chunk:
                        chunk_heading = block["heading"]
                        break

                metadata = {
                    "lang": lang_code.lower(),
                    "source": source_label,
                    "source_path": str(pdf_file),
                    "page": page_num,
                    "chunk_index": idx,
                    "heading": chunk_heading,
                }

                collection.add(
                    documents=[chunk],
                    metadatas=[metadata],
                    ids=[chunk_id],
                )
                added_ids.append(chunk_id)
                total_chunks += 1

        doc.close()

        headings_detected = 0
        if 'structured_blocks' in locals():
            headings_detected = len([b for b in structured_blocks if b.get("is_heading")])

        return {
            "lang": lang_code,
            "source": source_label,
            "pages": page_count,
            "chunks_ingested": total_chunks,
            "collection": collection.name,
            "headings_detected": headings_detected,
        }

    # ------------------------------------------------------------------ #
    # Retrieval
    # ------------------------------------------------------------------ #

    def query_grounding(
        self,
        lang_code: str,
        query: str,
        k: int = 6,
        *,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search against the language grounding collection.

        Returns rich results with text + metadata (page, source, etc.).
        """
        collection = self._get_collection(lang_code)

        results = collection.query(
            query_texts=[query],
            n_results=k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        output: List[Dict[str, Any]] = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            item = {
                "text": doc,
                "metadata": meta or {},
                "score": 1 - (dist or 0.0),  # convert distance to similarity-ish score
            }
            output.append(item)

        return output

    def get_collection_info(self, lang_code: str) -> Dict[str, Any]:
        """Return basic stats about a language collection."""
        try:
            collection = self._get_collection(lang_code)
            count = collection.count()
            return {
                "lang": lang_code,
                "collection": collection.name,
                "document_count": count,
                "embedding_model": self.embedding_model,
            }
        except Exception as e:
            return {"lang": lang_code, "error": str(e)}

    # ------------------------------------------------------------------ #
    # Maintenance
    # ------------------------------------------------------------------ #

    def delete_language_collection(self, lang_code: str) -> bool:
        """Completely remove the grounding collection for a language."""
        collection_name = f"grounding_{lang_code.lower()}"
        try:
            self.client.delete_collection(collection_name)
            return True
        except Exception:
            return False

    def list_languages(self) -> List[str]:
        """Return language codes that currently have grounding collections."""
        collections = self.client.list_collections()
        langs = []
        for col in collections:
            if col.name.startswith("grounding_"):
                langs.append(col.name.replace("grounding_", ""))
        return sorted(langs)

    def ingest_pdfs_from_directory(
        self,
        lang_code: str,
        directory: str,
        *,
        source_prefix: Optional[str] = None,
        reset_collection: bool = False,
    ) -> Dict[str, Any]:
        """
        Ingest all PDFs in a directory for a given language.

        Useful for bulk-seeding a language with many reference materials.
        """
        dir_path = Path(directory)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        pdf_files = sorted(dir_path.glob("*.pdf"))
        if not pdf_files:
            return {
                "lang": lang_code,
                "directory": str(dir_path),
                "pdfs_found": 0,
                "total_chunks": 0,
            }

        total_chunks = 0
        results = []

        for pdf_file in pdf_files:
            source_name = f"{source_prefix}: {pdf_file.name}" if source_prefix else pdf_file.name
            try:
                result = self.ingest_language_pdf(
                    lang_code=lang_code,
                    pdf_path=str(pdf_file),
                    source_name=source_name,
                    reset_collection=reset_collection if pdf_file == pdf_files[0] else False,
                )
                total_chunks += result.get("chunks_ingested", 0)
                results.append(result)
            except Exception as e:
                results.append({
                    "source": pdf_file.name,
                    "error": str(e)
                })

        return {
            "lang": lang_code,
            "directory": str(dir_path),
            "pdfs_found": len(pdf_files),
            "pdfs_processed": len([r for r in results if "error" not in r]),
            "total_chunks_ingested": total_chunks,
            "details": results,
        }


# Default global instance (configured from settings)
pdf_grounding_service = PDFGrounding()


def get_pdf_grounding_service() -> PDFGrounding:
    """Return the configured global PDFGrounding instance."""
    return pdf_grounding_service
