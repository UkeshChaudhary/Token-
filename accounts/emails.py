from django.core.mail import EmailMessage
from django.conf import settings
import random
from .models import User

def send_otp_via_email(email):
    try:
        # Generate OTP
        otp = random.randint(100000, 999999)
        
        # Create email content
        subject = 'Your account verification email'
        message = f'This is a message from Rome Nepal, your OTP code is {otp}'
        
        # Create EmailMessage object
        email_from = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email]
        )
        
        # Send the email
        email_from.send()
        
        # Save OTP to the user
        user_obj = User.objects.get(email=email)
        user_obj.otp = otp
        user_obj.save()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
