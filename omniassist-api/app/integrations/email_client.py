"""Email integration: SMTP sending + inbound email parsing/classification."""
from __future__ import annotations

import smtplib
from email.message import EmailMessage
from email.utils import parseaddr

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("email")


def send_email(to: str, subject: str, body: str, html: str | None = None) -> None:
    """Send an email via SMTP (Gmail or any SMTP relay)."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("smtp_not_configured", to=to)
        return
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
    logger.info("email_sent", to=to, subject=subject)


def parse_inbound(raw: dict) -> dict:
    """Normalize an inbound email payload (Gmail push / webhook) into a canonical shape."""
    from_field = raw.get("from", "")
    name, address = parseaddr(from_field)
    return {
        "from_name": name or (address.split("@")[0] if address else "Customer"),
        "from_email": address,
        "subject": raw.get("subject", "(no subject)"),
        "body": _clean_body(raw.get("body", raw.get("text", ""))),
        "thread_id": raw.get("threadId") or raw.get("thread_id"),
        "message_id": raw.get("id") or raw.get("message_id"),
    }


def _clean_body(body: str) -> str:
    """Strip quoted reply history so the AI sees only the new content."""
    lines = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith(">") or stripped.startswith("On ") and "wrote:" in stripped:
            break
        lines.append(line)
    return "\n".join(lines).strip()
