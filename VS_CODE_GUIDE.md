# VS Code Quick Start Guide for DrSeba.com

## Opening the Project

1. Open VS Code
2. Click `File` → `Open Folder`
3. Select the `drseba_website` folder
4. Click `Select Folder`

## Setting Up (First Time Only)

### Option 1: Using the Setup Script

**Windows:**
```
Double-click on setup.bat
```

**macOS/Linux:**
```bash
# Open terminal in VS Code (Terminal → New Terminal)
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

1. **Open Terminal**: `Terminal` → `New Terminal`

2. **Create Virtual Environment**:
   ```bash
   # Windows
   python -m venv venv
   
   # macOS/Linux
   python3 -m venv venv
   ```

3. **Activate Virtual Environment**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Populate Sample Data**:
   ```bash
   python manage.py populate_data
   ```

## Running the Server

### Method 1: Using Terminal
```bash
python manage.py runserver
```

### Method 2: Using VS Code Debugger
1. Press `F5` or click `Run` → `Start Debugging`
2. Select "Django Server" from the dropdown

### Method 3: Using VS Code Run Menu
1. Click the play icon (▶) in the top right
2. Select "Django Server"

## Accessing the Website

- **Main Website**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Stopping the Server

- Press `Ctrl+C` in the terminal
- Or click the stop button (⏹) in the debugger

## Useful VS Code Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+`` ` | Open/Close Terminal |
| `Ctrl+Shift+P` | Command Palette |
| `F5` | Start Debugging |
| `Shift+F5` | Stop Debugging |
| `Ctrl+S` | Save File |
| `Ctrl+Shift+F` | Search in Files |

## Making Changes

### After Changing Models:
```bash
python manage.py makemigrations
python manage.py migrate
```

### After Changing Static Files (CSS/JS):
- Just refresh the browser (no restart needed in DEBUG mode)

### After Changing Templates:
- Just refresh the browser (no restart needed)

## Project Structure in VS Code

```
drseba_website/
├── .vscode/              # VS Code settings
│   ├── launch.json       # Debug configurations
│   └── settings.json     # Editor settings
├── doctors/              # Main app
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── urls.py           # URL routes
│   └── admin.py          # Admin settings
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   └── doctors/          # App templates
├── static/               # CSS, JS, images
│   └── css/
│       └── style.css     # Main stylesheet
├── manage.py             # Django commands
└── requirements.txt      # Python packages
```

## Troubleshooting in VS Code

### Python Interpreter Not Found
1. Press `Ctrl+Shift+P`
2. Type "Python: Select Interpreter"
3. Choose the one in `./venv/Scripts/python.exe` (Windows) or `./venv/bin/python` (macOS/Linux)

### Terminal Shows Wrong Python
Make sure the virtual environment is activated. You should see `(venv)` at the start of the prompt.

### Server Won't Start
1. Check if another server is running (port 8000)
2. Try a different port: `python manage.py runserver 8080`

### Changes Not Showing
1. Clear browser cache (Ctrl+Shift+R)
2. Make sure DEBUG = True in settings.py

## Extensions to Install

1. **Python** (Microsoft) - Essential for Python development
2. **Django** (Baptiste Darthenay) - Django-specific features
3. **Bootstrap 5** - For HTML/CSS assistance

To install:
1. Click the Extensions icon (📦) on the left sidebar
2. Search for the extension name
3. Click "Install"

## Getting Help

- Django Documentation: https://docs.djangoproject.com/
- Bootstrap Documentation: https://getbootstrap.com/docs/
- VS Code Documentation: https://code.visualstudio.com/docs
