"""
Document Loader — Load va parse file tu knowledge/approved/ hoac Data/.

Tinh nang:
- Load MD + JSON files
- Manifest-based expiry validation (tu knowledge/approved/manifest.json)
- Fallback: inline **Het han:** metadata trong content
- Deduplicate content
- Uu tien knowledge/approved/
"""

import json
import re
import hashlib
import logging
from datetime import datetime, date
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from config import settings

logger = logging.getLogger("document_loader")


@dataclass
class Document:
    """Mot tai lieu da duoc parse."""
    title: str
    content: str
    source_url: str = ""
    source_file: str = ""
    metadata: dict = field(default_factory=dict)


class DocumentLoader:
    """Load va parse documents. Uu tien knowledge/approved/."""

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            approved_dir = Path(settings.KNOWLEDGE_APPROVED_DIR)
            if approved_dir.exists() and list(approved_dir.glob("*.md")):
                self.data_dir = approved_dir
            else:
                self.data_dir = Path(settings.DATA_DIR)
        self._load_manifest()

    def _load_manifest(self):
        """Load manifest.json tu knowledge/approved/."""
        self._manifest = {}
        manifest_path = self.data_dir / "manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for doc in data.get("documents", []):
                    self._manifest[doc["filename"]] = doc
                logger.info(f"Manifest loaded: {len(self._manifest)} documents")
            except Exception as e:
                logger.warning(f"Manifest load failed: {e}")

    def _is_expired(self, file_path: Path, content: str = "") -> bool:
        """Kiem tra tai lieu het han.

        Checks (theo thu tu uu tien):
        1. Manifest expires_at
        2. Inline **Het han:** metadata trong content
        """
        manifest_entry = self._manifest.get(file_path.name)
        if manifest_entry:
            expires_at = manifest_entry.get("expires_at", "")
            if expires_at:
                try:
                    expiry_date = datetime.strptime(expires_at, "%Y-%m-%d").date()
                    if expiry_date < date.today():
                        logger.info(f"Expired (manifest): {file_path.name} -> {expires_at}")
                        return True
                    return False
                except ValueError:
                    pass

        if content:
            match = re.search(r"\*\*Het han:\*\*\s*(\d{2}/\d{2}/\d{4})", content)
            if match:
                try:
                    expiry_date = datetime.strptime(match.group(1), "%d/%m/%Y").date()
                    return expiry_date < date.today()
                except ValueError:
                    pass

        return False

    @staticmethod
    def _is_supported_markdown(file_path: Path) -> bool:
        name = file_path.name
        keywords = ("Metadata", "Contacts", "Tables", "Forms", "Links", "Media")
        if any(k in name for k in keywords):
            return False
        return True

    @staticmethod
    def _content_hash(content: str) -> str:
        normalized = re.sub(r"\s+", " ", content).strip().lower()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def load_all(self) -> list[Document]:
        documents = []

        if not self.data_dir.exists():
            logger.warning(f"Data directory khong ton tai: {self.data_dir}")
            return documents

        for json_file in self.data_dir.glob("*.json"):
            if json_file.name == "manifest.json":
                continue
            docs = self._load_json(json_file)
            documents.extend(docs)

        json_titles = {doc.title for doc in documents}
        for md_file in sorted(self.data_dir.glob("*.md")):
            if not self._is_supported_markdown(md_file):
                continue
            docs = self._load_markdown(md_file)
            valid_docs = []
            for d in docs:
                with open(md_file, "r", encoding="utf-8") as f:
                    full_content = f.read()
                if self._is_expired(md_file, full_content):
                    logger.info(f"Expired: {d.title} (bo qua)")
                    continue
                valid_docs.append(d)
            new_docs = [d for d in valid_docs if d.title not in json_titles]
            documents.extend(new_docs)

        unique_documents = []
        seen_hashes = set()
        for doc in documents:
            content_hash = self._content_hash(doc.content)
            if content_hash in seen_hashes:
                continue
            seen_hashes.add(content_hash)
            doc.metadata["content_hash"] = content_hash
            unique_documents.append(doc)

        logger.info(f"Loaded {len(unique_documents)} documents from {self.data_dir.name}")
        return unique_documents

    def _load_json(self, file_path: Path) -> list[Document]:
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
                content_text = "\n".join(line.strip() for line in content_list if line.strip())
                if len(content_text) < 10:
                    continue
                documents.append(Document(
                    title=title, content=content_text,
                    source_url=url, source_file=file_path.name,
                    metadata={"id": item.get("id", 0)}
                ))
        except Exception as e:
            logger.error(f"Parse JSON {file_path.name} failed: {e}")
        return documents

    def _load_markdown(self, file_path: Path) -> list[Document]:
        documents = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if len(content) < 50:
                return documents
            title_match = re.match(r"^#\s+(.+)", content)
            title = title_match.group(1).strip() if title_match else file_path.stem
            url_match = re.search(r"(?:🔗\s*URL:\s*|\*\*Nguồn:\*\*\s*)(https?://\S+)", content)
            source_url = url_match.group(1) if url_match else ""
            body = content
            if title_match:
                body = body[title_match.end():].strip()
            body = re.sub(r">\s*(?:🔗\s*URL:\s*|\*\*Nguồn:\*\*\s*)https?://\S+", "", body).strip()
            body = re.sub(r"^---\s*$", "", body, flags=re.MULTILINE).strip()
            if len(body) < 20:
                return documents
            documents.append(Document(
                title=title, content=body,
                source_url=source_url, source_file=file_path.name
            ))
        except Exception as e:
            logger.error(f"Parse MD {file_path.name} failed: {e}")
        return documents


if __name__ == "__main__":
    loader = DocumentLoader()
    docs = loader.load_all()
    for doc in docs:
        print(f"  - {doc.title} ({len(doc.content)} chars)")
