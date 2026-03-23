from django import forms
from .models import LostItem, FoundItem
from datetime import date

class LostItemForm(forms.ModelForm):
    class Meta:
        model = LostItem
        fields = ['title', 'description', 'category', 'location', 'date_lost', 
                  'contact_phone', 'contact_email', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Laptop, Wallet, Phone'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Describe the item in detail (color, brand, unique marks)'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Library, Cafeteria, Parking Lot'
            }),
            'date_lost': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'max': date.today().isoformat()
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '9876543210'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'your@email.com'
            }),
        }
    
    def clean_date_lost(self):
        date_lost = self.cleaned_data.get('date_lost')
        if date_lost and date_lost > date.today():
            raise forms.ValidationError('Date lost cannot be in the future.')
        return date_lost

class FoundItemForm(forms.ModelForm):
    class Meta:
        model = FoundItem
        fields = ['title', 'description', 'category', 'location', 'date_found', 
                  'contact_phone', 'contact_email', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Laptop, Wallet, Phone'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Describe the item in detail (color, brand, unique marks)'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Library, Cafeteria, Parking Lot'
            }),
            'date_found': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'max': date.today().isoformat()
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '9876543210'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'your@email.com'
            }),
        }
    
    def clean_date_found(self):
        date_found = self.cleaned_data.get('date_found')
        if date_found and date_found > date.today():
            raise forms.ValidationError('Date found cannot be in the future.')
        return date_found