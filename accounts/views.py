from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# We no longer need RegisterForm, LoginForm, OTP, etc. for the main flow.

@login_required
def dashboard_view(request):
    """
    After Google Login, the user is redirected here.
    """
    context = {
        'user': request.user,
        # Ensure your User model has 'user_type'
        'is_teacher': getattr(request.user, 'user_type', None) in ['teacher', 'club_coordinator', 'admin'],
        'is_student': getattr(request.user, 'user_type', None) == 'student',
    }
    return render(request, 'accounts/dashboard.html', context)

def logout_view(request):
    """
    Logs out the user and redirects to the home/login page.
    """
    logout(request)
    messages.success(request, 'Logged out successfully.')
    # Redirecting to the Google Login trigger or home
    return redirect('/')

# You can delete register_view, verify_otp_view, login_view, 
# forgot_password_view, and reset_password_view.