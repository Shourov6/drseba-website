from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.home, name='home'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('specialties/', views.specialty_list, name='specialty_list'),
    path('hospitals/', views.hospital_list, name='hospital_list'),
    path('about/', views.about, name='about'),
    path('emergency/', views.emergency, name='emergency'),
]
