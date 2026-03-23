import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ignite.settings')
django.setup()

from lhtc.models import Room
from bus.models import BusRoute
from datetime import time
from django.contrib.auth import get_user_model

User = get_user_model()

def create_rooms():
    """Create sample rooms"""
    rooms_data = [
        {
            'room_number': 'LH-101',
            'name': 'Lecture Hall 101',
            'capacity': 60,
            'room_type': 'lecture',
            'has_projector': True,
            'has_ac': False,
            'has_whiteboard': True,
            'has_wifi': True,
            'floor': 1,
            'building': 'Academic Block A'
        },
        {
            'room_number': 'LH-102',
            'name': 'Lecture Hall 102',
            'capacity': 60,
            'room_type': 'lecture',
            'has_projector': True,
            'has_ac': False,
            'has_whiteboard': True,
            'has_wifi': True,
            'floor': 1,
            'building': 'Academic Block A'
        },
        {
            'room_number': 'SH-201',
            'name': 'Seminar Hall',
            'capacity': 120,
            'room_type': 'seminar',
            'has_projector': True,
            'has_ac': True,
            'has_whiteboard': True,
            'has_wifi': True,
            'floor': 2,
            'building': 'Academic Block A'
        },
        {
            'room_number': 'AUD-301',
            'name': 'Main Auditorium',
            'capacity': 300,
            'room_type': 'auditorium',
            'has_projector': True,
            'has_ac': True,
            'has_whiteboard': False,
            'has_wifi': True,
            'floor': 3,
            'building': 'Main Building'
        },
        {
            'room_number': 'CR-401',
            'name': 'Conference Room',
            'capacity': 30,
            'room_type': 'conference',
            'has_projector': True,
            'has_ac': True,
            'has_whiteboard': True,
            'has_wifi': True,
            'floor': 4,
            'building': 'Main Building'
        },
        {
            'room_number': 'LAB-501',
            'name': 'Computer Lab',
            'capacity': 40,
            'room_type': 'lab',
            'has_projector': True,
            'has_ac': True,
            'has_whiteboard': True,
            'has_wifi': True,
            'floor': 5,
            'building': 'Academic Block B'
        }
    ]
    
    created_count = 0
    for room_data in rooms_data:
        room, created = Room.objects.get_or_create(
            room_number=room_data['room_number'],
            defaults=room_data
        )
        if created:
            created_count += 1
            print(f"✅ Created room: {room.name}")
        else:
            print(f"⚠️ Room already exists: {room.name}")
    
    print(f"\n📊 Rooms created: {created_count}/{len(rooms_data)}")

def create_bus_routes():
    """Create sample bus routes"""
    bus_routes = [
        {
            'name': 'College to City - Morning 3:00 PM',
            'route_type': 'college_to_city',
            'departure_time': time(15, 0),
            'arrival_time': time(15, 45),
            'total_seats': 30,
            'fare': 50.00
        },
        {
            'name': 'College to City - Evening 3:30 PM',
            'route_type': 'college_to_city',
            'departure_time': time(15, 30),
            'arrival_time': time(16, 15),
            'total_seats': 30,
            'fare': 50.00
        },
        {
            'name': 'College to City - Evening 6:00 PM',
            'route_type': 'college_to_city',
            'departure_time': time(18, 0),
            'arrival_time': time(18, 45),
            'total_seats': 30,
            'fare': 50.00
        },
        {
            'name': 'College to City - Night 8:30 PM',
            'route_type': 'college_to_city',
            'departure_time': time(20, 30),
            'arrival_time': time(21, 15),
            'total_seats': 30,
            'fare': 50.00
        },
        {
            'name': 'City to College - Early Morning 5:00 AM',
            'route_type': 'city_to_college',
            'departure_time': time(5, 0),
            'arrival_time': time(5, 45),
            'total_seats': 30,
            'fare': 50.00
        },
        {
            'name': 'City to College - Morning 7:30 AM',
            'route_type': 'city_to_college',
            'departure_time': time(7, 30),
            'arrival_time': time(8, 15),
            'total_seats': 30,
            'fare': 50.00
        },
        {
            'name': 'City to College - Late Morning 9:30 AM',
            'route_type': 'city_to_college',
            'departure_time': time(9, 30),
            'arrival_time': time(10, 15),
            'total_seats': 30,
            'fare': 50.00
        }
    ]
    
    created_count = 0
    for route_data in bus_routes:
        route, created = BusRoute.objects.get_or_create(
            name=route_data['name'],
            defaults=route_data
        )
        if created:
            created_count += 1
            print(f"✅ Created bus route: {route.name}")
        else:
            print(f"⚠️ Bus route already exists: {route.name}")
    
    print(f"\n📊 Bus routes created: {created_count}/{len(bus_routes)}")

def create_admin_user():
    """Create admin user if not exists"""
    admin_email = 'admin@college.edu'
    if not User.objects.filter(college_email=admin_email).exists():
        admin = User.objects.create_superuser(
            username='admin',
            college_email=admin_email,
            password='admin123',
            user_type='admin',
            is_verified=True,
            department='Administration',
            first_name='Admin',
            last_name='User'
        )
        print("✅ Created admin user (admin@college.edu / admin123)")
    else:
        print("⚠️ Admin user already exists")

def create_sample_teacher():
    """Create a sample teacher user"""
    teacher_email = 'teacher@college.edu'
    if not User.objects.filter(college_email=teacher_email).exists():
        teacher = User.objects.create_user(
            username='teacher',
            college_email=teacher_email,
            password='teacher123',
            user_type='teacher',
            is_verified=True,
            department='Computer Science',
            first_name='John',
            last_name='Teacher'
        )
        print("✅ Created teacher user (teacher@college.edu / teacher123)")
    else:
        print("⚠️ Teacher user already exists")

def create_sample_student():
    """Create a sample student user"""
    student_email = 'student@college.edu'
    if not User.objects.filter(college_email=student_email).exists():
        student = User.objects.create_user(
            username='student',
            college_email=student_email,
            password='student123',
            user_type='student',
            is_verified=True,
            department='Computer Science',
            year=2,
            first_name='Jane',
            last_name='Student'
        )
        print("✅ Created student user (student@college.edu / student123)")
    else:
        print("⚠️ Student user already exists")

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 IGNITE - Creating Initial Data")
    print("=" * 50)
    print()
    
    print("📚 Creating rooms...")
    create_rooms()
    print()
    
    print("🚌 Creating bus routes...")
    create_bus_routes()
    print()
    
    print("👤 Creating users...")
    create_admin_user()
    create_sample_teacher()
    create_sample_student()
    print()
    
    print("=" * 50)
    print("✅ Initial data creation completed!")
    print("=" * 50)
    print()
    print("🔑 Login Credentials:")
    print("   Admin:   admin@college.edu / admin123")
    print("   Teacher: teacher@college.edu / teacher123")
    print("   Student: student@college.edu / student123")