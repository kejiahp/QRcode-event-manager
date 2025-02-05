import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import emails
from jinja2 import Template

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent.parent.parent / "templates" / "mail" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    assert settings.emails_enabled, "no provided configuration for email variables"
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER_EMAIL:
        smtp_options["user"] = settings.SMTP_USER_EMAIL
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"send email result: {response}")


def generate_event_invitation_email(
    *,
    fullname: str,
    qrcode_img_url: str,
    event_name: str,
    org_name: str,
    org_contact: str,
) -> EmailData:
    subject = f"✨✨Your Exclusive Invitation to {event_name}✨✨"
    html_content = render_email_template(
        template_name="event_invitation_mail.html",
        context={
            "fullname": fullname,
            "qrcode_img_url": qrcode_img_url,
            "event_name": event_name,
            "organiser_name": org_name,
            "organiser_contact_info": org_contact,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_password_reset_email(*, password_reset_link: str) -> EmailData:
    subject = f"Password Reset Request"
    html_content = render_email_template(
        template_name="reset_password_mail.html",
        context={
            "password_reset_link": password_reset_link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)
