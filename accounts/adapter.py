import re
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class RestrictEmailAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.user.email
        allowed_domain = "iiitdmj.ac.in" 

        # 1. Domain Check
        if not email or not email.endswith(f"@{allowed_domain}"):
            raise ValidationError(f"Access denied. Please use your @{allowed_domain} account.")

        # 2. Logic to distinguish Student vs Teacher
        # Regex explanation: ^\d checks if the email starts with a digit
        is_student_format = re.match(r'^\d', email)

        if is_student_format:
            sociallogin.user.user_type = 'student'
            # Optional: Extract roll number (everything before @)
            sociallogin.user.username = email.split('@')[0]
        else:
            # If it starts with letters (e.g., shiviansh@), it's likely faculty
            sociallogin.user.user_type = 'teacher' 

        # 3. Link to existing account if it exists
        try:
            user = User.objects.get(email=email)
            # Update the user_type of the existing user if it's not set
            if not user.user_type:
                user.user_type = sociallogin.user.user_type
                user.save()
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        """
        This ensures the user_type is actually saved to the database 
        when a new user is created via Google.
        """
        user = super().save_user(request, sociallogin, form)
        user.user_type = sociallogin.user.user_type
        user.save()
        return user