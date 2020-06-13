import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from . import mail_handler_consts


def send_mail(text, subject):
    try:
        sender_email = mail_handler_consts.SENDER_EMAIL
        receiver_emails = mail_handler_consts.RECEIVER_EMAILS
        password = mail_handler_consts.PASS

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        for receiver_email in receiver_emails:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = sender_email
            message["To"] = receiver_email

            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text, "plain")

            # The email client will try to render the last part first
            message.attach(part1)
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )
        return True
    except Exception:
        return False
