from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class LostItem(models.Model):
    CATEGORY_CHOICES = (
        ('electronics', 'Electronics'),
        ('books', 'Books'),
        ('clothing', 'Clothing'),
        ('accessories', 'Accessories'),
        ('documents', 'Documents'),
        ('other', 'Other'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lost_items')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=200)
    date_lost = models.DateField()
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField()
    image = models.ImageField(upload_to='lost_items/', blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class FoundItem(models.Model):
    CATEGORY_CHOICES = (
        ('electronics', 'Electronics'),
        ('books', 'Books'),
        ('clothing', 'Clothing'),
        ('accessories', 'Accessories'),
        ('documents', 'Documents'),
        ('other', 'Other'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='found_items')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=200)
    date_found = models.DateField()
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField()
    image = models.ImageField(upload_to='found_items/', blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class MatchNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lost_item = models.ForeignKey(LostItem, on_delete=models.CASCADE)
    found_item = models.ForeignKey(FoundItem, on_delete=models.CASCADE)
    match_score = models.IntegerField(default=0)
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Match: {self.lost_item.title} - {self.found_item.title}"