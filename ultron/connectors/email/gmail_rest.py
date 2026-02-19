from __future__ import annotations

import base64
import json
from typing import List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

from ...db.repo import Repository
from ...settings import settings
from ...utils.logging import get_logger
from ..types import EmailMessage
from .base import EmailConnector

logger = get_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailRestConnector(EmailConnector):
    source_name = "email:gmail"

    def __init__(
        self,
        token_path: Optional[str] = None,
        credentials_path: Optional[str] = None,
        user_id: str = "me",
    ):
        super().__init__(mailbox="INBOX")
        self.token_path = token_path or settings.gmail_token_file
        self.credentials_path = credentials_path or settings.gmail_credentials_file
        self.user_id = user_id
        if not self.token_path:
            raise ValueError("Gmail token file must be configured for GmailRestConnector")

    def sync(self, repo: Repository) -> List[EmailMessage]:
        service = self._build_service()
        cursor_state = repo.get_sync_cursor(self.source_name)
        history_id = cursor_state.cursor if cursor_state else None
        messages: List[EmailMessage] = []
        latest_history: Optional[str] = history_id

        try:
            if history_id:
                messages.extend(self._sync_from_history(service, history_id))
                latest_history = self._get_latest_history(service) or history_id
            else:
                messages.extend(self._initial_pull(service))
                latest_history = self._get_latest_history(service)
        except HttpError as exc:
            if exc.resp.status in (401, 403):
                logger.error("Gmail API authentication error: %s", exc)
                raise
            logger.warning("Gmail API error %s - falling back to initial pull", exc)
            messages.extend(self._initial_pull(service))
            latest_history = self._get_latest_history(service)

        pruned = [msg for msg in messages if self.should_keep(msg.subject, msg.text or msg.html or "")]
        if latest_history:
            extra = json.dumps({"history_id": latest_history})
            repo.set_sync_cursor(self.source_name, latest_history, extra=extra)
        logger.info("Gmail sync produced %s relevant messages", len(pruned))
        return pruned

    def _build_service(self):
        creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        return build("gmail", "v1", credentials=creds, cache_discovery=False)

    def _sync_from_history(self, service, history_id: str) -> List[EmailMessage]:
        messages: List[EmailMessage] = []
        request = service.users().history().list(
            userId=self.user_id,
            startHistoryId=history_id,
            historyTypes=["messageAdded"],
        )
        while request is not None:
            history_response = request.execute()
            for history in history_response.get("history", []):
                for record in history.get("messagesAdded", []):
                    message_id = record["message"]["id"]
                    message = self._fetch_message(service, message_id)
                    if message:
                        messages.append(message)
            request = service.users().history().list_next(previous_request=request, previous_response=history_response)
        return messages

    def _initial_pull(self, service) -> List[EmailMessage]:
        cutoff = self.cutoff_date(self.window_days).strftime("%Y/%m/%d")
        query = f"after:{cutoff} ({' OR '.join(self._keyword_query_terms())})"
        request = service.users().messages().list(userId=self.user_id, q=query, maxResults=100)
        messages: List[EmailMessage] = []
        while request is not None:
            response = request.execute()
            for item in response.get("messages", []):
                message = self._fetch_message(service, item["id"])
                if message:
                    messages.append(message)
            request = service.users().messages().list_next(previous_request=request, previous_response=response)
        return messages

    def _get_latest_history(self, service) -> Optional[str]:
        profile = service.users().getProfile(userId=self.user_id).execute()
        return str(profile.get("historyId")) if profile.get("historyId") else None

    def _fetch_message(self, service, message_id: str) -> Optional[EmailMessage]:
        msg = service.users().messages().get(userId=self.user_id, id=message_id, format="full").execute()
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        subject = headers.get("Subject", "")
        sender = headers.get("From", "")
        date_header = headers.get("Date")
        date = self.cutoff_date(0)
        if date_header:
            from email.utils import parsedate_to_datetime  # noqa

            try:
                date = parsedate_to_datetime(date_header)
            except (TypeError, ValueError):
                pass
        text, html = self._extract_parts(msg.get("payload", {}))
        return EmailMessage(
            id=msg["id"],
            thread_id=msg.get("threadId"),
            subject=subject,
            sender=sender,
            date=date,
            text=text,
            html=html,
            headers=headers,
        )

    @staticmethod
    def _extract_parts(payload) -> tuple[str, Optional[str]]:
        text_parts: List[str] = []
        html_content: Optional[str] = None

        def walk(part):
            nonlocal html_content
            body = part.get("body", {})
            data = body.get("data")
            if not data:
                for child in part.get("parts", []) or []:
                    walk(child)
                return
            padding = "=" * (-len(data) % 4)
            decoded_bytes = base64.urlsafe_b64decode(data + padding)
            charset = "utf-8"
            params = part.get("headers", [])
            for header in params:
                if header.get("name", "").lower() == "content-type":
                    parts = header.get("value", "").split("charset=")
                    if len(parts) == 2:
                        charset = parts[1].strip().strip('"')
            try:
                decoded = decoded_bytes.decode(charset, errors="ignore")
            except LookupError:
                decoded = decoded_bytes.decode("utf-8", errors="ignore")
            mime = part.get("mimeType")
            if mime == "text/html":
                html_content = decoded
            else:
                text_parts.append(decoded)

        walk(payload)
        text = "\n".join(text_parts)
        return text, html_content

    @staticmethod
    def _keyword_query_terms() -> List[str]:
        return [
            "subject:(syllabus)",
            "subject:(assignment)",
            "subject:(homework)",
            "subject:(quiz)",
            "subject:(exam)",
            "subject:(deadline)",
            "body:(assignment)",
            "body:(exam)",
        ]
