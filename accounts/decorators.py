from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles=[]):
    """Decorator to check if user has required role"""
    def decorator(view_func):
        def wrapped(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.user_type in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, 'You do not have permission to access this page.')
                    return redirect('accounts:dashboard')
            return redirect('accounts:login')
        return wrapped
    return decorator

def teacher_required(view_func):
    """Decorator to check if user is teacher or admin"""
    return role_required(['teacher', 'club_coordinator', 'admin'])(view_func)

def student_required(view_func):
    """Decorator to check if user is student"""
    return role_required(['student'])(view_func)