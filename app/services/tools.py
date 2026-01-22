import json
import smtplib
import os
from email.message import EmailMessage
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.units import inch
from bs4 import BeautifulSoup, NavigableString
from duckduckgo_search import DDGS
from app.core import config

def search_web(query: str):
    """
    Searches the web for the given query and returns a summary of results.
    """
    try:
        results = DDGS().text(query, max_results=5)
        if not results:
             return "No results found."
        
        summary = ""
        for res in results:
             summary += f"- {res['title']}: {res['body']} ({res['href']})\n"
        return summary
    except Exception as e:
        return f"Search failed: {e}"

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
        print(f"--- Attempting to send email via {EMAIL_HOST}:{EMAIL_PORT} ---")
        print(f"From: {EMAIL_USER}")
        print(f"To: {to_email}")
        
        # Determine strict SSL (465) vs STARTTLS (587/other)
        if EMAIL_PORT == 465:
            # Implicit SSL
            with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
                server.set_debuglevel(1)
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.send_message(msg)
        else:
            # STARTTLS (Default for 587)
            with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                server.set_debuglevel(1)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.send_message(msg)
                
        print("--- Email SMTP transaction complete ---")
        return f"Email sent successfully to {to_email}."
    except Exception as e:
        print(f"Failed to send email: {e}")
        return f"Failed to send email: {e}"

def sanitize_html_for_reportlab(html_content):
    """
    Sanitizes HTML content for ReportLab's Paragraph parser.
    ReportLab's img tag only supports: src, width, height, valign
    This removes unsupported attributes like alt, style, etc.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Find all img tags and remove unsupported attributes
    for img in soup.find_all('img'):
        # Keep only supported attributes
        supported_attrs = ['src', 'width', 'height', 'valign']
        attrs_to_remove = [attr for attr in img.attrs if attr not in supported_attrs]
        for attr in attrs_to_remove:
            del img[attr]
    
    return str(soup)

def parse_html_to_flowables(html_content, styles):
    """
    Parses a string of HTML content into a list of ReportLab Flowables.
    Handles basic tags: h1-h6, p, ul, li, strong, b, em, i.
    """
    # Sanitize HTML first to remove unsupported attributes
    html_content = sanitize_html_for_reportlab(html_content)
    
    soup = BeautifulSoup(html_content, "html.parser")
    flowables = []
    
    def process_element(element):
        if isinstance(element, NavigableString):
            text = str(element).strip()
            if text:
                flowables.append(Paragraph(text, styles["BodyText"]))
            return

        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # Map HTML headers to ReportLab styles
            style_name = 'Heading1' if element.name == 'h1' else \
                         'Heading2' if element.name == 'h2' else \
                         'Heading3' if element.name == 'h3' else \
                         'Heading4'
            # Get inner text/html for the paragraph
            # We use decode_contents to keep inner inline tags like <b> or <i> which Paragraph supports
            text = element.decode_contents() 
            flowables.append(Paragraph(text, styles[style_name]))
            flowables.append(Spacer(1, 6))
            
        elif element.name == 'p':
            text = element.decode_contents()
            flowables.append(Paragraph(text, styles["BodyText"]))
            flowables.append(Spacer(1, 8))
            
        elif element.name in ['ul', 'ol']:
            list_items = []
            for child in element.children:
                if child.name == 'li':
                    # Parse contents of li
                    # For simplicity, treat li content as a Paragraph
                    li_content = child.decode_contents()
                    list_items.append(
                        ListItem(
                            Paragraph(li_content, styles["BodyText"]),
                            leftIndent=20,
                            value='-' if element.name == 'ul' else '1'
                        )
                    )
            if list_items:
                flowables.append(ListFlowable(list_items, bulletType='bullet', start='circle'))
                flowables.append(Spacer(1, 8))
        
        elif element.name == 'div':
            # Recurse
            for child in element.children:
                process_args = process_element(child)
        
        else:
            # Generic fallback: try to extract text if it's a block, or ignore if it's structural junk
            # If it's a top level plain text or unknown tag, wrap in normal paragraph
             if element.name:
                 # It might be an inline tag at top level (unlikely if well formed, but possible)
                 # We wrap it
                 text = str(element)
                 flowables.append(Paragraph(text, styles["BodyText"]))
                 flowables.append(Spacer(1, 6))

    # If the content has no tags (just plain text), split by newlines
    if not soup.find():
        for line in html_content.split('\n'):
            if line.strip():
                flowables.append(Paragraph(line, styles["BodyText"]))
    else:
        # Iterate over top-level elements
        for child in soup.children:
            process_element(child)
            
    return flowables

def generate_flyer_pdf(title: str, content: str, filename: str = "flyer.pdf"):
    # Ensure static/flyers exists using absolute path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_dir = os.path.join(BASE_DIR, "static", "flyers")
    os.makedirs(output_dir, exist_ok=True)
    
    # Sanitize filename
    filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).strip()
    if not filename.endswith(".pdf"):
        filename += ".pdf"
        
    filepath = os.path.join(output_dir, filename)
    
    # Setup DocTemplate
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(name='FlyerTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=20, alignment=1)) # Center
    styles.add(ParagraphStyle(name='FlyerFooter', parent=styles['Italic'], fontSize=10, textColor='grey', spaceBefore=20))
    
    story = []
    
    # Add Company Branding
    conf = config.load_config()
    company = conf.get("company_name", "Company Name")
    
    # Title
    story.append(Paragraph(title, styles['FlyerTitle']))
    story.append(Paragraph(f"Brought to you by {company}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Content body - parse HTML or plain text
    # Note: Mistral might incorrectly escape characters like \n or produce Markdown mixed with HTML.
    # We trust BeautifulSoup to handle the HTML parts.
    
    # Pre-cleaning: simple replace of newlines if it's NOT HTML
    if not ("<" in content and ">" in content):
         content = content.replace("\n", "<br/>")

    story.extend(parse_html_to_flowables(content, styles))
    
    # Footer
    story.append(Spacer(1, 40))
    story.append(Paragraph(f"Contact us via our Chat Agent. © {company}", styles['FlyerFooter']))
    
    doc.build(story)
    
    return f"/static/flyers/{filename}"

def create_and_email_flyer(to_email: str, title: str, content: str, filename: str = "flyer.pdf"):
    """
    Generates a PDF flyer and immediately emails it to the user.
    """
    try:
        # 1. Generate PDF
        web_path = generate_flyer_pdf(title, content, filename)
        file_path = web_path.lstrip('/') 
        if file_path.startswith('/'): file_path = file_path[1:]

        # 2. Email it
        subject = f"Your Requested Flyer: {title}"
        email_body = f"Hello,\n\nPlease find attached the flyer for '{title}' as requested.\n\nBest regards,\nAutomated Assistant"
        
        result_email = send_email(to_email, subject, email_body, attachment_path=file_path)
        
        return {"url": web_path, "message": result_email}
        
    except Exception as e:
        return {"error": str(e)}

def update_lead_info(name: str = None, email: str = None, mobile: str = None, topic: str = None):
    return f"User info updated: {name}, {email}, {mobile}"
