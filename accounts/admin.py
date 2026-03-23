from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, OTP

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'college_email', 'user_type', 'is_verified', 'is_active')
    list_filter = ('user_type', 'is_verified', 'is_active', 'department')
    search_fields = ('username', 'college_email', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'college_email', 'is_verified', 
                                       'phone', 'department', 'year', 'profile_picture')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'college_email', 'phone', 
                                       'department', 'year')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(OTP)