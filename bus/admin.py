from django.contrib import admin
from .models import BusRoute, BusBooking

@admin.register(BusRoute)
class BusRouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'route_type', 'departure_time', 'arrival_time', 
                    'total_seats', 'available_seats', 'fare', 'is_active']
    list_filter = ['route_type', 'is_active']
    search_fields = ['name']
    list_editable = ['available_seats', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Route Information', {
            'fields': ('name', 'route_type', 'departure_time', 'arrival_time')
        }),
        ('Seating Information', {
            'fields': ('total_seats', 'available_seats', 'fare')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(BusBooking)
class BusBookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'route', 'travel_date', 'num_tickets', 
                    'total_amount', 'status', 'booking_date']
    list_filter = ['status', 'travel_date', 'route']
    search_fields = ['user__username', 'user__email', 'route__name']
    readonly_fields = ['booking_date', 'qr_code']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'route', 'travel_date', 'num_tickets', 'total_amount')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('QR Code', {
            'fields': ('qr_code',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('booking_date',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_used', 'mark_as_cancelled']
    
    def mark_as_used(self, request, queryset):
        queryset.update(status='used')
        self.message_user(request, f'{queryset.count()} bookings marked as used.')
    mark_as_used.short_description = "Mark selected bookings as used"
    
    def mark_as_cancelled(self, request, queryset):
        for booking in queryset:
            if booking.status == 'confirmed':
                # Restore seats
                booking.route.available_seats += booking.num_tickets
                booking.route.save()
                booking.status = 'cancelled'
                booking.save()
        self.message_user(request, f'{queryset.count()} bookings cancelled.')
    mark_as_cancelled.short_description = "Cancel selected bookings"