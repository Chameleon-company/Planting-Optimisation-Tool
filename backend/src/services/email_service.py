import asyncio
import smtplib
from email.message import EmailMessage

from src.config import settings


# Private sync function that handles SMTP
def _send_email_sync(subject: str, recipient: str, body: str, html_body: str | None = None) -> None:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from_email
    message["To"] = recipient
    message.set_content(body)
    if html_body:
        message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)


# Async function that offloads to thread pool to prevent blocking
async def send_email(subject: str, recipient: str, body: str, html_body: str | None = None) -> None:
    if settings.TESTING:
        print(f"TEST EMAIL to {recipient} | {subject} | {body}")
        return
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_email_sync, subject, recipient, body, html_body)
