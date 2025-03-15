import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class EmailSender:
    def __init__(self):
        self.sender_email = os.getenv("EMAIL_USER")
        
        self.password = os.getenv("EMAIL_PASS")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email(self, recipient_email, message_text, subject="No Subject"):
        print(self.sender_email)
        print(self.password)
        """Sends an email and returns a success or failure response."""

        if not self.sender_email or not self.password:
            return {"success": False, "message": "Missing sender email or password in .env file"}

        try:
            # Create email message
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = recipient_email
            msg["Subject"] = subject
            msg.attach(MIMEText(message_text, "plain"))

            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, recipient_email, msg.as_string())
            server.quit()

            return {"success": True, "message": "Email sent successfully"}
        
        except Exception as e:
            return {"success": False, "message": str(e)}

# Example usage
