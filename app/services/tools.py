import json
import smtplib
import os
from email.message import EmailMessage
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.core import config
# import secure_smtplib # REMOVED to avoid confusion, using standard smtplib


# Load ENV variables for email
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_sms(mobile_number: str, message: str):
    print(f"--- SMS SENT to {mobile_number} ---\n{message}\n------------------------------")
    return "SMS sent successfully."

def send_email(to_email: str, subject: str, content: str, attachment_path: str = None):
    """
    Sends an actual email using credentials from .env
    """
    # Check if we should redirect to CEO
    user_config = config.load_config()
    if to_email.upper() == "CEO":
        to_email = user_config.get("ceo_email", "")
        if not to_email:
            return "Error: No CEO email configured."

    # If no credentials, fallback to mock
    if not EMAIL_USER or not EMAIL_PASSWORD:
        print(f"--- MOCK EMAIL SENT to {to_email} ---\nSubject: {subject}\nContent: {content}\n(Configure .env for real email)\n--------------------------------")
        return f"Email sent to {to_email} (Mocked: No credentials)."

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg.set_content(content)

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(attachment_path)
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

    try:
        # Determine strict SSL (465) vs STARTTLS (587/other)
        if EMAIL_PORT == 465:
            # Implicit SSL
            with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.send_message(msg)
        else:
            # STARTTLS (Default for 587)
            with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.send_message(msg)
                
        return f"Email sent successfully to {to_email}."
    except Exception as e:
        print(f"Failed to send email: {e}")
        return f"Failed to send email: {e}"

def generate_flyer_pdf(title: str, content: str, filename: str = "flyer.pdf"):
    # Ensure static/flyers exists
    output_dir = os.path.join("static", "flyers")
    os.makedirs(output_dir, exist_ok=True)
    
    # Sanitize filename
    filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).strip()
    if not filename.endswith(".pdf"):
        filename += ".pdf"
        
    filepath = os.path.join(output_dir, filename)
    
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 80, title)
    
    # Company Branding (from config)
    conf = config.load_config()
    company = conf.get("company_name", "Wanderlust")
    c.setFont("Helvetica-Oblique", 14)
    c.drawCentredString(width / 2, height - 110, f"Brought to you by {company}")
    
    c.line(50, height - 120, width - 50, height - 120)
    
    # Content
    c.setFont("Helvetica", 12)
    text = c.beginText(50, height - 150)
    text.setFont("Helvetica", 12)
    
    # Basic logical wrapping
    max_chars = 90
    lines = content.split('\n')
    for line in lines:
        while len(line) > max_chars:
            chunk = line[:max_chars]
            last_space = chunk.rfind(' ')
            if last_space > 0:
                text.textLine(line[:last_space])
                line = line[last_space+1:]
            else:
                text.textLine(chunk)
                line = line[max_chars:]
        text.textLine(line)
        
    c.drawText(text)
    
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, f"Contact us via our Chat Agent. © {company}")
    
    c.save()
    
    return f"/static/flyers/{filename}"

def create_and_email_flyer(to_email: str, title: str, content: str, filename: str = "flyer.pdf"):
    """
    Generates a PDF flyer and immediately emails it to the user.
    """
    try:
        # 1. Generate PDF
        # We need the local file path, not the web URL.
        # generate_flyer_pdf returns "/static/flyers/filename", we need relative system path "static/flyers/filename"
        # but let's just reuse the logic or call the function and strip leading /
        web_path = generate_flyer_pdf(title, content, filename)
        file_path = web_path.lstrip('/') # "static/flyers/..."
        if file_path.startswith('/'): file_path = file_path[1:] # Double check

        # 2. Email it
        subject = f"Your Requested Flyer: {title}"
        email_body = f"Hello,\n\nPlease find attached the flyer for '{title}' as requested.\n\nBest regards,\nAutomated Assistant"
        
        result_email = send_email(to_email, subject, email_body, attachment_path=file_path)
        
        return f"Flyer created at {web_path} and {result_email}"
        
    except Exception as e:
        return f"Failed to process flyer request: {e}"

def update_lead_info(name: str = None, email: str = None, mobile: str = None, topic: str = None):
    # This just returns success message for agent
    return f"User info updated: {name}, {email}, {mobile}"
