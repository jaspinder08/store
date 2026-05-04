import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from api.core.config import settings

def send_otp_email(email_to: str, otp: str):
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"Skipping email send for {email_to} (Credentials not set). OTP: {otp}")
        return

    message = MIMEMultipart()
    message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = email_to
    message["Subject"] = f"Your OTP for {settings.PROJECT_NAME}"

    html_content = f"""
    <html>
        <body>
            <h2>Hello!</h2>
            <p>Your OTP for verification is: <b>{otp}</b></p>
            <p>This OTP is valid for 5 minutes.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
    </html>
    """
    message.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        if settings.SMTP_TLS:
            server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(message)
        server.quit()
        print(f"Email sent successfully to {email_to}")
    except Exception as e:
        print(f"Failed to send email to {email_to}: {e}")
