"""
Document Loader — Load và parse tất cả file dữ liệu từ Data/.

Hỗ trợ:
- File JSON (.json): parse array of objects với title + content
- File Markdown (.md): parse heading + body content
"""

import json
import re
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from config import settings


@dataclass
class Document:
    """Một tài liệu đã được parse."""
    title: str
    content: str
    source_url: str = ""
    source_file: str = ""
    metadata: dict = field(default_factory=dict)


class DocumentLoader:
    """Load và parse tất cả documents từ Data directory."""

    def __init__(self, data_dir: Optional[str] = None):
        requested_dir = Path(data_dir or settings.DATA_DIR)
        approved_dir = Path(settings.KNOWLEDGE_APPROVED_DIR)
        self.data_dir = (
            approved_dir
            if not data_dir and approved_dir.exists() and any(approved_dir.iterdir())
            else requested_dir
        )

    @staticmethod
    def _is_supported_markdown(file_path: Path) -> bool:
        """Ignore scraper artifacts that are not answerable hospital knowledge."""
        name = file_path.name
        if "Metadata" in name or "Contacts" in name or "Tables" in name or "Forms" in name or "Links" in name or "Media" in name:
            return False
        return True

    @staticmethod
    def _content_hash(content: str) -> str:
        normalized = re.sub(r"\s+", " ", content).strip().lower()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def load_all(self) -> list[Document]:
        """Load tất cả file .md và .json từ data directory."""
        documents = []

        if not self.data_dir.exists():
            print(f"⚠️  Data directory không tồn tại: {self.data_dir}")
            return documents

        # Load JSON files
        for json_file in self.data_dir.glob("*.json"):
            docs = self._load_json(json_file)
            documents.extend(docs)
            print(f"📄 Loaded JSON: {json_file.name} → {len(docs)} documents")

        # Load Markdown files (bỏ qua những file đã có trong JSON)
        json_titles = {doc.title for doc in documents}
        for md_file in sorted(self.data_dir.glob("*.md")):
            if not self._is_supported_markdown(md_file):
                continue
            docs = self._load_markdown(md_file)
            # Chỉ thêm nếu chưa có trong JSON
            new_docs = [d for d in docs if d.title not in json_titles]
            documents.extend(new_docs)
            if new_docs:
                print(f"📄 Loaded MD: {md_file.name} → {len(new_docs)} documents")

        unique_documents = []
        seen_hashes = set()
        for doc in documents:
            content_hash = self._content_hash(doc.content)
            if content_hash in seen_hashes:
                continue
            seen_hashes.add(content_hash)
            doc.metadata["content_hash"] = content_hash
            unique_documents.append(doc)

        print(f"\n✅ Tổng cộng: {len(unique_documents)} documents loaded")
        return unique_documents

    def _load_json(self, file_path: Path) -> list[Document]:
        """Parse JSON file — format: array of {id, title, url, content: []}."""
        documents = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                data = [data]

            for item in data:
                title = item.get("title", "").strip()
                url = item.get("url", "")
                content_list = item.get("content", [])

                if not content_list or not title:
                    continue

                # Join content array thành text
                content_text = "\n".join(
                    line.strip() for line in content_list if line.strip()
                )

                if len(content_text) < 10:
                    continue

                documents.append(Document(
                    title=title,
                    content=content_text,
                    source_url=url,
                    source_file=file_path.name,
                    metadata={"id": item.get("id", 0)}
                ))

        except Exception as e:
            print(f"❌ Lỗi parse JSON {file_path.name}: {e}")

        return documents

    def _load_markdown(self, file_path: Path) -> list[Document]:
        """Parse Markdown file — extract title từ heading, content từ body."""
        documents = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if len(content) < 50:
                return documents

            # Extract title từ first heading
            title_match = re.match(r"^#\s+(.+)", content)
            title = title_match.group(1).strip() if title_match else file_path.stem

            # Extract source URL từ blockquote
            url_match = re.search(r"\*\*Nguồn:\*\*\s*(https?://\S+)", content)
            source_url = url_match.group(1) if url_match else ""

            # Clean up content: bỏ heading đầu, bỏ source blockquote
            body = content
            if title_match:
                body = body[title_match.end():].strip()
            body = re.sub(r">\s*\*\*Nguồn:\*\*\s*https?://\S+", "", body).strip()
            body = re.sub(r"^---\s*$", "", body, flags=re.MULTILINE).strip()

            if len(body) < 20:
                return documents

            documents.append(Document(
                title=title,
                content=body,
                source_url=source_url,
                source_file=file_path.name
            ))

        except Exception as e:
            print(f"❌ Lỗi parse MD {file_path.name}: {e}")

        return documents


if __name__ == "__main__":
    loader = DocumentLoader()
    docs = loader.load_all()
    for doc in docs:
        print(f"\n📋 {doc.title}")
        print(f"   URL: {doc.source_url}")
        print(f"   Length: {len(doc.content)} chars")
        print(f"   Preview: {doc.content[:100]}...")
