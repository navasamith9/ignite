from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()

class Room(models.Model):
    ROOM_TYPES = (
        ('lecture', 'Lecture Hall'),
        ('seminar', 'Seminar Hall'),
        ('auditorium', 'Auditorium'),
        ('lab', 'Laboratory'),
        ('conference', 'Conference Room'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    has_projector = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=False)
    has_whiteboard = models.BooleanField(default=True)
    has_wifi = models.BooleanField(default=False)
    floor = models.IntegerField()
    building = models.CharField(max_length=100)
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.room_number}) - Capacity: {self.capacity}"
    
    class Meta:
        ordering = ['building', 'floor', 'room_number']

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    
    PURPOSE_CHOICES = (
        ('class', 'Regular Class'),
        ('extra_class', 'Extra Class'),
        ('exam', 'Examination'),
        ('club_event', 'Club Event'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('meeting', 'Meeting'),
        ('guest_lecture', 'Guest Lecture'),
    )
    
    YEAR_CHOICES = [(i, f'Year {i}') for i in range(1, 5)]
    BRANCH_CHOICES = (
        ('cse', 'Computer Science'),
        ('ece', 'Electronics'),
        ('mech', 'Mechanical'),
        ('civil', 'Civil'),
        ('eee', 'Electrical'),
        ('it', 'Information Technology'),
        ('ai', 'Artificial Intelligence'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    estimated_strength = models.IntegerField(validators=[MinValueValidator(1)])
    registered_strength = models.IntegerField(default=0)
    
    year_batch = models.CharField(max_length=10, choices=YEAR_CHOICES, blank=True, null=True)
    branches = models.CharField(max_length=200, blank=True, help_text="Comma-separated branch codes")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    registration_deadline = models.DateTimeField()
    reminder_sent = models.BooleanField(default=False)
    room_changed_notification_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} - {self.date} - {self.start_time}"
    
    class Meta:
        ordering = ['-date', '-start_time']
        unique_together = ['room', 'date', 'start_time']

class Participant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_registered = models.BooleanField(default=False)
    registration_date = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['booking', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.booking.title}"