from django.contrib import admin
from .models import LostItem, FoundItem, MatchNotification

@admin.register(LostItem)
class LostItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'location', 'date_lost', 'user', 'status', 'created_at']
    list_filter = ['category', 'status', 'date_lost']
    search_fields = ['title', 'description', 'location', 'user__username']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Item Information', {
            'fields': ('title', 'description', 'category', 'image')
        }),
        ('Location Details', {
            'fields': ('location', 'date_lost')
        }),
        ('Contact Information', {
            'fields': ('contact_phone', 'contact_email')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('User Information', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(FoundItem)
class FoundItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'location', 'date_found', 'user', 'status', 'created_at']
    list_filter = ['category', 'status', 'date_found']
    search_fields = ['title', 'description', 'location', 'user__username']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Item Information', {
            'fields': ('title', 'description', 'category', 'image')
        }),
        ('Location Details', {
            'fields': ('location', 'date_found')
        }),
        ('Contact Information', {
            'fields': ('contact_phone', 'contact_email')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('User Information', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(MatchNotification)
class MatchNotificationAdmin(admin.ModelAdmin):
    list_display = ['lost_item', 'found_item', 'match_score', 'is_sent', 'created_at']
    list_filter = ['is_sent', 'created_at']
    search_fields = ['lost_item__title', 'found_item__title']
    readonly_fields = ['created_at']