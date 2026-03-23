from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import date, datetime
from .models import Room, Booking, Participant
from .forms import BookingForm, BookingEditForm
from .utils import recommend_rooms, send_booking_email, check_and_reassign_room
import json

@login_required
def room_list_view(request):
    rooms = Room.objects.filter(is_active=True)
    
    # Filters
    room_type = request.GET.get('type')
    if room_type:
        rooms = rooms.filter(room_type=room_type)
    
    min_capacity = request.GET.get('min_capacity')
    if min_capacity:
        try:
            rooms = rooms.filter(capacity__gte=int(min_capacity))
        except:
            pass
    
    has_projector = request.GET.get('projector')
    if has_projector:
        rooms = rooms.filter(has_projector=True)
    
    has_ac = request.GET.get('ac')
    if has_ac:
        rooms = rooms.filter(has_ac=True)
    
    context = {
        'rooms': rooms,
        'room_types': Room.ROOM_TYPES,
        'filters': request.GET,
    }
    return render(request, 'lhtc/room_list.html', context)

@login_required
def booking_list_view(request):
    if request.user.user_type in ['teacher', 'club_coordinator', 'admin']:
        bookings = Booking.objects.filter(booked_by=request.user)
    else:
        # Students see bookings they're participating in
        bookings = Booking.objects.filter(participants__user=request.user, participants__is_registered=True)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    context = {
        'bookings': bookings.order_by('-date', '-start_time'),
        'is_teacher': request.user.user_type in ['teacher', 'club_coordinator', 'admin'],
        'status_choices': Booking.STATUS_CHOICES,
        'today': date.today(),
        'now': timezone.now(),
    }
    return render(request, 'lhtc/booking_list.html', context)

@login_required
def create_booking_view(request):
    if request.user.user_type not in ['teacher', 'club_coordinator', 'admin']:
        messages.error(request, 'You don\'t have permission to create bookings.')
        return redirect('lhtc:booking_list')
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.booked_by = request.user
            booking.status = 'confirmed'
            
            # Check for conflicts
            if check_room_availability(booking.room, booking.date, booking.start_time, booking.end_time):
                booking.save()
                
                # Send confirmation email to participants
                send_booking_email(
                    booking,
                    "New Event Created",
                    f"You have been invited to {booking.title}. Please register before {booking.registration_deadline}"
                )
                
                messages.success(request, 'Booking created successfully!')
                return redirect('lhtc:booking_list')
            else:
                messages.error(request, 'Room is not available at the selected time. Please choose another time.')
    else:
        form = BookingForm()
        # Pre-fill with data from AI recommendation if provided
        room_id = request.GET.get('room')
        if room_id:
            try:
                form.initial['room'] = room_id
            except:
                pass
        
        strength = request.GET.get('strength')
        if strength:
            try:
                form.initial['estimated_strength'] = int(strength)
            except:
                pass
        
        purpose = request.GET.get('purpose')
        if purpose:
            form.initial['purpose'] = purpose
    
    context = {
        'form': form,
        'rooms': Room.objects.filter(is_active=True),
    }
    return render(request, 'lhtc/create_booking.html', context)

@login_required
def edit_booking_view(request, booking_id):
    if request.user.user_type not in ['teacher', 'club_coordinator', 'admin']:
        messages.error(request, 'You don\'t have permission to edit bookings.')
        return redirect('lhtc:booking_list')
    
    booking = get_object_or_404(Booking, id=booking_id, booked_by=request.user)
    
    if booking.date < date.today():
        messages.error(request, 'Cannot edit past events.')
        return redirect('lhtc:booking_list')
    
    if request.method == 'POST':
        form = BookingEditForm(request.POST, instance=booking)
        if form.is_valid():
            updated_booking = form.save(commit=False)
            
            # Check if room/time changed
            if (updated_booking.room != booking.room or 
                updated_booking.date != booking.date or 
                updated_booking.start_time != booking.start_time or 
                updated_booking.end_time != booking.end_time):
                
                if check_room_availability(updated_booking.room, updated_booking.date, 
                                          updated_booking.start_time, updated_booking.end_time, 
                                          str(booking_id)):
                    updated_booking.save()
                    
                    # Notify participants about changes
                    send_booking_email(
                        updated_booking,
                        "Event Updated",
                        f"The details for {updated_booking.title} have been updated. Please check the new information."
                    )
                    
                    messages.success(request, 'Booking updated successfully!')
                else:
                    messages.error(request, 'New time slot is not available.')
                    return render(request, 'lhtc/edit_booking.html', {'form': form, 'booking': booking})
            else:
                updated_booking.save()
                messages.success(request, 'Booking updated successfully!')
            
            return redirect('lhtc:booking_list')
    else:
        form = BookingEditForm(instance=booking)
    
    context = {
        'form': form,
        'booking': booking,
        'rooms': Room.objects.filter(is_active=True),
    }
    return render(request, 'lhtc/edit_booking.html', context)

@login_required
def cancel_booking_view(request, booking_id):
    if request.user.user_type not in ['teacher', 'club_coordinator', 'admin']:
        messages.error(request, 'You don\'t have permission to cancel bookings.')
        return redirect('lhtc:booking_list')
    
    booking = get_object_or_404(Booking, id=booking_id, booked_by=request.user)
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        
        # Notify participants
        send_booking_email(
            booking,
            "Event Cancelled",
            f"We regret to inform you that {booking.title} has been cancelled."
        )
        
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('lhtc:booking_list')
    
    context = {'booking': booking}
    return render(request, 'lhtc/cancel_booking.html', context)

@login_required
def ai_recommendation_view(request):
    if request.user.user_type not in ['teacher', 'club_coordinator', 'admin']:
        messages.error(request, 'You don\'t have permission to access this feature.')
        return redirect('lhtc:booking_list')
    
    recommended_rooms = []
    search_params = {
        'strength': '',
        'purpose': '',
        'year': '',
        'branches': '',
        'date': '',
        'start': '',
        'end': '',
    }
    
    if request.method == 'POST':
        # Get form data with defaults
        estimated_strength = request.POST.get('estimated_strength', '').strip()
        purpose = request.POST.get('purpose', '').strip()
        year_batch = request.POST.get('year_batch', '').strip()
        branches = request.POST.get('branches', '').strip()
        date_val = request.POST.get('date', '').strip()
        start_time = request.POST.get('start_time', '').strip()
        end_time = request.POST.get('end_time', '').strip()
        
        # Update search params
        search_params = {
            'strength': estimated_strength,
            'purpose': purpose,
            'year': year_batch,
            'branches': branches,
            'date': date_val,
            'start': start_time,
            'end': end_time,
        }
        
        # Validate required fields
        if not estimated_strength:
            messages.error(request, 'Please enter estimated strength.')
        elif not purpose:
            messages.error(request, 'Please select a purpose.')
        else:
            try:
                estimated_strength_int = int(estimated_strength)
                
                if estimated_strength_int <= 0:
                    messages.error(request, 'Please enter a valid strength (greater than 0).')
                else:
                    # Get AI recommendations
                    recommended_rooms = recommend_rooms(
                        estimated_strength_int, 
                        purpose, 
                        year_batch, 
                        branches, 
                        date_val, 
                        start_time, 
                        end_time
                    )
                    
                    if not recommended_rooms:
                        messages.warning(request, 'No suitable rooms found. Try adjusting your requirements.')
                    else:
                        messages.success(request, f'Found {len(recommended_rooms)} recommended rooms!')
                        
            except ValueError:
                messages.error(request, 'Please enter a valid number for strength.')
    
    # Prepare purpose choices and year choices
    purpose_choices = Booking.PURPOSE_CHOICES
    year_choices = Booking.YEAR_CHOICES
    
    context = {
        'recommended_rooms': recommended_rooms,
        'search_params': search_params,
        'purpose_choices': purpose_choices,
        'year_choices': year_choices,
    }
    return render(request, 'lhtc/ai_recommendation.html', context)

@login_required
def register_for_event(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, status='confirmed')
    
    if booking.registration_deadline < timezone.now():
        messages.error(request, 'Registration deadline has passed.')
        return redirect('lhtc:booking_list')
    
    participant, created = Participant.objects.get_or_create(
        booking=booking,
        user=request.user,
        defaults={'is_registered': True}
    )
    
    if created:
        booking.registered_strength += 1
        booking.save()
        
        # Check if room needs to be changed
        check_and_reassign_room(booking)
        
        messages.success(request, f'Successfully registered for {booking.title}')
    else:
        if participant.is_registered:
            messages.info(request, 'You are already registered for this event.')
        else:
            participant.is_registered = True
            participant.save()
            booking.registered_strength += 1
            booking.save()
            messages.success(request, f'Successfully registered for {booking.title}')
    
    return redirect('lhtc:booking_list')

def check_room_availability(room, date_val, start_time, end_time, exclude_booking_id=None):
    bookings = Booking.objects.filter(
        room=room,
        date=date_val,
        status__in=['pending', 'confirmed']
    )
    
    if exclude_booking_id:
        bookings = bookings.exclude(id=exclude_booking_id)
    
    for booking in bookings:
        if (start_time < booking.end_time and end_time > booking.start_time):
            return False
    
    return True