from django import forms
from .models import BusBooking, BusRoute
from datetime import date

class BusBookingForm(forms.ModelForm):
    class Meta:
        model = BusBooking
        fields = ['route', 'travel_date', 'num_tickets']
        widgets = {
            'travel_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'min': date.today().isoformat()
            }),
            'num_tickets': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 1, 
                'max': 2
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show routes with available seats
        self.fields['route'].queryset = BusRoute.objects.filter(
            is_active=True, 
            available_seats__gt=0
        )
        self.fields['route'].widget.attrs.update({'class': 'form-control'})
        
    def clean_num_tickets(self):
        num_tickets = self.cleaned_data.get('num_tickets')
        route = self.cleaned_data.get('route')
        
        # Validate ticket count
        if num_tickets:
            if num_tickets > 2:
                raise forms.ValidationError('Maximum 2 tickets per booking.')
            
            if num_tickets < 1:
                raise forms.ValidationError('Minimum 1 ticket required.')
            
            if route and num_tickets > route.available_seats:
                raise forms.ValidationError(f'Only {route.available_seats} tickets available.')
        
        return num_tickets
    
    def clean_travel_date(self):
        travel_date = self.cleaned_data.get('travel_date')
        
        if travel_date and travel_date < date.today():
            raise forms.ValidationError('Travel date cannot be in the past.')
        
        return travel_date
    
    def clean(self):
        cleaned_data = super().clean()
        route = cleaned_data.get('route')
        travel_date = cleaned_data.get('travel_date')
        user = None
        
        # Check if user is authenticated (for form validation)
        if hasattr(self, 'instance') and hasattr(self.instance, 'user'):
            user = self.instance.user
        
        # Check if user already has a booking for this route on the same date
        if route and travel_date and user:
            existing_booking = BusBooking.objects.filter(
                user=user,
                route=route,
                travel_date=travel_date,
                status='confirmed'
            ).exists()
            
            if existing_booking:
                raise forms.ValidationError('You already have a booking for this route on this date.')
        
        return cleaned_data