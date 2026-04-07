#!/bin/bash

echo "=========================================="
echo "DrSeba.com - Django Project Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed! Please install Python 3.10 or higher."
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate

echo "Creating superuser..."
echo "Please enter admin details:"
python manage.py createsuperuser

echo "Populating sample data..."
python manage.py populate_data

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To run the server, use:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Then open: http://127.0.0.1:8000/"
echo ""
echo "Admin panel: http://127.0.0.1:8000/admin/"
echo ""
