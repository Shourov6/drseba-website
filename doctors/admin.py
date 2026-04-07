from django.contrib import admin
from .models import Specialty, Hospital, Doctor, Testimonial, Service, Statistic


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color']
    search_fields = ['name']


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'address']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty', 'experience_years', 'rating', 'consultation_fee', 'is_featured', 'is_active']
    list_filter = ['specialty', 'is_featured', 'is_verified', 'is_active', 'gender']
    search_fields = ['name', 'about', 'address']
    list_editable = ['is_featured', 'is_active']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'is_active', 'created_at']
    list_filter = ['rating', 'is_active']
    search_fields = ['name', 'content']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    search_fields = ['name']


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ['value', 'label', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    search_fields = ['label']
