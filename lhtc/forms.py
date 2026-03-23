from django import forms
from .models import Booking, Room
from datetime import date, datetime

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'purpose', 'title', 'description', 'date', 
                  'start_time', 'end_time', 'estimated_strength', 
                  'year_batch', 'branches', 'registration_deadline']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter event description'}),
            'estimated_strength': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'year_batch': forms.Select(attrs={'class': 'form-control'}),
            'branches': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'cse,ece,mech'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].widget.attrs.update({'class': 'form-control'})
        self.fields['purpose'].widget.attrs.update({'class': 'form-control'})
        
    def clean(self):
        cleaned_data = super().clean()
        date_val = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        registration_deadline = cleaned_data.get('registration_deadline')
        
        if date_val and date_val < date.today():
            raise forms.ValidationError('Event date cannot be in the past.')
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError('End time must be after start time.')
        
        if registration_deadline and registration_deadline < datetime.now():
            raise forms.ValidationError('Registration deadline cannot be in the past.')
        
        return cleaned_data

class BookingEditForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'purpose', 'title', 'description', 'date', 
                  'start_time', 'end_time', 'estimated_strength', 
                  'year_batch', 'branches', 'registration_deadline']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estimated_strength': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }