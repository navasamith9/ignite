from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.db.models import Sum

User = get_user_model()

class BusRoute(models.Model):
    ROUTE_TYPES = (
        ('college_to_city', 'College to City'),
        ('city_to_college', 'City to College'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    route_type = models.CharField(max_length=20, choices=ROUTE_TYPES)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    total_seats = models.IntegerField(default=30, validators=[MinValueValidator(1)])
    available_seats = models.IntegerField(default=30, validators=[MinValueValidator(0)])
    fare = models.DecimalField(max_digits=6, decimal_places=2, default=50.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_available_seats(self, travel_date):
        booked = self.bookings.filter(
            travel_date=travel_date,
            payment_status=True,
            status='confirmed'
        ).aggregate(total=Sum('num_tickets'))['total'] or 0

        return self.total_seats - booked
    
    def __str__(self):
        return f"{self.name} - {self.departure_time} ({self.get_route_type_display()})"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # New instance
            self.available_seats = self.total_seats
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['route_type', 'departure_time']


class BusBooking(models.Model):
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('used', 'Used'),
        ('expired', 'Expired'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bus_bookings')
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    travel_date = models.DateField()
    num_tickets = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)])
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    qr_code = models.TextField(blank=True, null=True)  # Changed to TextField for base64 data
    payment_status = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.route.name} - {self.travel_date}"
    
    class Meta:
        unique_together = ['user', 'travel_date', 'route']
        ordering = ['-booking_date']