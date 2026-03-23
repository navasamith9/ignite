from django.contrib import admin
from .models import Room, Booking, Participant

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'name', 'capacity', 'room_type', 'building', 'floor', 'is_active']
    list_filter = ['room_type', 'building', 'has_ac', 'has_projector', 'is_active']
    search_fields = ['room_number', 'name', 'building']
    list_editable = ['is_active']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('room_number', 'name', 'room_type', 'capacity')
        }),
        ('Location', {
            'fields': ('building', 'floor')
        }),
        ('Amenities', {
            'fields': ('has_projector', 'has_ac', 'has_whiteboard', 'has_wifi')
        }),
        ('Status', {
            'fields': ('is_active', 'image')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['title', 'room', 'date', 'start_time', 'purpose', 'status', 'booked_by']
    list_filter = ['status', 'purpose', 'date', 'room']
    search_fields = ['title', 'description', 'booked_by__username']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at', 'registered_strength']
    
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'description', 'purpose', 'room')
        }),
        ('Schedule', {
            'fields': ('date', 'start_time', 'end_time')
        }),
        ('Participants', {
            'fields': ('estimated_strength', 'registered_strength', 'year_batch', 'branches')
        }),
        ('Registration', {
            'fields': ('registration_deadline',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['confirm_bookings', 'cancel_bookings']
    
    def confirm_bookings(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f'{queryset.count()} bookings confirmed.')
    confirm_bookings.short_description = "Confirm selected bookings"
    
    def cancel_bookings(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f'{queryset.count()} bookings cancelled.')
    cancel_bookings.short_description = "Cancel selected bookings"

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['booking', 'user', 'is_registered', 'registration_date', 'attended']
    list_filter = ['is_registered', 'attended', 'registration_date']
    search_fields = ['user__username', 'booking__title']
    readonly_fields = ['registration_date']