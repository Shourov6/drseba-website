# MySQL Setup Guide for DrSeba Healthcare Platform

## Option 1: Using SQLite (Current Default - Recommended for Development)

SQLite is now configured as the default database for local development. No additional setup required!

**To use SQLite:**
1. The project is already configured to use SQLite
2. Run migrations: `python manage.py migrate`
3. Create demo data: `python setup_demo_data.py`
4. Start the server: `python manage.py runserver`

---

## Option 2: Setting Up MySQL (for Production)

If you want to use MySQL with the DrSeba platform, follow these steps:

### Step 1: Reset MySQL Root Password

If you don't know the MySQL root password, you need to reset it:

#### Windows - Using MySQL Command Line Client:

1. **Find MySQL Installation Path:**
   ```
   C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe
   ```

2. **Restart MySQL in safe mode (as Administrator):**
   ```bash
   net stop MySQL80
   "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld" --skip-grant-tables
   ```

3. **In another Administrator Command Prompt, connect as root:**
   ```bash
   "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root
   ```

4. **Reset the password:**
   ```sql
   FLUSH PRIVILEGES;
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'YourNewPassword';
   FLUSH PRIVILEGES;
   EXIT;
   ```

5. **Restart MySQL normally:**
   ```bash
   net start MySQL80
   ```

### Step 2: Create the Database and User

Once you have the root password, use the Python setup script:

```bash
# Activate your virtual environment
venv\Scripts\Activate.ps1

# Run the setup script and enter your root password when prompted
python setup_mysql.py
```

This script will:
- ✓ Create the `drseba_healthcare` database
- ✓ Create the `drseba_user` with password `DrsebaPwd123!@#`
- ✓ Grant all necessary privileges

### Step 3: Configure Django for MySQL

**Option A: Using .env file**

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and uncomment MySQL settings:
   ```
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=drseba_healthcare
   DB_USER=drseba_user
   DB_PASSWORD=DrsebaPwd123!@#
   DB_HOST=localhost
   DB_PORT=3306
   ```

**Option B: Using settings.py directly**

Edit `drseba/settings.py` and modify the DATABASES configuration to use MySQL instead of SQLite.

### Step 4: Run Migrations

```bash
python manage.py migrate
```

This will create all necessary database tables.

### Step 5: Create Demo Data

```bash
python setup_demo_data.py
```

This will populate the database with sample appointments and users.

### Step 6: Run the Development Server

```bash
python manage.py runserver
```

Access the application at http://127.0.0.1:8000/

---

## Database Configuration Details

### SQLite (Default)
- **File:** `db.sqlite3` in the project root
- **Advantages:** 
  - No setup required
  - Perfect for local development
  - Good for testing and learning
- **Drawbacks:** 
  - Not suitable for production
  - Single user at a time
  - Limited to local connections

### MySQL (Production)
- **Database:** `drseba_healthcare`
- **User:** `drseba_user`
- **Password:** `DrsebaPwd123!@#` (change in production!)
- **Host:** `localhost:3306`
- **Charset:** UTF-8mb4 (full Unicode support for Bangla text)
- **Advantages:**
  - Multi-user support
  - Production-ready
  - Better performance with large datasets
  - Remote access capability

---

## Troubleshooting

### MySQL Connection Error: "Access denied for user 'root'@'localhost'"

**Solution:** Reset the root password following the steps above.

### MySQL not running

**Check MySQL service status:**
```bash
Get-Service MySQL80 | Format-List Name, Status
```

**Start MySQL:**
```bash
net start MySQL80
```

### Database "drseba_healthcare" already exists

**Drop the database and recreate:**
```bash
python setup_mysql.py
```

The script automatically drops and recreates the database and user.

---

## Demo Data Information

The `setup_demo_data.py` script creates:
- **3 Sample Patients**
- **3 Sample Doctors**
- **9 Sample Appointments** with mixed statuses:
  - Pending (future appointments)
  - Confirmed (upcoming)
  - Completed (past appointments)
- **Consultation Types:** Online and In-person
- **Service Fees:** Consultation + Platform Service Fee

---

## Admin Panel Access

After setup, access the admin panel:
- **URL:** http://127.0.0.1:8000/admin/
- **Create superuser:** `python manage.py createsuperuser`
- **Username:** admin (or your choice)
- **Password:** Set when creating superuser

---

## Environment Variables Reference

```
# Database Engine
DB_ENGINE = django.db.backends.mysql  # or django.db.backends.sqlite3

# MySQL Credentials
DB_NAME = drseba_healthcare
DB_USER = drseba_user
DB_PASSWORD = your_password
DB_HOST = localhost
DB_PORT = 3306

# Django
DEBUG = True
SECRET_KEY = your-secret-key
ALLOWED_HOSTS = localhost,127.0.0.1

# Timezone
TIME_ZONE = Asia/Dhaka
LANGUAGE_CODE = en-us
```

---

## Next Steps

1. **Set up admin account:** `python manage.py createsuperuser`
2. **Create test data:** `python setup_demo_data.py`
3. **Start development server:** `python manage.py runserver`
4. **Access admin panel:** http://127.0.0.1:8000/admin/
5. **View appointments:** http://127.0.0.1:8000/appointments/

---

**For more help, see the original MYSQL_SETUP.md file.**
