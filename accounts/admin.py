from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Remove OTP from imports since it was removed from models.py
# from .models import OTP 

class CustomUserAdmin(UserAdmin):
    # Updated to use 'email' instead of 'college_email' 
    # and removed 'is_verified' as Google handles verification
    list_display = ('email', 'username', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    
    # fieldsets controls the "Change User" page in Admin
    fieldsets = UserAdmin.fieldsets + (
        ('IGNITE Profile Info', {'fields': ('user_type',)}),
    )
    
    # add_fieldsets controls the "Add User" page in Admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('IGNITE Profile Info', {'fields': ('user_type', 'email')}),
    )

# Register only the User model
admin.site.register(User, CustomUserAdmin)

# DELETE or COMMENT OUT the OTP registration
# admin.site.register(OTP)