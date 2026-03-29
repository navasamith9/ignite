from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, date
from django.db.models import Sum
from django.http import HttpResponse
from io import BytesIO
import qrcode
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

from .models import BusRoute, BusBooking


@login_required
def bus_list_view(request):
    """Display all bus routes with available seats for selected date"""
    selected_date = request.GET.get('date')
    route_type = request.GET.get('type')
    
    # Get all routes
    routes = BusRoute.objects.all()
    
    # Filter by route type if specified
    if route_type:
        routes = routes.filter(route_type=route_type)
    
    # Calculate available seats for each route based on selected date
    for route in routes:
        if selected_date:
            route.available_seats = route.get_available_seats(selected_date)
        else:
            route.available_seats = route.total_seats
    
    # Get route types for filter dropdown
    route_types = BusRoute.ROUTE_TYPES
    
    return render(request, 'bus/bus_list.html', {
        'routes': routes,
        'selected_date': selected_date,
        'route_types': route_types,
        'current_type': route_type
    })


@login_required
def book_bus_view(request, route_id):
    """Book tickets for a specific route"""
    route = get_object_or_404(BusRoute, id=route_id)
    
    # Get selected date from GET or POST
    selected_date = request.GET.get('date') or request.POST.get('travel_date')
    
    # Validate date is selected
    if not selected_date:
        messages.error(request, "Please select a travel date first.")
        return redirect('bus:bus_list')
    
    # Check if date is valid
    try:
        travel_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
        if travel_date_obj < date.today():
            messages.error(request, "Cannot book tickets for past dates.")
            return redirect('bus:bus_list')
    except ValueError:
        messages.error(request, "Invalid date format.")
        return redirect('bus:bus_list')
    
    # Get available seats
    available_seats = route.get_available_seats(selected_date)
    
    if request.method == 'POST':
        # Get number of tickets from form
        try:
            tickets = int(request.POST.get('num_tickets', 0))
        except ValueError:
            messages.error(request, "Invalid number of tickets.")
            return redirect(request.path + f'?date={selected_date}')
        
        # Validate ticket count
        if tickets < 1:
            messages.error(request, "Please select at least 1 ticket.")
            return redirect(request.path + f'?date={selected_date}')
        
        if tickets > 2:
            messages.error(request, "Maximum 2 tickets per booking.")
            return redirect(request.path + f'?date={selected_date}')
        
        if tickets > available_seats:
            messages.error(request, f"Only {available_seats} seats available.")
            return redirect(request.path + f'?date={selected_date}')
        
        # Create booking
        booking = BusBooking.objects.create(
            user=request.user,
            route=route,
            travel_date=selected_date,
            num_tickets=tickets,
            total_amount=route.fare * tickets,
            payment_status=False,  # Not paid yet
            status='pending'  # Pending payment
        )
        
        messages.success(request, "Booking created! Please complete payment.")
        return redirect('bus:payment', booking.id)
    
    # GET request - show booking form
    return render(request, 'bus/book_ticket.html', {
        'route': route,
        'available_seats': available_seats,
        'selected_date': selected_date,
        'max_tickets': min(2, available_seats)  # Max 2 or available seats
    })


@login_required
def payment_view(request, booking_id):
    """Handle payment for a booking"""
    booking = get_object_or_404(BusBooking, id=booking_id, user=request.user)
    
    # Check if booking is already paid
    if booking.payment_status:
        messages.info(request, "Payment already completed. Download your ticket.")
        return redirect('bus:download_ticket', booking.id)
    
    # Check if booking can be paid (not cancelled)
    if booking.status == 'cancelled':
        messages.error(request, "This booking has been cancelled.")
        return redirect('bus:my_bookings')
    
    if request.method == 'POST':
        payment_method = request.POST.get('method')
        
        # Simulate payment processing
        # In real application, integrate with payment gateway here
        payment_success = True
        
        if payment_success:
            # Update booking status
            booking.payment_status = True
            booking.status = 'confirmed'
            booking.payment_date = timezone.now()
            booking.save()
            
            messages.success(request, "Payment successful! Your ticket is ready.")
            return redirect('bus:download_ticket', booking.id)
        else:
            messages.error(request, "Payment failed. Please try again.")
            return redirect('bus:payment', booking.id)
    
    return render(request, 'bus/payment.html', {'booking': booking})


@login_required
def download_ticket_view(request, booking_id):
    """Generate and download PDF ticket with QR code"""
    booking = get_object_or_404(BusBooking, id=booking_id, user=request.user)
    
    # Check if payment is completed
    if not booking.payment_status:
        messages.error(request, "Payment not completed. Cannot download ticket.")
        return redirect('bus:payment', booking.id)
    
    # Create QR code data
    qr_data = f"""
Booking ID: {booking.id}
Passenger: {booking.user.get_full_name() or booking.user.username}
Route: {booking.route.name}
Travel Date: {booking.travel_date}
Departure: {booking.route.departure_time|time:"H:i"}
Arrival: {booking.route.arrival_time|time:"H:i"}
Tickets: {booking.num_tickets}
Total Amount: ₹{booking.total_amount}
Status: {booking.status}
    """
    
    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    elements.append(Paragraph("BUS TICKET", styles['Title']))
    elements.append(Spacer(1, 20))
    
    # Booking details
    elements.append(Paragraph(f"<b>Booking ID:</b> {booking.id}", styles['Normal']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"<b>Passenger Name:</b> {booking.user.get_full_name() or booking.user.username}", styles['Normal']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"<b>Route:</b> {booking.route.name}", styles['Normal']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"<b>Travel Date:</b> {booking.travel_date}", styles['Normal']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"<b>Departure Time:</b> {booking.route.departure_time|time:'H:i'}", styles['Normal']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"<b>Arrival Time:</b> {booking.route.arrival_time|time:'H:i'}", styles['Normal']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"<b>Number of Tickets:</b> {booking.num_tickets}", styles['Normal']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"<b>Total Amount:</b> ₹{booking.total_amount}", styles['Normal']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"<b>Status:</b> {booking.status.upper()}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Add QR code
    elements.append(Paragraph("SCAN FOR VERIFICATION", styles['Normal']))
    elements.append(Spacer(1, 10))
    qr_image = Image(qr_buffer, width=150, height=150)
    elements.append(qr_image)
    elements.append(Spacer(1, 20))
    
    # Footer
    elements.append(Paragraph("Please present this ticket at the time of boarding.", styles['Normal']))
    elements.append(Paragraph("Valid only for the specified date and route.", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Return PDF as response
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking.id}.pdf"'
    return response


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
    
    if booking.payment_status and booking.travel_date > date.today():
        if request.method == 'POST':
            # Update booking status
            booking.status = 'cancelled'
            booking.save()
            
            messages.success(request, 'Booking cancelled successfully.')
            return redirect('bus:my_bookings')
    else:
        messages.error(request, 'This booking cannot be cancelled.')
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
def generate_qr_view(request, booking_id):
    """Generate QR code image for booking"""
    booking = get_object_or_404(BusBooking, id=booking_id, user=request.user)
    
    if not booking.payment_status:
        messages.error(request, "Payment not completed. Cannot generate QR.")
        return redirect('bus:payment', booking.id)
    
    qr_data = f"Booking ID: {booking.id}, User: {booking.user.username}, Route: {booking.route.name}"
    
    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)
    
    return HttpResponse(buffer.getvalue(), content_type="image/png")


@login_required
def my_bookings_view(request):
    """Display all bookings for the logged-in user"""
    bookings = BusBooking.objects.filter(user=request.user).order_by('-booking_date')
    
    return render(request, 'bus/my_bookings.html', {
        'bookings': bookings
    })