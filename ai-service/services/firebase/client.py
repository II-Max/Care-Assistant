"""
Firebase Client — Ket noi va tuong tac voi Firebase.

Su dung Firebase Admin SDK de:
1. Firestore: Luu conversations, messages, feedback, audit logs
2. Firebase Auth: Xac thuc nguoi dung (Phase 3)

Cau hinh:
- FIREBASE_CREDENTIALS_PATH: Path den file serviceAccountKey.json
- Neu khong co -> chay o che do offline (log ra console)
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    firestore = None
    auth = None

from config import settings

logger = logging.getLogger("firebase_client")


def hash_ip(ip: str) -> str:
    """Hash IP address de luu tru an danh (tranh PII)."""
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


class FirebaseClient:
    """Ket noi va tuong tac voi Firebase Firestore.

    Fallback mode: Neu Firebase chua duoc cau hinh, log ra console.
    """

    def __init__(self):
        self._db = None
        self._auth = None
        self._initialized = False
        self._fallback_mode = False

    @property
    def is_ready(self) -> bool:
        return self._initialized and not self._fallback_mode

    def initialize(self, credential_path: Optional[str] = None) -> bool:
        # Guard: tranh double-init khi ca main.py va chat_service deu goi initialize
        if self._initialized:
            logger.debug("Firebase already initialized, skipping.")
            return self.is_ready

        cred_path = credential_path or settings.FIREBASE_CREDENTIALS_PATH

        if not cred_path:
            logger.warning(
                "Firebase credentials chua duoc cau hinh. "
                "Chay o che do offline."
            )
            self._fallback_mode = True
            self._initialized = True
            return False

        cred_file = Path(cred_path)
        if not cred_file.exists():
            logger.warning(
                f"Khong tim thay file credentials: {cred_path}. Chay offline."
            )
            self._fallback_mode = True
            self._initialized = True
            return False

        if not FIREBASE_AVAILABLE:
            logger.warning(
                "firebase-admin chua duoc cai dat. "
                "Chay: pip install firebase-admin"
            )
            self._fallback_mode = True
            self._initialized = True
            return False

        try:
            # Kiem tra neu app da duoc khoi tao (tranh ValueError)
            try:
                firebase_admin.get_app()
                logger.debug("Firebase app already exists, reusing.")
            except ValueError:
                cred = credentials.Certificate(str(cred_file))
                firebase_admin.initialize_app(cred)

            self._db = firestore.client()
            self._auth = auth
            self._initialized = True
            self._fallback_mode = False
            logger.info(f"Firebase initialized: {cred_file.name}")
            return True
        except Exception as e:
            logger.error(f"Firebase init failed: {e}")
            self._fallback_mode = True
            self._initialized = True
            return False

    # --- Conversations ---

    def create_conversation(self, conversation_data: dict) -> Optional[str]:
        if self._fallback_mode:
            self._log_fallback("create_conversation", conversation_data)
            return None
        try:
            doc_ref = self._db.collection("conversations").document()
            doc_ref.set({**conversation_data, "created_at": firestore.SERVER_TIMESTAMP})
            logger.info(f"Conversation created: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"create_conversation failed: {e}")
            return None

    def update_conversation(self, conversation_id: str, updates: dict) -> bool:
        if self._fallback_mode:
            self._log_fallback("update_conversation", {"id": conversation_id, **updates})
            return False
        try:
            self._db.collection("conversations").document(conversation_id).update(updates)
            return True
        except Exception as e:
            logger.error(f"update_conversation failed: {e}")
            return False

    def get_conversation(self, conversation_id: str) -> Optional[dict]:
        if self._fallback_mode:
            return None
        try:
            doc = self._db.collection("conversations").document(conversation_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            logger.error(f"get_conversation failed: {e}")
            return None

    # --- Messages ---

    def add_message(self, conversation_id: str, message_data: dict) -> Optional[str]:
        if self._fallback_mode:
            self._log_fallback("add_message", {"conversation_id": conversation_id, **message_data})
            return None
        try:
            doc_ref = (
                self._db.collection("conversations")
                .document(conversation_id)
                .collection("messages")
                .document()
            )
            doc_ref.set({**message_data, "created_at": firestore.SERVER_TIMESTAMP})
            return doc_ref.id
        except Exception as e:
            logger.error(f"add_message failed: {e}")
            return None

    def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> list:
        if self._fallback_mode:
            return []
        try:
            docs = (
                self._db.collection("conversations")
                .document(conversation_id)
                .collection("messages")
                .order_by("created_at")
                .limit(limit)
                .stream()
            )
            return [{"id": d.id, **d.to_dict()} for d in docs]
        except Exception as e:
            logger.error(f"get_conversation_messages failed: {e}")
            return []

    # --- Feedback ---

    def add_feedback(self, feedback_data: dict) -> Optional[str]:
        if self._fallback_mode:
            self._log_fallback("add_feedback", feedback_data)
            return None
        try:
            doc_ref = self._db.collection("feedback").document()
            doc_ref.set({**feedback_data, "created_at": firestore.SERVER_TIMESTAMP})
            return doc_ref.id
        except Exception as e:
            logger.error(f"add_feedback failed: {e}")
            return None

    def get_conversation_feedback(self, conversation_id: str) -> list:
        if self._fallback_mode:
            return []
        try:
            docs = (
                self._db.collection("feedback")
                .where("conversation_id", "==", conversation_id)
                .stream()
            )
            return [{"id": d.id, **d.to_dict()} for d in docs]
        except Exception as e:
            logger.error(f"get_conversation_feedback failed: {e}")
            return []

    # --- Audit Logs ---

    def add_audit_log(self, log_data: dict) -> Optional[str]:
        if self._fallback_mode:
            self._log_fallback("audit_log", log_data)
            return None
        try:
            doc_ref = self._db.collection("audit_logs").document()
            doc_ref.set({**log_data, "created_at": firestore.SERVER_TIMESTAMP})
            return doc_ref.id
        except Exception as e:
            logger.error(f"audit_log failed: {e}")
            return None

    def query_audit_logs(
        self, event_type=None, risk_level=None,
        emergency_only=False, start_time=None, limit=100
    ) -> list:
        if self._fallback_mode:
            return []
        try:
            query = self._db.collection("audit_logs")
            if event_type:
                query = query.where("event_type", "==", event_type)
            if risk_level:
                query = query.where("risk_level", "==", risk_level)
            if emergency_only:
                query = query.where("emergency_triggered", "==", True)
            if start_time:
                query = query.where("timestamp", ">=", start_time)
            docs = (
                query.order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            return [{"id": d.id, **d.to_dict()} for d in docs]
        except Exception as e:
            logger.error(f"query_audit_logs failed: {e}")
            return []

    # --- Emergency Logs ---

    def add_emergency_log(self, log_data: dict) -> Optional[str]:
        if self._fallback_mode:
            self._log_fallback("emergency_log", log_data)
            return None
        try:
            doc_ref = self._db.collection("emergency_logs").document()
            doc_ref.set({**log_data, "created_at": firestore.SERVER_TIMESTAMP})
            return doc_ref.id
        except Exception as e:
            logger.error(f"emergency_log failed: {e}")
            return None

    def get_recent_emergencies(self, hours: int = 24, limit: int = 50) -> list:
        if self._fallback_mode:
            return []
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            docs = (
                self._db.collection("emergency_logs")
                .where("timestamp", ">=", since)
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            return [{"id": d.id, **d.to_dict()} for d in docs]
        except Exception as e:
            logger.error(f"get_recent_emergencies failed: {e}")
            return []

    # --- Bookings (Phase 3) ---

    def create_booking(self, booking_data: dict) -> Optional[str]:
        if self._fallback_mode:
            self._log_fallback("create_booking", booking_data)
            return None
        try:
            idempotency_key = booking_data.get("idempotency_key", "")
            if idempotency_key:
                existing = (
                    self._db.collection("bookings")
                    .where("idempotency_key", "==", idempotency_key)
                    .limit(1)
                    .get()
                )
                if len(existing) > 0:
                    logger.info(f"Booking exists (idempotency): {idempotency_key}")
                    return existing[0].id
            doc_ref = self._db.collection("bookings").document()
            doc_ref.set({**booking_data, "created_at": firestore.SERVER_TIMESTAMP})
            logger.info(f"Booking created: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"create_booking failed: {e}")
            return None

    # --- Auth (Phase 3) ---

    def verify_token(self, id_token: str) -> Optional[dict]:
        if self._fallback_mode or not self._auth:
            return None
        try:
            return self._auth.verify_id_token(id_token)
        except Exception as e:
            logger.error(f"verify_token failed: {e}")
            return None

    def get_user(self, uid: str) -> Optional[dict]:
        if self._fallback_mode or not self._auth:
            return None
        try:
            user = self._auth.get_user(uid)
            return {
                "uid": user.uid, "email": user.email,
                "phone": user.phone_number,
                "display_name": user.display_name, "disabled": user.disabled,
            }
        except Exception as e:
            logger.error(f"get_user failed: {e}")
            return None

    # --- Utilities ---

    def _log_fallback(self, operation: str, data: dict):
        logger.info(
            f"[FALLBACK] {operation}: "
            f"{json.dumps(data, default=str, ensure_ascii=False)[:200]}"
        )

    def get_collection_stats(self) -> dict:
        if self._fallback_mode:
            return {"status": "fallback_mode"}
        stats = {}
        try:
            collections = ["conversations", "feedback", "audit_logs", "emergency_logs", "bookings"]
            for col in collections:
                docs = self._db.collection(col).count().get()
                stats[col] = docs[0].value if docs else 0
            return {"status": "connected", **stats}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Singleton
firebase_client = FirebaseClient()
