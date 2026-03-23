from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from .models import User, OTP
from .forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from .utils import create_otp, verify_otp

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.is_verified = False
            user.save()
            
            # Create and send OTP
            create_otp(user, 'verification')
            
            request.session['temp_user_id'] = str(user.id)
            messages.success(request, 'Registration successful! Please verify your email.')
            return redirect('accounts:verify_otp')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def verify_otp_view(request):
    user_id = request.session.get('temp_user_id')
    if not user_id:
        return redirect('accounts:register')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp')
        
        if verify_otp(user, otp_code, 'verification'):
            user.is_verified = True
            user.save()
            login(request, user)
            messages.success(request, 'Email verified successfully! Welcome to IGNITE.')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')
    
    # Resend OTP
    if request.GET.get('resend'):
        create_otp(user, 'verification')
        messages.success(request, 'New OTP sent to your email.')
    
    return render(request, 'accounts/verify_otp.html', {'email': user.college_email})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                user = User.objects.get(college_email=email)
                if user.check_password(password):
                    if user.is_verified:
                        login(request, user)
                        messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                        return redirect('accounts:dashboard')
                    else:
                        messages.error(request, 'Please verify your email first.')
                        return redirect('accounts:verify_otp')
                else:
                    messages.error(request, 'Invalid password.')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(college_email=email)
                create_otp(user, 'password_reset')
                request.session['reset_user_id'] = str(user.id)
                messages.success(request, 'OTP sent to your email for password reset.')
                return redirect('accounts:reset_password')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email.')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'accounts/forgot_password.html', {'form': form})

def reset_password_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('accounts:forgot_password')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp']
            new_password = form.cleaned_data['new_password']
            
            if verify_otp(user, otp_code, 'password_reset'):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset successfully! Please login.')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Invalid or expired OTP.')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'accounts/reset_password.html', {'form': form})

@login_required
def dashboard_view(request):
    context = {
        'user': request.user,
        'is_teacher': request.user.user_type in ['teacher', 'club_coordinator', 'admin'],
        'is_student': request.user.user_type == 'student',
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('accounts:login')