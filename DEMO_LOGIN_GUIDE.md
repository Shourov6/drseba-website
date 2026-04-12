# DrSeba.com - Demo Login Credentials & Dashboard Guide

## Demo Accounts

### 1. PATIENT ACCOUNT
```
Username: patient
Password: demo123456
Email: patient@drseba.com
Role: Patient
```
**Dashboard URL:** `http://localhost:8000/dashboard/`

**Patient Dashboard Features:**
- View booked appointments
- Search and book new doctors
- Manage appointments (reschedule/cancel)
- View appointment history
- Doctor reviews and ratings
- Payment history

**How to Access:**
1. Go to `http://localhost:8000/accounts/login/`
2. Enter username: `patient`
3. Enter password: `demo123456`
4. Click Login
5. Access Dashboard: `http://localhost:8000/dashboard/`

---

### 2. DOCTOR ACCOUNTS

#### Doctor 1
```
Username: dr.karim
Password: demo123456
Email: dr.karim@drseba.com
Role: Doctor (Verified)
Specialty: Cardiology
```

#### Doctor 2
```
Username: dr.fatima
Password: demo123456
Email: dr.fatima@drseba.com
Role: Doctor (Verified)
Specialty: Pediatrics
```

#### Doctor 3
```
Username: dr.hasan
Password: demo123456
Email: dr.hasan@drseba.com
Role: Doctor (Verified)
Specialty: Ophthalmology
```

**Doctor Dashboard Features:**
- View patient appointments
- Manage availability
- View consultations
- Patient reviews
- Income/earnings
- Medical records

**How to Access Doctor Dashboard:**
1. Go to `http://localhost:8000/accounts/login/`
2. Use any doctor username (e.g., `dr.karim`)
3. Contact admin for password reset if needed
4. Access Dashboard: `http://localhost:8000/dashboard/`

---

### 3. ADMIN ACCOUNT
```
Username: N/A (Use Django Admin)
Role: Super Admin
```

**Admin Dashboard URL:** `http://localhost:8000/admin/`

**Admin Features:**
- Manage users (patients, doctors)
- Verify doctors
- Manage hospitals and specialties
- View all appointments
- Financial reports
- System settings

**Note:** Contact development team for admin credentials

---

## Create New Demo Accounts (Optional)

To create fresh demo accounts, run:

```bash
python manage.py shell
```

Then execute:

```python
from django.contrib.auth import get_user_model
from accounts.models import PatientProfile

User = get_user_model()

# Create Patient
patient = User.objects.create_user(
    username='demo_patient',
    email='demo_patient@drseba.com',
    password='Demo@12345',
    first_name='Demo',
    last_name='Patient',
    role='patient'
)
PatientProfile.objects.create(user=patient)

# Create Doctor
doctor = User.objects.create_user(
    username='demo_doctor',
    email='demo_doctor@drseba.com',
    password='Demo@12345',
    first_name='Demo',
    last_name='Doctor',
    role='doctor'
)

# Create Admin
admin = User.objects.create_user(
    username='demo_admin',
    email='demo_admin@drseba.com',
    password='Demo@12345',
    first_name='Demo',
    last_name='Admin',
    role='admin',
    is_staff=True,
    is_superuser=True
)

print("Demo accounts created!")
```

---

## Find Doctors Page Features

### New Contact Section (Right Side)
The Find Doctors page now includes an enhanced "Need Help?" contact card on the right side with:

✅ **Call Button** - Direct link to call center  
✅ **WhatsApp Button** - Chat via WhatsApp  
✅ **Live Chat Button** - Real-time support (coming soon)  
✅ **Social Media Link** - Follow DrSeba on Facebook  
✅ **Call Now Button** - Quick action button  

**Visual Effects:**
- Smooth slide-in animation on page load
- Hover effects with lift animation
- Color-coded contact options (blue, green, cyan)
- Sticky positioning (follows scroll)
- Responsive design for mobile

---

## Dashboard Overview

### Patient Dashboard
- **Home/Overview:** Upcoming appointments, quick actions
- **My Appointments:** All booked appointments with status
- **Find Doctors:** Search and filter doctors
- **Book Appointment:** Step-by-step booking wizard
- **Medical Records:** Store health documents
- **Reviews:** Leave reviews for doctors
- **Settings:** Profile, preferences, notifications

### Doctor Dashboard
- **Home/Overview:** Today's appointments
- **My Schedule:** Manage availability
- **Appointments:** View patient appointments
- **Patients:** Patient list and medical history
- **Reviews:** View patient reviews
- **Earnings:** Income tracking and payments
- **Settings:** Profile, consultation fees, availability

### Admin Dashboard
- **User Management:** Create/edit/delete users
- **Doctor Verification:** Approve pending doctors
- **Hospitals:** Manage hospital information
- **Specialties:** Manage doctor specialties
- **Appointments:** Monitor all appointments
- **Reports:** Financial and usage reports
- **Settings:** System configuration

---

## Testing Workflow

### 1. Patient Journey
```
1. Go to home: http://localhost:8000/
2. Search for doctor using auto-suggest
3. Click "Find Doctors" link
4. Browse doctor list
5. Click "Book Appointment"
6. Complete booking form
7. Make payment
8. View confirmation
9. Check appointment in dashboard
```

### 2. Doctor Profile Viewing
```
1. On home page, use search bar
2. Type doctor name (e.g., "dr.karim")
3. See auto-suggest dropdown
4. Click on doctor result
5. View doctor profile
6. See availability calendar
7. Book appointment
```

### 3. Advanced Search
```
1. Go to /doctors/
2. Use sidebar filters:
   - Specialty filter
   - District filter
   - Gender filter
   - Fee range slider
3. Apply filters
4. See filtered results
```

---

## Common Dashboard URLs

| Role | Dashboard | Admin | Notes |
|------|-----------|-------|-------|
| Patient | `/dashboard/` | N/A | View appointments |
| Doctor | `/dashboard/` | N/A | Manage schedule |
| Admin | `/dashboard/` | `/admin/` | Full system access |

---

## Features Showcase

### Auto-Suggest Search
- Type 2+ characters to see suggestions
- Categories: Doctors, Specialties, Hospitals
- Click any suggestion to navigate
- Available on home page and doctors page

### Responsive Design
- Mobile: Full-screen layout
- Tablet: Adjusted spacing
- Desktop: Multi-column layout

### Modern UI
- Gradient backgrounds
- Smooth animations
- Color-coded buttons
- Icons for accessibility

---

## Contact Information

**Support Team:**
- 📞 Call: 09678-901234
- 💬 WhatsApp: +8801700123456
- 💻 Live Chat: Available 24/7 (button on Find Doctors page)
- 📧 Email: support@drseba.com
- 👍 Facebook: @DrSeba.com

---

## Troubleshooting

**Q: Can't login?**
A: Ensure you're using correct username and password. Contact admin for account creation.

**Q: Dashboard not loading?**
A: Clear browser cache, try incognito mode, or check if you're logged in.

**Q: Doctor listing empty?**
A: Make sure doctors are marked as verified and active in admin panel.

**Q: Search not working?**
A: Check API endpoint at `/doctors/api/search-suggestions/` is accessible.

---

## Development Notes

**Key Files:**
- Login: `accounts/views.py` - `login_view()`
- Dashboard: `dashboards/views.py` - `dashboard_index()`
- Doctor List: `doctors/views.py` - `doctor_list()`
- Auto-suggest: `doctors/views.py` - `search_suggestions()`

**Database:** SQLite3 at `db.sqlite3`

**Static Files:** `static/css/modern-healthcare.css`

**Templates:** `templates/` directory

---

Last Updated: April 10, 2026
