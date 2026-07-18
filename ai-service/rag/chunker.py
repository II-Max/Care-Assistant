"""
Chunker — Chia documents thành các chunks nhỏ cho RAG pipeline.

Sử dụng semantic chunking: split theo heading/paragraph, giữ metadata.
Tối ưu cho dữ liệu y tế tiếng Việt.
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from config import settings


@dataclass
class Chunk:
    """Một đoạn text nhỏ đã được chunk."""
    text: str
    title: str
    source_url: str = ""
    source_file: str = ""
    chunk_index: int = 0
    section_header: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def display_text(self) -> str:
        """Text để hiển thị khi debug."""
        return f"[{self.title}] {self.text[:80]}..."

    @property
    def embedding_text(self) -> str:
        """Text tối ưu để tạo embedding — bao gồm title + section context."""
        parts = []
        if self.title:
            parts.append(f"Chủ đề: {self.title}")
        if self.section_header:
            parts.append(f"Mục: {self.section_header}")
        parts.append(self.text)
        return "\n".join(parts)


class DocumentChunker:
    """Chia documents thành chunks cho vector indexing."""

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def chunk_documents(self, documents: list) -> list[Chunk]:
        """Chunk tất cả documents."""
        all_chunks = []
        for doc in documents:
            chunks = self._chunk_document(doc)
            all_chunks.extend(chunks)
        print(f"✅ Chunked {len(documents)} documents → {len(all_chunks)} chunks")
        return all_chunks

    def _chunk_document(self, doc) -> list[Chunk]:
        """Chunk một document duy nhất.

        Strategy:
        1. Split theo headings (##, ###) trước
        2. Trong mỗi section, split theo paragraph
        3. Nếu paragraph quá dài, split theo câu
        4. Merge các đoạn nhỏ lại để đạt chunk_size tối ưu
        """
        sections = self._split_by_sections(doc.content)
        chunks = []
        chunk_index = 0

        for section_header, section_text in sections:
            section_chunks = self._split_section(section_text)

            for chunk_text in section_chunks:
                chunk_text = chunk_text.strip()
                if len(chunk_text) < 20:
                    continue

                chunks.append(Chunk(
                    text=chunk_text,
                    title=doc.title,
                    source_url=doc.source_url,
                    source_file=doc.source_file,
                    chunk_index=chunk_index,
                    section_header=section_header,
                    metadata=doc.metadata
                ))
                chunk_index += 1

        return chunks

    def _split_by_sections(self, text: str) -> list[tuple[str, str]]:
        """Split text theo Markdown headings."""
        # Pattern cho ## hoặc ### headings
        heading_pattern = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)

        sections = []
        matches = list(heading_pattern.finditer(text))

        if not matches:
            return [("", text)]

        # Nội dung trước heading đầu tiên
        if matches[0].start() > 0:
            pre_text = text[:matches[0].start()].strip()
            if pre_text:
                sections.append(("", pre_text))

        # Mỗi heading + nội dung sau nó
        for i, match in enumerate(matches):
            header = match.group(2).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()

            if body:
                sections.append((header, body))

        return sections

    def _split_section(self, text: str) -> list[str]:
        """Split section thành chunks tối ưu.

        1. Split theo double newline (paragraphs)
        2. Merge paragraphs nhỏ lại
        3. Split paragraphs quá dài theo câu
        """
        # Estimate token count (~1.5 chars per token cho tiếng Việt)
        char_limit = self.chunk_size * 3  # ~500 tokens * 3 chars ≈ 1500 chars
        overlap_chars = self.chunk_overlap * 3

        paragraphs = re.split(r"\n\s*\n|\n(?=\s*[\-\+\*•·✔️]\s)", text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(para) > char_limit:
                # Paragraph quá dài — split theo câu
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""

                sentences = self._split_sentences(para)
                sent_chunk = ""
                for sent in sentences:
                    if len(sent_chunk) + len(sent) > char_limit:
                        if sent_chunk:
                            chunks.append(sent_chunk)
                        # Overlap: giữ lại phần cuối
                        sent_chunk = sent_chunk[-overlap_chars:] + " " + sent if overlap_chars else sent
                    else:
                        sent_chunk = (sent_chunk + " " + sent).strip() if sent_chunk else sent
                if sent_chunk:
                    chunks.append(sent_chunk)

            elif len(current_chunk) + len(para) > char_limit:
                # Đã đủ chunk size — save current và bắt đầu mới
                if current_chunk:
                    chunks.append(current_chunk)
                # Overlap
                if overlap_chars and current_chunk:
                    current_chunk = current_chunk[-overlap_chars:] + "\n" + para
                else:
                    current_chunk = para
            else:
                current_chunk = (current_chunk + "\n" + para).strip() if current_chunk else para

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """Split text thành các câu tiếng Việt."""
        # Split theo dấu chấm, chấm hỏi, chấm than, dấu chấm phẩy
        sentences = re.split(r"(?<=[.!?;])\s+", text)
        return [s.strip() for s in sentences if s.strip()]


if __name__ == "__main__":
    from document_loader import DocumentLoader

    loader = DocumentLoader()
    docs = loader.load_all()

    chunker = DocumentChunker()
    chunks = chunker.chunk_documents(docs)

    for i, chunk in enumerate(chunks[:5]):
        print(f"\n--- Chunk {i} ---")
        print(f"Title: {chunk.title}")
        print(f"Section: {chunk.section_header}")
        print(f"Length: {len(chunk.text)} chars")
        print(f"Text: {chunk.text[:200]}...")
