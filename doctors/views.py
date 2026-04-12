from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Doctor, Specialty, Hospital, Testimonial, Service, Statistic


def home(request):
    """Home page view"""
    context = {
        'services': Service.objects.filter(is_active=True)[:4],
        'statistics': Statistic.objects.filter(is_active=True)[:3],
        'specialties': Specialty.objects.all()[:8],
        'featured_doctors': Doctor.objects.filter(is_featured=True, is_active=True)[:6],
        'testimonials': Testimonial.objects.filter(is_active=True)[:3],
        'hospitals': Hospital.objects.filter(is_active=True)[:4],
    }
    return render(request, 'doctors/home.html', context)


def doctor_list(request):
    """List all doctors with search and filter"""
    doctors = Doctor.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        doctors = doctors.filter(
            Q(name__icontains=search_query) |
            Q(specialty__name__icontains=search_query) |
            Q(about__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Filter by specialty
    specialty_id = request.GET.get('specialty')
    if specialty_id:
        doctors = doctors.filter(specialty_id=specialty_id)
    
    context = {
        'doctors': doctors,
        'specialties': Specialty.objects.all(),
        'search_query': search_query,
        'selected_specialty': specialty_id,
    }
    return render(request, 'doctors/doctor_list.html', context)


def doctor_detail(request, pk):
    """Doctor detail page"""
    doctor = get_object_or_404(Doctor, pk=pk, is_active=True)
    context = {
        'doctor': doctor,
        'related_doctors': Doctor.objects.filter(specialty=doctor.specialty, is_active=True).exclude(pk=pk)[:3],
    }
    return render(request, 'doctors/doctor_detail.html', context)


def specialty_list(request):
    """List all specialties"""
    context = {
        'specialties': Specialty.objects.all(),
    }
    return render(request, 'doctors/specialty_list.html', context)


def hospital_list(request):
    """List all partner hospitals"""
    context = {
        'hospitals': Hospital.objects.filter(is_active=True),
    }
    return render(request, 'doctors/hospital_list.html', context)


def about(request):
    """About page"""
    context = {
        'statistics': Statistic.objects.filter(is_active=True),
    }
    return render(request, 'doctors/about.html', context)


def emergency(request):
    """Emergency services page"""
    return render(request, 'doctors/emergency.html')
