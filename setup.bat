@echo off
echo ==========================================
echo DrSeba.com - Django Project Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.10 or higher.
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Running migrations...
python manage.py migrate

echo Creating superuser...
echo Please enter admin details:
python manage.py createsuperuser

echo Populating sample data...
python manage.py populate_data

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To run the server, use:
echo   python manage.py runserver
echo.
echo Then open: http://127.0.0.1:8000/
echo.
echo Admin panel: http://127.0.0.1:8000/admin/
echo.
pause
