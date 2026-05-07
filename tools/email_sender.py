import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables (like EMAIL_SENDER and EMAIL_PASSWORD)
load_dotenv()

def send_email(recipient_email: str, subject: str, body_text: str) -> bool:
    """
    Drafts and securely sends an email to the specified recipient using SMTP.
    Requires EMAIL_SENDER and EMAIL_PASSWORD to be set in the .env file.
    
    Args:
        recipient_email (str): Who receives the email.
        subject (str): The email subject line.
        body_text (str): The plain text content of the email.
        
    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        print("Error: EMAIL_SENDER or EMAIL_PASSWORD missing in .env file.")
        return False
        
    # By default, we'll configure this for Gmail.
    # If you use Outlook or Yahoo, change the smtp_server to match.
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    
    # Construct the email container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    # Attach the body text
    msg.attach(MIMEText(body_text, 'plain'))
    
    try:
        print(f"Attempting to send email to {recipient_email}...")
        
        # Connect to SMTP server and encrypt the connection using TLS
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() 
        
        # Login and send
        server.login(sender_email, sender_password)
        server.send_message(msg)
        
        # Close connection cleanly
        server.quit()
        print("Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
        return False

if __name__ == "__main__":
    # Test block (will fail unless you add real credentials to your .env)
    print("Testing email setup...")
    print("Please make sure you have EMAIL_SENDER and EMAIL_PASSWORD in .env!")
    # send_email("test@example.com", "Test Subject", "This is a test body.")
