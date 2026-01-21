"""
Email service for sending verification codes
Supports Gmail SMTP and can be configured for other providers
"""
from flask_mail import Mail, Message
import logging
import os

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending verification codes"""
    
    def __init__(self, app=None):
        self.mail = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize email service with Flask app"""
        # Configure Flask-Mail
        app.config['MAIL_SERVER'] = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(os.getenv('SMTP_PORT', 587))
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False
        app.config['MAIL_USERNAME'] = os.getenv('SMTP_USER', '')
        app.config['MAIL_PASSWORD'] = os.getenv('SMTP_PASSWORD', '')
        # Use the actual Gmail account as sender (required for Gmail SMTP)
        app.config['MAIL_DEFAULT_SENDER'] = os.getenv('SMTP_USER', 'TKR Chatbot <noreply@tkrchatbot.com>')
        
        self.mail = Mail(app)
        logger.info("Email service initialized")
    
    def send_verification_code(self, email, code):
        """Send verification code to email"""
        try:
            if not self.mail:
                # If email not configured, just log the code (for development)
                logger.warning(f"Email service not configured. Verification code for {email}: {code}")
                return {'success': True, 'message': f'Verification code (dev mode): {code}'}
            
            # Create email message
            msg = Message(
                subject='TKR Chatbot - Email Verification Code',
                recipients=[email]
            )
            
            # HTML email body
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .code-box {{ background: white; border: 2px dashed #667eea; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px; }}
                    .code {{ font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 5px; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎓 TKR College Chatbot</h1>
                        <p>Admin Email Verification</p>
                    </div>
                    <div class="content">
                        <h2>Hello Admin!</h2>
                        <p>Thank you for registering as an admin for the TKR College Chatbot.</p>
                        <p>Your verification code is:</p>
                        <div class="code-box">
                            <div class="code">{code}</div>
                        </div>
                        <p><strong>This code will expire in 10 minutes.</strong></p>
                        <p>If you didn't request this code, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>TKR College of Engineering and Technology</p>
                        <p>This is an automated email. Please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text fallback
            msg.body = f"""
            TKR College Chatbot - Email Verification
            
            Hello Admin!
            
            Your verification code is: {code}
            
            This code will expire in 10 minutes.
            
            If you didn't request this code, please ignore this email.
            
            ---
            TKR College of Engineering and Technology
            """
            
            # Send email
            self.mail.send(msg)
            logger.info(f"Verification code sent to {email}")
            return {'success': True, 'message': 'Verification code sent successfully'}
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            # In development, still return the code
            logger.warning(f"Email failed. Verification code for {email}: {code}")
            return {'success': True, 'message': f'Email service error. Code (dev mode): {code}'}

# Global email service instance
email_service = EmailService()
