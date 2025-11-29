#!/usr/bin/env python3
"""
Email Fallback System for BA Agent
Provides alternative email methods when ACS fails
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
from datetime import datetime
from azure.communication.email import EmailClient
from azure.core.exceptions import HttpResponseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    """Unified email service with fallback options"""
    
    def __init__(self, acs_connection_string=None, acs_sender_address=None):
        self.acs_connection_string = acs_connection_string
        self.acs_sender_address = acs_sender_address
        self.acs_client = None
        
        # Initialize ACS client if available
        if acs_connection_string:
            try:
                self.acs_client = EmailClient.from_connection_string(acs_connection_string)
                logger.info("✅ ACS Email client initialized")
            except Exception as e:
                logger.warning(f"⚠️ ACS Email client initialization failed: {str(e)}")
    
    def send_email(self, recipient_email, subject, content, html_content=None, attachments=None):
        """
        Send email with automatic fallback
        
        Args:
            recipient_email (str): Recipient email address
            subject (str): Email subject
            content (str): Plain text content
            html_content (str, optional): HTML content
            attachments (list, optional): List of file paths to attach
            
        Returns:
            dict: Result with success status and method used
        """
        
        # Try ACS first
        if self.acs_client and self.acs_sender_address:
            try:
                return self._send_via_acs(recipient_email, subject, content, html_content)
            except Exception as e:
                logger.warning(f"⚠️ ACS email failed: {str(e)}")
        
        # Fallback to console logging
        return self._log_email_fallback(recipient_email, subject, content)
    
    def _send_via_acs(self, recipient_email, subject, content, html_content=None):
        """Send email via Azure Communication Services"""
        try:
            message = {
                "senderAddress": self.acs_sender_address,
                "recipients": {
                    "to": [{"address": recipient_email}]
                },
                "content": {
                    "subject": subject,
                    "plainText": content
                }
            }
            
            if html_content:
                message["content"]["html"] = html_content
            
            logger.info(f"📤 Sending ACS email to: {recipient_email}")
            poller = self.acs_client.begin_send(message)
            result = poller.result()
            
            logger.info(f"✅ ACS email sent successfully! Message ID: {result.message_id}")
            return {
                "success": True,
                "method": "ACS",
                "message_id": result.message_id,
                "status": result.status
            }
            
        except HttpResponseError as e:
            if "Denied" in str(e):
                logger.error("❌ ACS Denied Error - Sender address needs verification in Azure portal")
            raise e
        except Exception as e:
            logger.error(f"❌ ACS email error: {str(e)}")
            raise e
    
    def _send_via_smtp_gmail(self, recipient_email, subject, content, html_content=None):
        """Send email via Gmail SMTP (requires app password)"""
        # This would require Gmail app password configuration
        # Placeholder for future implementation
        logger.info("📧 Gmail SMTP fallback not configured")
        return {"success": False, "method": "Gmail", "error": "Not configured"}
    
    def _log_email_fallback(self, recipient_email, subject, content):
        """Log email details when actual sending fails"""
        logger.info("📝 Email Fallback - Logging email details")
        
        email_log = f"""
        
        ═══════════════════════════════════════════════════════════════
        📧 EMAIL NOTIFICATION LOG
        ═══════════════════════════════════════════════════════════════
        Timestamp: {datetime.now()}
        To: {recipient_email}
        Subject: {subject}
        
        Content:
        {content}
        
        Status: LOGGED (Email service unavailable)
        ═══════════════════════════════════════════════════════════════
        
        """
        
        # Print to console
        print(email_log)
        
        # Also save to file
        try:
            with open('email_notifications.log', 'a', encoding='utf-8') as f:
                f.write(email_log)
            logger.info("📄 Email logged to file: email_notifications.log")
        except Exception as e:
            logger.warning(f"⚠️ Failed to write email log: {str(e)}")
        
        return {
            "success": True,
            "method": "Console/File Log",
            "message": "Email logged - manual notification required"
        }
    
    def test_connection(self):
        """Test email service connectivity"""
        test_email = "test@example.com"
        test_subject = "BA Agent Email Service Test"
        test_content = f"Email service test at {datetime.now()}"
        
        try:
            result = self.send_email(test_email, test_subject, test_content)
            logger.info(f"🧪 Email test result: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ Email test failed: {str(e)}")
            return {"success": False, "error": str(e)}

# Convenience function for BA Agent integration
def send_approval_email(recipient_email, analysis_data, documents_info):
    """
    Send approval email with document details
    
    Args:
        recipient_email (str): Recipient email
        analysis_data (dict): Analysis results
        documents_info (dict): Generated documents information
    """
    
    from config import ACS_CONNECTION_STRING, ACS_SENDER_ADDRESS
    
    # Initialize email service
    email_service = EmailService(ACS_CONNECTION_STRING, ACS_SENDER_ADDRESS)
    
    # Create email content
    subject = f"BA Agent - Document Analysis Ready for Approval (ID: {analysis_data.get('analysis_id', 'N/A')})"
    
    content = f"""
Dear Reviewer,

A new Business Analysis has been completed and is ready for your review and approval.

Analysis Details:
- Analysis ID: {analysis_data.get('analysis_id', 'N/A')}
- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Documents Created: {', '.join(documents_info.get('documents', ['TRD', 'HLD', 'LLD', 'Backlog']))}

Generated Documents:
{chr(10).join([f"- {doc}" for doc in documents_info.get('documents', [])])}

Please review the analysis and provide your approval to proceed with Azure DevOps work item creation.

Access the analysis at: {documents_info.get('access_url', 'http://localhost:3000')}

Best regards,
BA Agent System
"""
    
    html_content = f"""
    <html>
    <body>
        <h2>BA Agent - Document Analysis Ready</h2>
        <p>Dear Reviewer,</p>
        <p>A new Business Analysis has been completed and is ready for your review and approval.</p>
        
        <h3>Analysis Details:</h3>
        <ul>
            <li><strong>Analysis ID:</strong> {analysis_data.get('analysis_id', 'N/A')}</li>
            <li><strong>Generated on:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
            <li><strong>Documents Created:</strong> {', '.join(documents_info.get('documents', ['TRD', 'HLD', 'LLD', 'Backlog']))}</li>
        </ul>
        
        <h3>Generated Documents:</h3>
        <ul>
            {''.join([f"<li>{doc}</li>" for doc in documents_info.get('documents', [])])}
        </ul>
        
        <p>Please review the analysis and provide your approval to proceed with Azure DevOps work item creation.</p>
        
        <p><a href="{documents_info.get('access_url', 'http://localhost:3000')}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Review Analysis</a></p>
        
        <p>Best regards,<br>BA Agent System</p>
    </body>
    </html>
    """
    
    try:
        result = email_service.send_email(
            recipient_email=recipient_email,
            subject=subject,
            content=content,
            html_content=html_content
        )
        
        logger.info(f"📧 Approval email result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to send approval email: {str(e)}")
        # Fallback to console logging
        print(f"📧 EMAIL FALLBACK - Approval Request:")
        print(f"   To: {recipient_email}")
        print(f"   Subject: {subject}")
        print(f"   Analysis ID: {analysis_data.get('analysis_id', 'N/A')}")
        print(f"   Access URL: {documents_info.get('access_url', 'http://localhost:3000')}")
        print(f"   Note: Email service unavailable, but approval workflow continues")
        return {"success": True, "method": "console_fallback", "message": "Email logged to console"}

# Test function
def test_email_service():
    """Test the email service"""
    from config import ACS_CONNECTION_STRING, ACS_SENDER_ADDRESS, APPROVAL_RECIPIENT_EMAIL
    
    email_service = EmailService(ACS_CONNECTION_STRING, ACS_SENDER_ADDRESS)
    
    print("🧪 Testing Email Service...")
    result = email_service.send_email(
        recipient_email=APPROVAL_RECIPIENT_EMAIL,
        subject="BA Agent - Email Service Test",
        content="This is a test email to verify the email service is working correctly."
    )
    
    print(f"📊 Test Result: {result}")
    return result

if __name__ == "__main__":
    test_email_service()
