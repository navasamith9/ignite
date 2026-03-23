from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from .models import Room, Booking
from datetime import datetime, time
import math

def recommend_rooms(estimated_strength, purpose, year_batch, branches, date, start_time, end_time):
    """AI-based room recommendation system"""
    
    # Parse inputs with error handling
    try:
        if start_time and start_time != '':
            start = datetime.strptime(start_time, '%H:%M').time()
        else:
            start = None
            
        if end_time and end_time != '':
            end = datetime.strptime(end_time, '%H:%M').time()
        else:
            end = None
            
        if date and date != '':
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            target_date = None
    except:
        start = end = target_date = None
    
    # Get all active rooms with sufficient capacity
    rooms = Room.objects.filter(is_active=True, capacity__gte=estimated_strength)
    
    if not rooms:
        return []
    
    # Score each room
    scored_rooms = []
    
    for room in rooms:
        score = 0
        reasons = []
        
        # Capacity score (ideal: 60-80% occupancy)
        capacity_ratio = estimated_strength / room.capacity
        if 0.6 <= capacity_ratio <= 0.8:
            score += 50
            reasons.append("Optimal capacity utilization")
        elif 0.4 <= capacity_ratio < 0.6:
            score += 40
            reasons.append("Good capacity fit")
        elif capacity_ratio < 0.4:
            score += 30
            reasons.append("Room larger than needed")
        else:
            score += 10
            reasons.append("Room might be too small")
        
        # Amenities score based on purpose
        if purpose in ['exam', 'workshop', 'seminar', 'guest_lecture']:
            if room.has_projector:
                score += 25
                reasons.append("Has projector")
            if room.has_ac:
                score += 15
                reasons.append("Air conditioned")
        
        # Room type match based on purpose
        if purpose == 'club_event' and room.room_type == 'auditorium':
            score += 30
            reasons.append("Auditorium suitable for events")
        elif purpose == 'exam' and room.room_type == 'lecture':
            score += 25
            reasons.append("Standard lecture hall for exams")
        elif purpose == 'workshop' and room.room_type == 'seminar':
            score += 25
            reasons.append("Seminar hall ideal for workshops")
        elif purpose == 'class' and room.room_type == 'lecture':
            score += 20
            reasons.append("Lecture hall for classes")
        elif purpose == 'meeting' and room.room_type == 'conference':
            score += 20
            reasons.append("Conference room for meetings")
        
        # Check availability for the requested time
        if target_date and start and end:
            if is_room_available(room, target_date, start, end):
                score += 100
                reasons.append("Available at requested time")
            else:
                # Not available at requested time
                score = max(0, score - 50)
                reasons.append("Not available at requested time")
        else:
            # No time specified, assume flexible
            score += 50
            reasons.append("Time flexible")
        
        # Building location (prefer central buildings)
        central_buildings = ['main', 'academic', 'central', 'admin']
        if room.building.lower() in central_buildings:
            score += 10
            reasons.append("Central location")
        
        # Ensure score is a valid number between 0 and 100
        score = max(0, min(100, score))
        
        # Format capacity fit string
        capacity_fit = f"{estimated_strength}/{room.capacity} ({int(capacity_ratio*100)}%)"
        
        scored_rooms.append({
            'room': room,
            'score': score,
            'reasons': reasons[:5],  # Limit to top 5 reasons
            'capacity_fit': capacity_fit,
        })
    
    # Sort by score
    scored_rooms.sort(key=lambda x: x['score'], reverse=True)
    
    # Return top 5 recommendations
    return scored_rooms[:5]

def is_room_available(room, date, start_time, end_time):
    """Check if room is available at given time"""
    bookings = Booking.objects.filter(
        room=room,
        date=date,
        status__in=['pending', 'confirmed']
    )
    
    for booking in bookings:
        if (start_time < booking.end_time and end_time > booking.start_time):
            return False
    
    return True

def send_booking_email(booking, subject, message):
    """Send email to all participants"""
    participants = booking.participants.filter(is_registered=True)
    recipient_list = [p.user.college_email for p in participants]
    
    if recipient_list:
        html_message = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{subject}</h2>
                </div>
                <div class="content">
                    {message}
                    <br>
                    <p><strong>Event Details:</strong></p>
                    <ul>
                        <li>Title: {booking.title}</li>
                        <li>Date: {booking.date}</li>
                        <li>Time: {booking.start_time} - {booking.end_time}</li>
                        <li>Venue: {booking.room.name}</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>IGNITE - Institute Gateway</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=True,
            html_message=html_message
        )

def check_and_reassign_room(booking):
    """Check if room needs to be reassigned based on registered strength"""
    if booking.registered_strength > booking.room.capacity:
        # Find better room
        better_rooms = Room.objects.filter(
            is_active=True,
            capacity__gte=booking.registered_strength,
            capacity__lt=booking.room.capacity * 1.5
        ).exclude(id=booking.room.id)
        
        for room in better_rooms:
            if is_room_available(room, booking.date, booking.start_time, booking.end_time):
                # Notify about room change
                old_room = booking.room
                booking.room = room
                booking.save()
                
                # Send notification
                send_booking_email(
                    booking,
                    "Room Changed - Action Required",
                    f"The venue for {booking.title} has been changed from {old_room.name} to {room.name} due to increased participation."
                )
                return True
    
    return False