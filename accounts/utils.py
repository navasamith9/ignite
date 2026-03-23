import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import OTP

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(user, otp_code, purpose='verification'):
    """Send OTP via email"""
    subject = f'{purpose.upper()} OTP - IGNITE Platform'
    
    if purpose == 'verification':
        message = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .otp {{ font-size: 32px; font-weight: bold; color: #4CAF50; text-align: center; padding: 20px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to IGNITE!</h1>
                </div>
                <div class="content">
                    <p>Hello {user.get_full_name() or user.username},</p>
                    <p>Thank you for registering with IGNITE. Please verify your email address using the OTP below:</p>
                    <div class="otp">{otp_code}</div>
                    <p>This OTP is valid for 10 minutes.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2024 IGNITE - Institute Gateway. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        '''
    else:  # password reset
        message = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2196F3; color: white; padding: 20px; text-align: center; }}
                .otp {{ font-size: 32px; font-weight: bold; color: #2196F3; text-align: center; padding: 20px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hello {user.get_full_name() or user.username},</p>
                    <p>We received a request to reset your password. Use the OTP below to proceed:</p>
                    <div class="otp">{otp_code}</div>
                    <p>This OTP is valid for 10 minutes.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2024 IGNITE - Institute Gateway. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        '''
    
    send_mail(
        subject,
        '',
        settings.DEFAULT_FROM_EMAIL,
        [user.college_email],
        fail_silently=False,
        html_message=message
    )

def create_otp(user, purpose='verification'):
    """Create and send OTP"""
    # Delete existing unused OTPs
    OTP.objects.filter(user=user, purpose=purpose, is_used=False).delete()
    
    # Generate new OTP
    otp_code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=10)
    
    # Save OTP
    otp = OTP.objects.create(
        user=user,
        otp=otp_code,
        purpose=purpose,
        expires_at=expires_at
    )
    
    # Send email
    send_otp_email(user, otp_code, purpose)
    
    return otp

def verify_otp(user, otp_code, purpose='verification'):
    """Verify OTP"""
    try:
        otp = OTP.objects.get(
            user=user,
            otp=otp_code,
            purpose=purpose,
            is_used=False
        )
        
        if otp.is_valid():
            otp.is_used = True
            otp.save()
            return True
        else:
            return False
    except OTP.DoesNotExist:
        return False