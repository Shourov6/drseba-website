"""
Views for the main DrSeba app
"""
from django.shortcuts import render
from doctors.models import Specialty


def home(request):
    """Home page view with popular specialties"""
    # Get popular specialties (ordered by order field)
    specialties = Specialty.objects.filter(is_active=True).order_by('order')
    
    context = {
        'specialties': specialties,
    }
    
    return render(request, 'home.html', context)
