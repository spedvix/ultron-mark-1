from __future__ import annotations

import base64
import email
import imaplib
from email.header import decode_header, make_header
from email.message import Message
from email.utils import parsedate_to_datetime
from typing import List, Optional, Tuple

from ...db.repo import Repository
from ...settings import settings
from ...utils.logging import get_logger, mask_email
from ..types import EmailMessage
from .base import EmailConnector

logger = get_logger(__name__)


class IMAPXOauthConnector(EmailConnector):
    source_name = "email:imap"

    def __init__(
        self,
        host: Optional[str] = None,
        email_address: Optional[str] = None,
        oauth_token: Optional[str] = None,
        mailbox: str = "INBOX",
    ):
        super().__init__(mailbox=mailbox)
        self.host = host or settings.imap_host
        self.email_address = email_address or settings.imap_email
        self.oauth_token = oauth_token or settings.imap_oauth_token
        if not all([self.host, self.email_address, self.oauth_token]):
            raise ValueError("IMAP host, email, and oauth token must be configured")

    def sync(self, repo: Repository) -> List[EmailMessage]:
        imap = self._connect()
        try:
            imap.select(self.mailbox)
            cursor = self._get_cursor(repo)
            cutoff = self.cutoff_date(self.window_days)
            criteria = f'(SINCE "{cutoff.strftime("%d-%b-%Y")}")'
            status, data = imap.uid("search", None, criteria)
            if status != "OK":
                logger.warning("IMAP search failed with status %s", status)
                return []

            uids = [uid.decode() for uid in data[0].split()]
            if cursor:
                try:
                    uids = [uid for uid in uids if int(uid) > int(cursor)]
                except ValueError:
                    logger.debug("Non-numeric cursor encountered; processing all messages.")

            messages: List[EmailMessage] = []
            highest_uid: Optional[str] = cursor
            for uid in uids:
                status, fetched = imap.uid("fetch", uid, "(RFC822 X-GM-THRID)")
                if status != "OK" or not fetched:
                    continue
                raw_message = fetched[0][1]
                gm_thread = self._extract_thread_id(fetched)
                parsed = email.message_from_bytes(raw_message)
                subject = self._decode_header(parsed.get("Subject", ""))
                sender = parsed.get("From", "")
                sent_at = parsedate_to_datetime(parsed.get("Date")) if parsed.get("Date") else None
                sent_at = sent_at or self.cutoff_date(0)
                text, html = self._extract_content(parsed)
                if not self.should_keep(subject, text or html or ""):
                    continue
                message = EmailMessage(
                    id=uid,
                    thread_id=gm_thread,
                    subject=subject,
                    sender=sender,
                    date=sent_at,
                    text=text or "",
                    html=html,
                    headers={k: v for k, v in parsed.items()},
                )
                messages.append(message)
                if highest_uid is None or int(uid) > int(highest_uid):
                    highest_uid = uid

            if highest_uid and highest_uid != cursor:
                self._update_cursor(repo, highest_uid)
            logger.info("IMAP sync pulled %s messages", len(messages))
            return messages
        finally:
            try:
                imap.logout()
            except Exception:  # pragma: no cover - best effort cleanup
                pass

    def _connect(self) -> imaplib.IMAP4_SSL:
        logger.info("Connecting to IMAP host %s as %s", self.host, mask_email(self.email_address))
        auth_string = self._xoauth2_string(self.email_address, self.oauth_token)
        client = imaplib.IMAP4_SSL(self.host)
        client.authenticate("XOAUTH2", lambda _: auth_string)
        return client

    @staticmethod
    def _xoauth2_string(user: str, token: str) -> bytes:
        auth_string = f"user={user}\1auth=Bearer {token}\1\1"
        return base64.b64encode(auth_string.encode("utf-8"))

    @staticmethod
    def _decode_header(value: str) -> str:
        try:
            return str(make_header(decode_header(value)))
        except Exception:
            return value

    @staticmethod
    def _extract_content(msg: Message) -> Tuple[str, Optional[str]]:
        plain_parts: List[str] = []
        html_parts: List[str] = []
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                disposition = part.get("Content-Disposition", "")
                if "attachment" in disposition:
                    continue
                payload = part.get_payload(decode=True) or b""
                charset = part.get_content_charset() or "utf-8"
                try:
                    decoded = payload.decode(charset, errors="ignore")
                except LookupError:
                    decoded = payload.decode("utf-8", errors="ignore")
                if content_type == "text/plain":
                    plain_parts.append(decoded)
                elif content_type == "text/html":
                    html_parts.append(decoded)
        else:
            payload = msg.get_payload(decode=True) or b""
            charset = msg.get_content_charset() or "utf-8"
            try:
                decoded = payload.decode(charset, errors="ignore")
            except LookupError:
                decoded = payload.decode("utf-8", errors="ignore")
            if msg.get_content_type() == "text/html":
                html_parts.append(decoded)
            else:
                plain_parts.append(decoded)

        plain = "\n".join(p.strip() for p in plain_parts if p)
        html = "\n".join(html_parts) if html_parts else None
        return plain, html

    @staticmethod
    def _extract_thread_id(fetch_response) -> Optional[str]:
        for item in fetch_response:
            if isinstance(item, tuple) and b"X-GM-THRID" in item[0]:
                parts = item[0].split()
                if parts and parts[-2] == b"X-GM-THRID":
                    return parts[-1].decode()
        return None
