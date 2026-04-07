import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio

EMAIL_ADDRESS = 'sugarly41@gmail.com'
EMAIL_PASSWORD = 'pjei zdjw dene jhqt'

def send_email_sync(user_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = user_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_ADDRESS, user_email, msg.as_string())
    except Exception as e:
        print(f'Email sending error ({subject}):', e)

async def send_verification_email(user_email: str, verify_url: str):
    subject = 'Sugarly - Verify your email'
    body = f"""
    <h2>Welcome to Sugarly!</h2>
    <p>Please verify your email by clicking the link below:</p>
    <a href='{verify_url}'>Verify Email</a>
    <p>If you did not register, ignore this message.</p>
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, send_email_sync, user_email, subject, body)

async def send_reset_password_email(user_email: str, reset_url: str):
    subject = 'Sugrly - Reset Your Password'
    body = f"""
    <h2>Password Reset Request</h2>
    <p>You recently requested to reset your password for your Sugrly account. Click the link below to proceed:</p>
    <a href='{reset_url}'>Reset Password</a>
    <p>If you did not request a password reset, please ignore this email.</p>
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, send_email_sync, user_email, subject, body)

async def send_email_change_confirmation(user_email: str, confirm_url: str):
    subject = 'Sugrly - Confirm Email Change'
    body = f"""
    <h2>Email Change Request</h2>
    <p>We received a request to change your account email to a new address. To authorize this change, please click the link below:</p>
    <a href='{confirm_url}'>Authorize Email Change</a>
    <p>If you did not request this change, please ignore this email or change your password immediately.</p>
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, send_email_sync, user_email, subject, body)

async def send_new_email_verification(user_email: str, verify_url: str):
    subject = 'Sugrly - Verify Your New Email'
    body = f"""
    <h2>Verify New Email Address</h2>
    <p>To complete your email change request, please verify your new email address by clicking the link below:</p>
    <a href='{verify_url}'>Verify New Email</a>
    <p>If you did not initiate this change, ignore this email.</p>
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, send_email_sync, user_email, subject, body)
