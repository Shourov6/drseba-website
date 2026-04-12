"""
URL configuration for core app
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    path('employee/', views.employee_dashboard_view, name='employee_dashboard'),
    
    # Doctors
    path('doctors/', views.doctors_list_view, name='doctors_list'),
    path('doctors/add/', views.doctor_add_view, name='doctor_add'),
    path('doctors/<str:doctor_id>/', views.doctor_detail_view, name='doctor_detail'),
    path('doctors/<str:doctor_id>/edit/', views.doctor_edit_view, name='doctor_edit'),
    path('doctors/<str:doctor_id>/delete/', views.doctor_delete_view, name='doctor_delete'),
    
    # Hospitals
    path('hospitals/', views.hospitals_list_view, name='hospitals_list'),
    path('hospitals/add/', views.hospital_add_view, name='hospital_add'),
    path('hospitals/<str:hospital_id>/edit/', views.hospital_edit_view, name='hospital_edit'),
    path('hospitals/<str:hospital_id>/delete/', views.hospital_delete_view, name='hospital_delete'),
    
    # Appointments
    path('appointments/', views.appointments_list_view, name='appointments_list'),
    path('appointments/add/', views.appointment_add_view, name='appointment_add'),
    path('appointments/<str:appointment_id>/edit/', views.appointment_edit_view, name='appointment_edit'),
    path('appointments/<str:appointment_id>/delete/', views.appointment_delete_view, name='appointment_delete'),
    path('appointments/<str:appointment_id>/assign/', views.appointment_assign_view, name='appointment_assign'),
    
    # Employees
    path('employees/', views.employees_list_view, name='employees_list'),
    path('employees/add/', views.employee_add_view, name='employee_add'),
    path('employees/<str:employee_id>/', views.employee_detail_view, name='employee_detail'),
    path('employees/<str:employee_id>/edit/', views.employee_edit_view, name='employee_edit'),
    path('employees/<str:employee_id>/delete/', views.employee_delete_view, name='employee_delete'),
    
    # Payments
    path('payments/', views.payments_list_view, name='payments_list'),
    path('payments/add/', views.payment_add_view, name='payment_add'),
    path('payments/<str:invoice_id>/', views.payment_invoice_view, name='payment_invoice'),
    path('payments/<str:invoice_id>/edit/', views.payment_edit_view, name='payment_edit'),
    path('payments/<str:invoice_id>/delete/', views.payment_delete_view, name='payment_delete'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),
    
    # Patients
    path('patients/<int:patient_id>/', views.patient_detail_view, name='patient_detail'),
]
