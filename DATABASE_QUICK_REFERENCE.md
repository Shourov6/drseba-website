# 🗄️ DrSeba Healthcare Platform - Database Quick Reference

## Current Status
```
┌─────────────────────────────────────────────┐
│   Database: SQLite (db.sqlite3)             │
│   Status: ✅ Ready to Use                   │
│   Demo Data: ✅ Loaded (24 appointments)    │
│   Admin User: ✅ admin                      │
│   System Check: ✅ No Issues                │
└─────────────────────────────────────────────┘
```

---

## 📊 Database Comparison

| Feature | SQLite | MySQL |
|---------|--------|-------|
| **Setup Time** | None | ~5 minutes |
| **Configuration** | Automatic | Manual |
| **File Size** | Small | Scalable |
| **Concurrent Users** | 1 | Many |
| **Production Ready** | ❌ No | ✅ Yes |
| **Remote Access** | ❌ No | ✅ Yes |
| **Current Status** | ✅ Active | ⚠️ Available |

---

## 🚀 Quick Start (SQLite)

### Start Server
```bash
venv\Scripts\Activate.ps1
python manage.py runserver
```

### Access Application
- **App:** http://127.0.0.1:8000/
- **Admin:** http://127.0.0.1:8000/admin/ (username: admin)

---

## 🔄 Switch to MySQL (3 Steps)

### Step 1: Setup MySQL
```bash
python setup_mysql.py
# Enter MySQL root password when prompted
```

### Step 2: Update Configuration
Edit `.env` file - uncomment MySQL section:
```
DB_ENGINE=django.db.backends.mysql
DB_NAME=drseba_healthcare
DB_USER=drseba_user
DB_PASSWORD=DrsebaPwd123!@#
DB_HOST=localhost
DB_PORT=3306
```

### Step 3: Migrate Data
```bash
python manage.py migrate
python setup_demo_data.py
```

---

## 📝 .env File Format

```ini
# OPTION 1: SQLite (Current)
DB_ENGINE=django.db.backends.sqlite3

# OPTION 2: MySQL (Uncomment to use)
# DB_ENGINE=django.db.backends.mysql
# DB_NAME=drseba_healthcare
# DB_USER=drseba_user
# DB_PASSWORD=DrsebaPwd123!@#
# DB_HOST=localhost
# DB_PORT=3306

# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=*
TIME_ZONE=Asia/Dhaka
LANGUAGE_CODE=en-us
```

---

## 🔧 Common Database Tasks

### Change Admin Password
```bash
python manage.py changepassword admin
```

### Create New Superuser
```bash
python manage.py createsuperuser
```

### Reset Database (SQLite)
```bash
# Delete the file and re-run migrations
rm db.sqlite3
python manage.py migrate
python setup_demo_data.py
```

### Reset Database (MySQL)
```bash
python setup_mysql.py  # Re-creates database
python manage.py migrate
python setup_demo_data.py
```

### View Database Stats
```bash
python manage.py shell
>>> from appointments.models import Appointment
>>> Appointment.objects.count()
```

---

## 🗃️ Demo Data Contents

| Entity | Count | Details |
|--------|-------|---------|
| Appointments | 24 | Mixed statuses (pending, confirmed, completed) |
| Patients | Multiple | With profiles and medical history |
| Doctors | Multiple | With specialties and ratings |
| Hospitals | Multiple | With chamber and ICU bed info |
| Payments | Multiple | Payment records for appointments |
| Reviews | Multiple | Doctor ratings and comments |

---

## 📍 Database File Locations

### SQLite
```
C:\...\drseba\db.sqlite3
```
(Local file, no server needed)

### MySQL
```
Database: drseba_healthcare
Host: localhost:3306
User: drseba_user
Password: DrsebaPwd123!@#
```
(Requires MySQL Server 8.0+)

---

## ⚙️ Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `.env` | Current configuration | `./` |
| `.env.example` | Configuration template | `./` |
| `settings.py` | Django DB settings | `drseba/` |
| `setup_mysql.py` | MySQL setup script | `./` |
| `migrate_to_mysql.py` | Migration tool | `./` |
| `setup_demo_data.py` | Demo data loader | `./` |

---

## 🔐 Database Credentials

### Admin Account
```
Username: admin
Password: (Set during creation or changepassword command)
Email: admin@drseba.local
```

### MySQL Account (if using MySQL)
```
User: drseba_user
Password: DrsebaPwd123!@#
Privilege: All on drseba_healthcare
```

### MySQL Root (for setup only)
```
User: root
Password: (Your local MySQL installation password)
```

---

## 🆘 Troubleshooting

### "Database Locked" Error (SQLite)
```bash
# Close all connections and try again
# Or reset database
rm db.sqlite3
python manage.py migrate
```

### "Access Denied" Error (MySQL)
```bash
# Check MySQL service is running
net start MySQL80

# Verify .env credentials
# Re-run setup: python setup_mysql.py
```

### "Table Does Not Exist" Error
```bash
python manage.py migrate
```

### Admin Panel Not Working
```bash
python manage.py createsuperuser
# Or reset password
python manage.py changepassword admin
```

---

## 📚 Documentation Files

- **SETUP_COMPLETE.md** - Complete setup summary
- **MYSQL_COMPLETE_SETUP.md** - Detailed MySQL installation guide
- **README.md** - Project overview
- **DESIGN_SYSTEM.md** - Design and architecture
- **IMPLEMENTATION_SUMMARY.md** - Feature implementation details

---

## ✅ Verification Checklist

- [x] Database initialized (SQLite)
- [x] All migrations applied
- [x] Demo data loaded
- [x] Admin user created
- [x] .env file configured
- [x] System health check passed
- [x] MySQL setup script available
- [x] Documentation complete

---

## 🎯 Next Steps

1. **Start Server:** `python manage.py runserver`
2. **Test Admin:** http://127.0.0.1:8000/admin/
3. **View Demo Data:** Check appointments in admin panel
4. **To Switch to MySQL:** Follow "Switch to MySQL" section above

---

## 📞 Support Resources

| Topic | Resource |
|-------|----------|
| **MySQL Setup** | MYSQL_COMPLETE_SETUP.md |
| **Project Architecture** | DESIGN_SYSTEM.md |
| **Features** | IMPLEMENTATION_SUMMARY.md |
| **General Info** | README.md |
| **Database Config** | .env file |

---

**Status:** ✅ Production Ready (with MySQL setup)  
**Current:** 🚀 SQLite for Development  
**Last Updated:** April 12, 2026

---

## 💡 Pro Tips

1. **Development:** Use SQLite for speed and simplicity
2. **Production:** Switch to MySQL for scalability
3. **Backup:** Regularly back up db.sqlite3 during development
4. **Migration:** Use `migrate_to_mysql.py` for automated switching
5. **Environment:** Use `.env` to manage different configurations

---

*For detailed information, see the comprehensive documentation files included in the project.*
