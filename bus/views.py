from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, date
from .models import BusRoute, BusBooking
from .forms import BusBookingForm
import qrcode
import io
import base64
import uuid

@login_required
def bus_list_view(request):
    """Display all available bus routes"""
    routes = BusRoute.objects.filter(is_active=True)
    
    # Filter by route type
    route_type = request.GET.get('type')
    if route_type:
        routes = routes.filter(route_type=route_type)
    
    # Filter by date (optional)
    travel_date = request.GET.get('date')
    if travel_date:
        try:
            travel_date_obj = datetime.strptime(travel_date, '%Y-%m-%d').date()
            if travel_date_obj >= date.today():
                # Only show routes with available seats for the selected date
                routes = routes.filter(available_seats__gt=0)
        except:
            pass
    
    context = {
        'routes': routes,
        'route_types': BusRoute.ROUTE_TYPES,
        'today': date.today(),
    }
    return render(request, 'bus/bus_list.html', context)


@login_required
def book_ticket_view(request, route_id):
    """Book tickets for a specific bus route"""
    route = get_object_or_404(BusRoute, id=route_id, is_active=True)
    
    # Check if tickets are available
    if route.available_seats <= 0:
        messages.error(request, 'No tickets available for this route.')
        return redirect('bus:bus_list')
    
    if request.method == 'POST':
        form = BusBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.route = route
            booking.total_amount = route.fare * booking.num_tickets
            
            # Generate a unique booking ID for QR code
            booking_id = str(uuid.uuid4())[:8]
            qr_data = f"BUS:{booking_id}:{booking.user.username}:{booking.travel_date}:{booking.num_tickets}"
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert QR code to base64 for storage
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            qr_base64 = base64.b64encode(buffered.getvalue()).decode()
            booking.qr_code = qr_base64
            
            # Update available seats
            route.available_seats -= booking.num_tickets
            route.save()
            
            # Save booking
            booking.save()
            
            messages.success(request, f'Tickets booked successfully! Total: ₹{booking.total_amount}')
            return redirect('bus:my_bookings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BusBookingForm(initial={'route': route, 'num_tickets': 1})
    
    context = {
        'form': form,
        'route': route,
        'max_tickets': min(2, route.available_seats),
        'today': date.today(),
    }
    return render(request, 'bus/book_ticket.html', context)


@login_required
def my_bookings_view(request):
    """Display all bookings for the logged-in user"""
    bookings = BusBooking.objects.filter(user=request.user).order_by('-booking_date')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    # Mark expired bookings
    current_date = date.today()
    for booking in bookings:
        if booking.travel_date < current_date and booking.status == 'confirmed':
            booking.status = 'expired'
            booking.save()
    
    context = {
        'bookings': bookings,
        'status_choices': BusBooking.STATUS_CHOICES,
        'today': current_date,
    }
    return render(request, 'bus/my_bookings.html', context)


@login_required
def cancel_booking_view(request, booking_id):
    """Cancel an existing booking"""
    booking = get_object_or_404(BusBooking, id=booking_id, user=request.user)
    
    # Check if booking can be cancelled
    if booking.travel_date < date.today():
        messages.error(request, 'Cannot cancel past bookings.')
        return redirect('bus:my_bookings')
    
    if booking.status != 'confirmed':
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('bus:my_bookings')
    
    if request.method == 'POST':
        # Restore seats to the route
        booking.route.available_seats += booking.num_tickets
        booking.route.save()
        
        # Update booking status
        booking.status = 'cancelled'
        booking.save()
        
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('bus:my_bookings')
    
    context = {'booking': booking}
    return render(request, 'bus/cancel_booking.html', context)


@login_required
def booking_details_view(request, booking_id):
    """View details of a specific booking"""
    booking = get_object_or_404(BusBooking, id=booking_id, user=request.user)
    
    context = {
        'booking': booking,
    }
    return render(request, 'bus/booking_details.html', context)


@login_required
def download_ticket_view(request, booking_id):
    """Download ticket as PDF (optional feature)"""
    booking = get_object_or_404(BusBooking, id=booking_id, user=request.user)
    
    # This would generate a PDF ticket
    # For now, just show the ticket page
    messages.info(request, 'PDF download feature coming soon!')
    return redirect('bus:my_bookings')