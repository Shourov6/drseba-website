# 🏥 DrSeba Healthcare Platform - MySQL Setup Guide

## Prerequisites
- MySQL Server 5.7+ or 8.0+ installed and running
- Python 3.8+
- Django 4.2+

## Step-by-Step Setup

### Step 1: Ensure MySQL Server is Running

**Windows:**
```bash
# Check if MySQL is running
wmic logicaldisk get name | find /i "mysql"

# Start MySQL service (Run as Administrator)
net start MySQL80  # if using MySQL 8.0
# or
net start MySQL57  # if using MySQL 5.7
```

**Alternative (via Services):**
- Open Services (services.msc)
- Find "MySQL80" or "MySQL57"
- Right-click → Start

**Verify MySQL is running:**
```bash
mysql -u root -p
# If it connects, MySQL is running. Type: exit
```

### Step 2: Install Python Dependencies

All required packages are already in `requirements.txt`:

```bash
# Navigate to project directory
cd "c:\Users\Shourov\Downloads\Kimi_Agent_DrSeba Healthcare Platform\drseba"

# Install dependencies (if not already installed)
pip install -r requirements.txt
```

**Packages installed:**
- `Django >= 4.2.0`
- `mysqlclient >= 2.2.0` (MySQL database adapter)
- `mysql-connector-python` (for setup script)
- `Pillow` (image handling)
- `django-crispy-forms` (form styling)
- `python-dotenv` (environment variables)

### Step 3: Automatically Create MySQL Database

Run the automated setup script:

```bash
python setup_mysql.py
```

**What it does:**
✓ Creates database: `drseba_healthcare`
✓ Creates dedicated user: `drseba_user` (optional)
✓ Sets UTF-8 character encoding
✓ Grants all necessary privileges

**Manual Alternative (if script fails):**

Open MySQL Command Line or MySQL Workbench and run:

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS drseba_healthcare 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Create user (optional)
CREATE USER IF NOT EXISTS 'drseba_user'@'localhost' 
IDENTIFIED BY 'DrsebaPwd123!@#';

-- Grant privileges
GRANT ALL PRIVILEGES ON drseba_healthcare.* 
TO 'drseba_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
SELECT USER FROM mysql.user WHERE USER='drseba_user';
```

### Step 4: Configure Django Settings

**Option A: Using Root User (Simple)**

Edit `.env` file in project root:

```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=drseba_healthcare
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
```

**Option B: Using Application User (Recommended)**

Edit `.env` file in project root:

```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=drseba_healthcare
DB_USER=drseba_user
DB_PASSWORD=DrsebaPwd123!@#
DB_HOST=localhost
DB_PORT=3306
```

**Option C: Custom Configuration**

Update values as per your MySQL setup. The application reads from `.env` first, then uses defaults.

### Step 5: Run Database Migrations

```bash
# Navigate to project directory
cd "c:\Users\Shourov\Downloads\Kimi_Agent_DrSeba Healthcare Platform\drseba"

# Apply migrations
python manage.py migrate
```

**Expected output:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, accounts, doctors, appointments, payments, dashboards
Running migrations:
  Applying ... OK
  ...
```

**If you get charset errors:**

The settings.py already handles this with:
```python
'OPTIONS': {
    'charset': 'utf8mb4',
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
}
```

### Step 6: Load Demo Data (Optional)

```bash
python manage.py create_specialties
python manage.py create_demo_data
```

### Step 7: Create Superuser (First Time)

```bash
python manage.py createsuperuser
```

Follow the prompts to create admin account.

### Step 8: Run Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

---

## Troubleshooting

### Error: "Access denied for user 'root'@'localhost'"
- MySQL credentials are wrong
- Password is incorrect in `.env`
- Solution: Update `.env` with correct credentials

### Error: "Can't connect to MySQL server on 'localhost'"
- MySQL server is not running
- Solution: Start MySQL service (see Step 1)

### Error: "No module named 'mysqlclient'"
- Install mysqlclient: `pip install mysqlclient`

### Error: "Byte string argument without an encoding"
- This is already fixed in settings.py with `utf8mb4` charset
- Make sure you're using the updated settings.py

### Error: "1071 Specified key was too long"
- Already handled by using `utf8mb4_unicode_ci` collation
- Make sure setup_mysql.py was used

### Migrating from SQLite to MySQL

If you had existing SQLite data:
1. Export SQLite data: `python manage.py dumpdata > data.json`
2. Run migrations on MySQL
3. Load data: `python manage.py loaddata data.json`

---

## Verification

Test the connection:

```bash
python manage.py dbshell
# If it opens mysql prompt, connection is successful
# Type: exit
```

Or create a test view:

```bash
python manage.py shell
```

```python
from django.db import connection
print(connection.get_connection_params())
# Should show MySQL connection parameters
```

---

## Switching Back to SQLite (If Needed)

Update `drseba/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Then run migrations again.

---

## Environment Variables Reference

All these can be set in `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| DB_ENGINE | django.db.backends.mysql | Database backend |
| DB_NAME | drseba_healthcare | Database name |
| DB_USER | root | Database user |
| DB_PASSWORD | (empty) | Database password |
| DB_HOST | localhost | Database host |
| DB_PORT | 3306 | Database port |
| DEBUG | True | Django debug mode |
| SECRET_KEY | (hardcoded) | Django secret key |
| TIME_ZONE | Asia/Dhaka | Application timezone |

---

## Next Steps

1. ✅ Run `setup_mysql.py`
2. ✅ Configure `.env` with MySQL credentials
3. ✅ Run `python manage.py migrate`
4. ✅ Create superuser with `createsuperuser`
5. ✅ Load demo data (optional)
6. ✅ Run development server

**Everything is now set up with MySQL!** 🎉

---

## Support

For issues:
1. Check MySQL is running
2. Verify credentials in `.env`
3. Check logs in console
4. Ensure all dependencies are installed: `pip install -r requirements.txt`

