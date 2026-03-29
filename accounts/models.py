from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('club_coordinator', 'Club Coordinator'),
        ('admin', 'Admin'),
    ]
    
    # Define username (Google Auth will fill this with the part before the @)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, null=True, blank=True)
    
    # Use email as the primary identifier
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS must NOT include the USERNAME_FIELD
    REQUIRED_FIELDS = ['username'] 

    def __str__(self):
        return self.email