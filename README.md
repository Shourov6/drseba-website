# DrSeva Healthcare Admin Dashboard

A complete healthcare admin dashboard built with Django and Bootstrap 5. This system supports role-based authentication for Admin and Employee users, with comprehensive management of doctors, hospitals, appointments, employees, and payments.

## Features

### Authentication & Role-Based Access
- Login with role selection (Admin / Employee)
- Admin Dashboard: Full access to all sections
- Employee Dashboard: Personal profile, managed appointments, and performance metrics
- Logout functionality

### Admin Dashboard - Main Sections

#### 1. Dashboard/Analytics
- Key metrics cards: Total Doctors, Hospitals, Appointments, Revenue, Active Employees
- Recent appointments list
- Charts and analytics

#### 2. Doctors Management
- Doctor List with all details
- Multi-step Add Doctor Form (6 steps)
- Edit and Delete functionality
- Doctor Profile Modal
- Multi-hospital support for doctors

#### 3. Hospitals Management
- Hospital List with card view
- Add/Edit/Delete functionality
- Hospital details with bed capacity

#### 4. Appointments Management
- Tab-based layout: Distributed & Non-Distributed Appointments
- Full appointment edit modal with status management
- Employee assignment workflow
- Status auto-calculation logic

#### 5. Employees Management
- Employee List Table
- Add/Edit/Delete functionality
- Employee Profile Modal

#### 6. Payments & Billing
- Payments Table with status tracking
- Invoice generation and preview
- Payment method tracking

### Employee Dashboard
- Profile Section with personal info
- My Managed Appointments
- Performance Metrics

## Technology Stack

- **Backend**: Django 5.0.2
- **Database**: SQLite (default)
- **Frontend**: HTML, CSS, Bootstrap 5, Font Awesome
- **Python**: 3.8+

## Project Structure

```
drseva_backend/
├── drseva_backend/          # Project configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                     # Main application
│   ├── __init__.py
│   ├── admin.py             # Admin panel configuration
│   ├── forms.py             # Form definitions
│   ├── models.py            # Database models
│   ├── urls.py              # URL routing
│   └── views.py             # View functions
├── templates/               # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── employee_dashboard.html
│   ├── doctors/
│   ├── hospitals/
│   ├── appointments/
│   ├── employees/
│   ├── payments/
│   └── patients/
├── manage.py
├── requirements.txt
└── README.md
```

## Setup Instructions

### Step 1: Create Virtual Environment

```bash
# Open VS Code terminal
# Navigate to the project folder
cd drseva_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Create Superuser

```bash
python manage.py createsuperuser
```

Enter the following when prompted:
- Username: admin
- Email: admin@drseva.com
- Password: admin123

### Step 5: Create Default Users

Run the Django shell to create default users:

```bash
python manage.py shell
```

Then paste the following commands:

```python
from core.models import User, Employee

# Create admin user if not exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@drseva.com', 'admin123', role='admin')
    print("Admin user created")

# Create employee user
if not User.objects.filter(username='employee').exists():
    user = User.objects.create_user('employee', 'employee@drseva.com', 'employee123', role='employee', first_name='John Employee')
    Employee.objects.create(
        user=user,
        name='John Employee',
        age=30,
        gender='Male',
        phone='+8801234567890',
        email='employee@drseva.com',
        role='Employee'
    )
    print("Employee user created")

exit()
```

### Step 6: Run the Development Server

```bash
python manage.py runserver
```

### Step 7: Access the Application

- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

### Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Employee | employee | employee123 |

## GitHub Team Workflow

### Clone the Repository

```bash
git clone <repo-link>
cd drseva_backend
```

### Create and Switch to Your Branch

```bash
git checkout -b esha-backend
```

### Make Changes and Commit

```bash
# After making changes
git add .
git commit -m "complete backend"
```

### Push to Remote

```bash
git push origin esha-backend
```

### Merge with Main Branch

```bash
# Switch to main
git checkout main
git pull origin main

# Switch back to your branch
git checkout esha-backend

# Merge main into your branch
git merge main

# Resolve any conflicts if needed
# Then push again
git push origin esha-backend
```

## Models Overview

### User
- Custom user model with role-based access
- Fields: username, email, role (admin/employee), phone, profile_photo

### Doctor
- Personal and professional information
- Multi-hospital support via DoctorHospital model
- Fields: name, age, gender, specialty, qualification, experience, etc.

### Hospital
- Hospital information and capacity
- Fields: hospital_id, name, location, contact, total_beds, icu_beds, status

### DoctorHospital (Many-to-Many)
- Links doctors to hospitals with schedule details
- Fields: doctor, hospital, days, time, consultation_fee, service_charge

### Patient
- Patient information
- Fields: name, age, gender, phone, email

### Employee
- Employee information and role
- Fields: employee_id, name, age, gender, phone, email, role, status

### Appointment
- Appointment booking with status tracking
- Fields: patient, doctor, date, time, type, service_charge, manager_status, doctor_status, final_status

### Payment
- Payment/Invoice tracking
- Fields: invoice_id, patient, doctor, consultation_fee, service_charge, total_amount, payment_method, status

## Status Logic for Appointments

The final status is automatically calculated based on Manager and Doctor status:

- If either = Cancelled → Final = Cancelled
- If either = Pending → Final = Pending
- If both = Confirmed → Final = Confirmed

## Admin Panel

Access the Django admin panel at `/admin/` to manage all data:

- All models are registered with custom list displays
- Search and filter functionality available
- Inline editing for doctor-hospital relationships

## Screenshots

The dashboard includes:
- Clean, modern UI with Bootstrap 5
- Responsive design for mobile and desktop
- Color-coded status badges
- Interactive charts and analytics
- Smooth animations and transitions

## Support

For any issues or questions, please contact the development team.

## License

This project is proprietary and confidential.
