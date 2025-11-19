import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from langchain_tavily import TavilySearch

def get_tools():
    """
    Returns a list of tools that the agent can use.
    """
    # 1. Web Search Tool
    # This tool uses the Tavily Search API to find information online.
    tavily_search = TavilySearch(max_results=3)
    tavily_search.name = "web_search"
    tavily_search.description = "A search engine useful for finding information about companies, their mission, and recent news."

    # 2. Email Sending Tool
    # Note: This is a simplified email tool for this project.
    # In a real-world scenario, you would use a more robust service like SendGrid or AWS SES.
    def send_email(recipient_email: str, subject: str, body: str, resume_path: str) -> str:
        """
        Sends an email with the resume attached.
        recipient_email: The email address of the recipient.
        subject: The subject of the email.
        body: The body content of the email.
        resume_path: The file path of the resume to be attached.
        """
        try:
            sender_email = os.getenv("SENDER_EMAIL")
            app_password = os.getenv("GMAIL_APP_PASSWORD")

            if not all([sender_email, app_password]):
                return "Error: Gmail credentials are not set in the environment variables."

            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Attach the resume
            if os.path.exists(resume_path):
                with open(resume_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(resume_path)}")
                msg.attach(part)
            else:
                return "Error: Resume file not found for attachment."

            # Send the email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, app_password)
                server.send_message(msg)

            return f"Email successfully sent to {recipient_email}."

        except Exception as e:
            return f"Error sending email: {e}"

    # We need to wrap the python function into a LangChain tool
    from langchain.tools import tool
    email_tool = tool(send_email)
    email_tool.name = "send_email"
    email_tool.description = "Use this tool to send an email with a resume attached. Do not use it for anything else."

    return [tavily_search, email_tool]
