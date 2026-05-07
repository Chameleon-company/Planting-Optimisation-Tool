import httpx

from src.config import settings


async def send_email(subject: str, recipient: str, body: str, html_body: str | None = None) -> None:
    if settings.TESTING:
        print(f"TEST EMAIL to {recipient} | {subject} | {body}")
        return

    payload: dict = {
        "sender": {"name": "Planting Optimisation Tool", "email": settings.smtp_from_email},
        "to": [{"email": recipient}],
        "subject": subject,
        "textContent": body,
    }
    if html_body:
        payload["htmlContent"] = html_body

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={"api-key": settings.brevo_api_key},
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
