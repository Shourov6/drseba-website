# DrSeba.com - Healthcare Website

A Django-based healthcare platform for finding and booking appointments with verified doctors in Bangladesh.

## Features

- **Doctor Search**: Find doctors by name, specialty, or location
- **Specialties**: Browse doctors by medical specialties
- **Featured Doctors**: View top-rated verified doctors
- **Partner Hospitals**: Explore affiliated healthcare facilities
- **Emergency Services**: Quick access to emergency contacts
- **Online Booking**: Book appointments with doctors
- **Responsive Design**: Works on desktop, tablet, and mobile

## Tech Stack

- **Backend**: Django 5.0+
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Database**: SQLite (default)
- **Icons**: Bootstrap Icons

## Project Structure

```
drseba_website/
├── drseba/                 # Main Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── doctors/                # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin configuration
│   └── management/        # Custom management commands
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   └── doctors/          # App templates
├── static/               # Static files (CSS, JS, images)
│   └── css/
├── media/                # User-uploaded files
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## How to Run in VS Code (Step-by-Step)

### Prerequisites

1. **Install Python** (3.10 or higher)
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Install VS Code**
   - Download from: https://code.visualstudio.com/

3. **Install VS Code Extensions**
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X or Cmd+Shift+X on Mac)
   - Search and install:
     - **Python** (by Microsoft)
     - **Django** (by Baptiste Darthenay)

### Step 1: Open Project in VS Code

1. Open VS Code
2. Click on `File` → `Open Folder`
3. Select the `drseba_website` folder
4. Click `Select Folder`

### Step 2: Open Terminal in VS Code

1. Click on `Terminal` in the top menu
2. Select `New Terminal`
3. A terminal will open at the bottom of VS Code

### Step 3: Create Virtual Environment (Recommended)

In the terminal, run:

```bash
# Windows
python -m venv venv

# macOS/Linux
python3 -m venv venv
```

### Step 4: Activate Virtual Environment

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

You'll see `(venv)` at the start of your terminal prompt when activated.

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Run Migrations

```bash
python manage.py migrate
```

This creates the database tables.

### Step 7: Create Superuser (Admin Access)

```bash
python manage.py createsuperuser
```

Enter:
- Username: `admin`
- Email: `admin@example.com`
- Password: (choose a password, at least 8 characters)

### Step 8: Populate Sample Data

```bash
python manage.py populate_data
```

This creates sample doctors, specialties, hospitals, etc.

### Step 9: Run the Development Server

```bash
python manage.py runserver
```

You'll see output like:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Step 10: Access the Website

1. Open your web browser
2. Go to: http://127.0.0.1:8000/
3. The website should load!

### Admin Panel Access

- Go to: http://127.0.0.1:8000/admin/
- Login with the superuser credentials you created
- Here you can manage doctors, specialties, hospitals, etc.

## Common Commands

```bash
# Run development server
python manage.py runserver

# Run server on different port
python manage.py runserver 8080

# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Open Django shell
python manage.py shell

# Populate sample data
python manage.py populate_data

# Collect static files (for production)
python manage.py collectstatic
```

## Troubleshooting

### Issue: "python" command not found
**Solution**: Use `python3` instead of `python` (macOS/Linux)

### Issue: "pip" command not found
**Solution**: 
```bash
python -m pip install -r requirements.txt
```

### Issue: Port already in use
**Solution**: Use a different port
```bash
python manage.py runserver 8080
```

### Issue: Migration errors
**Solution**: Delete db.sqlite3 and migrations, then recreate
```bash
# Delete database
rm db.sqlite3  # macOS/Linux
del db.sqlite3  # Windows

# Delete migration files (except __init__.py)
# Then run:
python manage.py makemigrations
python manage.py migrate
```

### Issue: Static files not loading
**Solution**: Make sure DEBUG = True in settings.py for development

## Customization

### Change Website Name/Logo
Edit in `templates/base.html`

### Change Colors
Edit in `static/css/style.css`

### Add More Specialties
1. Go to Admin panel: http://127.0.0.1:8000/admin/
2. Login with superuser
3. Click on "Specialties"
4. Click "Add Specialty"

### Add More Doctors
1. Go to Admin panel
2. Click on "Doctors"
3. Click "Add Doctor"
4. Fill in the details

## Deployment (Production)

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Set proper `ALLOWED_HOSTS`
3. Use PostgreSQL instead of SQLite
4. Set up a web server (Nginx/Apache)
5. Use Gunicorn or uWSGI
6. Configure SSL certificate

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please create an issue in the repository.
