import logging
import resend
from api.core.config import settings

logger = logging.getLogger(__name__)

def send_otp_email(email: str, otp: str):
    if not settings.RESEND_API_KEY:
        logger.warning(f"Skipping email send for {email} (Resend API Key not set). OTP: {otp}")
        return

    resend.api_key = settings.RESEND_API_KEY

    html_content = f"""
    <html>
        <body>
            <h2>Hello!</h2>
            <p>Your OTP for verification at <b>{settings.PROJECT_NAME or 'Apna Store'}</b> is: <b>{otp}</b></p>
            <p>This OTP is valid for 5 minutes.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
    </html>
    """

    params = {
        "from": "onboarding@resend.dev",
        "to": [email],
        "subject": f"Your OTP for {settings.PROJECT_NAME or 'Apna Store'}",
        "html": html_content,
    }

    try:
        response = resend.Emails.send(params)
        logger.info(f"Email sent successfully to {email}. Resend ID: {response.get('id', 'N/A')}")
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {e}")

