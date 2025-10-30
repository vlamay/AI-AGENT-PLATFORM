"""
AI-Powered Email Processing Service

Automatically reads, classifies, and responds to emails using AI agents
"""

import asyncio
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import logging
import httpx
from html2text import html2text

import aioimaplib
import aiosmtplib
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailAccount:
    """Email account configuration"""
    def __init__(
        self,
        email_address: str,
        imap_host: str,
        imap_port: int,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        agent_id: str
    ):
        self.email_address = email_address
        self.imap_host = imap_host
        self.imap_port = imap_port
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.agent_id = agent_id


class EmailProcessor:
    """
    Main email processing engine
    
    Features:
    - IMAP connection for reading emails
    - AI classification (urgent, spam, inquiry, complaint, etc.)
    - Automated response generation
    - Thread management
    - Attachment handling
    """
    
    def __init__(self, orchestrator_url: str = "http://orchestrator:8080"):
        self.orchestrator_url = orchestrator_url
        self.imap_client = None
    
    async def connect_imap(self, account: EmailAccount):
        """Connect to IMAP server"""
        try:
            self.imap_client = aioimaplib.IMAP4_SSL(
                host=account.imap_host,
                port=account.imap_port
            )
            
            await self.imap_client.wait_hello_from_server()
            await self.imap_client.login(account.username, account.password)
            await self.imap_client.select('INBOX')
            
            logger.info(f"Connected to IMAP for {account.email_address}")
            return True
            
        except Exception as e:
            logger.error(f"IMAP connection failed: {str(e)}")
            return False
    
    async def fetch_unread_emails(self) -> List[Dict]:
        """Fetch unread emails from inbox"""
        try:
            # Search for unread emails
            response = await self.imap_client.search('UNSEEN')
            
            if response[0] != 'OK':
                return []
            
            message_ids = response[1][0].split()
            
            if not message_ids:
                logger.info("No unread emails")
                return []
            
            emails = []
            for msg_id in message_ids:
                email_data = await self._fetch_email_by_id(msg_id)
                if email_data:
                    emails.append(email_data)
            
            logger.info(f"Fetched {len(emails)} unread emails")
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            return []
    
    async def _fetch_email_by_id(self, msg_id: bytes) -> Optional[Dict]:
        """Fetch and parse a single email"""
        try:
            response = await self.imap_client.fetch(msg_id, '(RFC822)')
            
            if response[0] != 'OK':
                return None
            
            # Parse email
            raw_email = response[1][0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Extract email data
            email_data = {
                "message_id": msg.get('Message-ID'),
                "thread_id": msg.get('In-Reply-To') or msg.get('References'),
                "from_address": email.utils.parseaddr(msg.get('From'))[1],
                "to_addresses": [addr[1] for addr in email.utils.getaddresses([msg.get('To')])],
                "cc_addresses": [addr[1] for addr in email.utils.getaddresses([msg.get('Cc', '')])],
                "subject": msg.get('Subject', ''),
                "date": email.utils.parsedate_to_datetime(msg.get('Date')),
                "body_text": "",
                "body_html": "",
                "attachments": []
            }
            
            # Extract body
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    
                    if content_type == "text/plain":
                        email_data["body_text"] = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif content_type == "text/html":
                        html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        email_data["body_html"] = html_content
                        # Convert HTML to text if no plain text
                        if not email_data["body_text"]:
                            email_data["body_text"] = html2text(html_content)
                    elif part.get_filename():
                        # Handle attachments
                        email_data["attachments"].append({
                            "filename": part.get_filename(),
                            "content_type": content_type,
                            "size": len(part.get_payload(decode=True))
                        })
            else:
                email_data["body_text"] = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            return email_data
            
        except Exception as e:
            logger.error(f"Error parsing email {msg_id}: {str(e)}")
            return None
    
    async def classify_email(self, email_data: Dict) -> Dict:
        """
        Classify email using AI
        
        Categories:
        - urgent_inquiry
        - general_inquiry
        - complaint
        - feedback
        - spam
        - newsletter
        - order_related
        """
        
        classification_prompt = f"""Analyze this email and classify it:

From: {email_data['from_address']}
Subject: {email_data['subject']}
Body: {email_data['body_text'][:500]}

Classify into ONE category:
- urgent_inquiry (needs immediate response)
- general_inquiry (standard question)
- complaint (customer dissatisfaction)
- feedback (suggestions/praise)
- spam (promotional/irrelevant)
- order_related (purchase/shipping inquiry)

Also determine:
- Sentiment (positive/neutral/negative)
- Requires human (true/false)
- Priority (high/medium/low)

Respond ONLY with JSON:
{{
  "category": "category_name",
  "sentiment": "positive|neutral|negative",
  "requires_human": true/false,
  "priority": "high|medium|low",
  "confidence": 0.0-1.0
}}"""
        
        # Call orchestrator for classification
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.orchestrator_url}/api/v1/internal/classify",
                    json={"prompt": classification_prompt},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return self._default_classification()
                    
            except Exception as e:
                logger.error(f"Classification error: {str(e)}")
                return self._default_classification()
    
    def _default_classification(self) -> Dict:
        """Default classification if AI fails"""
        return {
            "category": "general_inquiry",
            "sentiment": "neutral",
            "requires_human": False,
            "priority": "medium",
            "confidence": 0.5
        }
    
    async def generate_response(
        self,
        email_data: Dict,
        classification: Dict,
        agent_id: str
    ) -> Optional[str]:
        """
        Generate AI response to email
        """
        
        # Don't respond to spam or newsletters
        if classification['category'] in ['spam', 'newsletter']:
            logger.info(f"Skipping response for {classification['category']}")
            return None
        
        # Build context for AI
        response_prompt = f"""You are a professional customer service AI assistant.

Generate a helpful email response to this customer:

Original Email:
From: {email_data['from_address']}
Subject: {email_data['subject']}
Body:
{email_data['body_text']}

Context:
- Category: {classification['category']}
- Sentiment: {classification['sentiment']}
- Priority: {classification['priority']}

Requirements:
- Be professional and empathetic
- Address their specific concern
- Provide actionable next steps
- Sign off appropriately
- Keep it concise (max 200 words)

Generate ONLY the email body (no subject line):"""
        
        # Call orchestrator for response generation
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.orchestrator_url}/api/v1/agents/{agent_id}/generate",
                    json={
                        "message": response_prompt,
                        "context": {
                            "email_data": email_data,
                            "classification": classification
                        }
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('text', '')
                else:
                    logger.error(f"Response generation failed: {response.status_code}")
                    return None
                    
            except Exception as e:
                logger.error(f"Response generation error: {str(e)}")
                return None
    
    async def send_email(
        self,
        account: EmailAccount,
        to_address: str,
        subject: str,
        body: str,
        in_reply_to: Optional[str] = None
    ):
        """Send email via SMTP"""
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = account.email_address
            msg['To'] = to_address
            msg['Subject'] = f"Re: {subject}" if in_reply_to else subject
            
            if in_reply_to:
                msg['In-Reply-To'] = in_reply_to
                msg['References'] = in_reply_to
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send via SMTP
            async with aiosmtplib.SMTP(
                hostname=account.smtp_host,
                port=account.smtp_port,
                use_tls=True
            ) as smtp:
                await smtp.login(account.username, account.password)
                await smtp.send_message(msg)
            
            logger.info(f"Email sent to {to_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    async def process_inbox(self, account: EmailAccount):
        """
        Main processing loop
        
        1. Connect to IMAP
        2. Fetch unread emails
        3. Classify each email
        4. Generate responses
        5. Send responses
        """
        
        if not await self.connect_imap(account):
            return
        
        try:
            emails = await self.fetch_unread_emails()
            
            for email_data in emails:
                logger.info(f"Processing email from {email_data['from_address']}")
                
                # Classify
                classification = await self.classify_email(email_data)
                logger.info(f"Classification: {classification}")
                
                # Check if requires human
                if classification['requires_human'] or classification['priority'] == 'high':
                    logger.info("Email flagged for human review")
                    # TODO: Send to human agent queue
                    continue
                
                # Generate response
                response_text = await self.generate_response(
                    email_data,
                    classification,
                    account.agent_id
                )
                
                if response_text:
                    # Send response
                    await self.send_email(
                        account,
                        email_data['from_address'],
                        email_data['subject'],
                        response_text,
                        email_data['message_id']
                    )
                    
                    logger.info(f"Automated response sent to {email_data['from_address']}")
                
        except Exception as e:
            logger.error(f"Error processing inbox: {str(e)}")
        
        finally:
            if self.imap_client:
                await self.imap_client.logout()


async def main():
    """Main entry point for email processor service"""
    
    # In production, fetch accounts from database
    # For demo, using environment variables
    import os
    
    account = EmailAccount(
        email_address=os.getenv("EMAIL_ADDRESS"),
        imap_host=os.getenv("IMAP_HOST", "imap.gmail.com"),
        imap_port=int(os.getenv("IMAP_PORT", "993")),
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        username=os.getenv("EMAIL_USERNAME"),
        password=os.getenv("EMAIL_PASSWORD"),
        agent_id=os.getenv("AGENT_ID")
    )
    
    processor = EmailProcessor()
    
    # Process inbox every 60 seconds
    while True:
        try:
            logger.info("Checking for new emails...")
            await processor.process_inbox(account)
            await asyncio.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Shutting down email processor...")
            break
        except Exception as e:
            logger.error(f"Main loop error: {str(e)}")
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
