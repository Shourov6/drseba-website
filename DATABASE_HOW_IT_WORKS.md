# HOW DRSEBA DATABASE WORKS

## 🎯 CURRENT ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB REPOSITORY                             │
│  (Contains: Code, Migrations, Templates, NOT Database Files)    │
│                                                                   │
│  ├── accounts/                                                   │
│  ├── doctors/                                                    │
│  ├── appointments/                                               │
│  ├── payments/                                                   │
│  ├── dashboards/                                                 │
│  ├── templates/                                                  │
│  ├── drseba/settings.py  ← Database configuration               │
│  ├── manage.py                                                   │
│  ├── requirements.txt                                            │
│  ├── .gitignore  ← Excludes db.sqlite3                          │
│  └── DATABASE_SETUP_GUIDE.md  ← This file                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                        Clone Locally
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              DEVELOPER'S LOCAL MACHINE                           │
│                                                                   │
│  /drseba-website-clone/                                          │
│  ├── [All files from GitHub]                                    │
│  └── db.sqlite3  ← Created locally during setup                 │
│      (NOT from GitHub - Generated fresh)                        │
│                                                                   │
│      Data Flow:                                                  │
│      ┌──────────────────────────────────────┐                   │
│      │  Django Migrations (Schema Setup)    │                   │
│      └─────────────────────┬────────────────┘                   │
│                            ↓                                     │
│      ┌──────────────────────────────────────┐                   │
│      │  Fresh Empty Database Created        │                   │
│      │  (db.sqlite3 - 0KB, empty tables)    │                   │
│      └─────────────────────┬────────────────┘                   │
│                            ↓                                     │
│      ┌──────────────────────────────────────┐                   │
│      │  Superuser Manually Adds Data Via:   │                   │
│      │  - Django Admin Panel (/admin/)      │                   │
│      │  - OR Demo Setup Script              │                   │
│      └─────────────────────┬────────────────┘                   │
│                            ↓                                     │
│      ┌──────────────────────────────────────┐                   │
│      │  Database Populated with Data        │                   │
│      │  (Only on this machine, stays local) │                   │
│      └──────────────────────────────────────┘                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 DATA FLOW EXPLANATION

### WHAT IS STORED IN GITHUB
✅ **Code & Configuration:**
- Python files (.py)
- HTML templates
- CSS styling
- Django settings
- Migration files (database schema definitions)

❌ **NOT Stored in GitHub:**
- `db.sqlite3` (database file with actual data)
- `.env` (local environment variables)
- `media/` folder (uploaded files)
- `static/` folder (compiled static files)

### WHAT IS STORED LOCALLY (On Each Developer's Machine)
- `db.sqlite3` - The actual database file
- `.env` - Local environment configuration
- `media/` - Uploaded files
- `venv/` - Virtual environment

### WHY THIS DESIGN?
```
Problem with Committing db.sqlite3 to GitHub:

❌ Developer A makes changes:
   ├── Adds 5 doctors
   ├── Creates 10 appointments
   └── Commits changes including db.sqlite3

❌ Developer B makes changes:
   ├── Adds different doctors
   ├── Creates different appointments
   └── Tries to merge → CONFLICT! → DATABASE CORRUPTION

✅ Better Approach - Database Schema Files:
   ├── Migrations (schema definitions) → In GitHub
   ├── Each developer gets fresh empty database → Generated locally
   ├── Each developer adds their own test data → Stays local
   └── NO CONFLICTS! ✓
```

---

## 🗂️ FILE STORAGE LOCATIONS

```
Django Project Structure:

drseba-website/
│
├── accounts/           → User authentication code
│   ├── migrations/     → Database schema changes (IN GITHUB)
│   ├── models.py       → Database table definitions (IN GITHUB)
│   └── views.py        → Business logic (IN GITHUB)
│
├── doctors/            → Doctor management code
│   ├── migrations/     → Database schema (IN GITHUB)
│   ├── models.py       → Defines Specialty, Doctor tables (IN GITHUB)
│   └── views.py        → Doctor views (IN GITHUB)
│
├── appointments/       → Appointment system
├── payments/           → Payment processing
│
├── db.sqlite3          → ❌ NOT IN GITHUB (Created locally)
├── .gitignore          → ✓ Tells Git to ignore db.sqlite3
├── manage.py           → Django command tool (IN GITHUB)
├── requirements.txt    → Python dependencies (IN GITHUB)
│
└── migrations/         → Schema change history (IN GITHUB)
```

---

## 📈 DJANGO DATABASE WORKFLOW

### 1️⃣ CODE (Django Models) → Migrations → Schema
```
Step 1: Developer writes model
─────────────────────────────
class Specialty(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50)

↓

Step 2: Create migration
─────────────────────────────
python manage.py makemigrations

Creates: accounts/migrations/0001_initial.py
(This file is IN GITHUB - versioned)

↓

Step 3: Apply migration (creates tables)
─────────────────────────────
python manage.py migrate

Creates: db.sqlite3 with Specialty table
(This file is NOT in GitHub - local only)

↓

Step 4: Add data (via Admin)
─────────────────────────────
Superuser adds data through Django Admin
Data goes into: db.sqlite3 (local only)
```

### 2️⃣ New Developer Cloning
```
Step 1: Clone from GitHub
─────────────────────────────
git clone https://github.com/Shourov-666/drseba-website.git

↓ (Gets all code + migrations, but NO db.sqlite3)

Step 2: Create fresh database
─────────────────────────────
python manage.py migrate

↓ (Uses migrations to recreate schema)

Step 3: Creates brand new empty database
─────────────────────────────
db.sqlite3 created (empty tables)

↓

Step 4: Superuser adds data they want
─────────────────────────────
Via Admin panel or setup script
```

---

## 💾 WHAT EACH FILE STORES

| File | Location | In GitHub? | Purpose |
|------|----------|-----------|---------|
| `db.sqlite3` | Root folder | ❌ NO | Binary database with all data |
| `migrations/` | Each app folder | ✅ YES | Database schema definitions |
| `models.py` | Each app folder | ✅ YES | Table structures (code) |
| `views.py` | Each app folder | ✅ YES | Business logic |
| `requirements.txt` | Root | ✅ YES | Python package list |
| `.gitignore` | Root | ✅ YES | File exclusion rules |
| `.env` | Root | ❌ NO | Secret configuration |
| `media/` | Root | ❌ NO | User uploaded files |

---

## 🔄 HOW DATA GETS STORED

### Specialties Example:
```
1. Code (IN GITHUB):
   └── doctors/models.py
       class Specialty(models.Model):
           name = models.CharField(max_length=100)
           icon = models.CharField(max_length=50)

2. Schema (IN GITHUB):
   └── doctors/migrations/0001_initial.py
       CreateModel('Specialty',
           fields=[
               ('name', CharField(max_length=100)),
               ('icon', CharField(max_length=50)),
           ]
       )

3. Data (NOT IN GITHUB, stored locally in db.sqlite3):
   ┌─────────────┬──────────────────┐
   │    name     │       icon       │
   ├─────────────┼──────────────────┤
   │ Cardiology  │        ❤️         │
   │ Dermatology │        🩹         │
   │ Neurology   │        🧠         │
   └─────────────┴──────────────────┘
   
   This table data is:
   - Modified via Django Admin Panel
   - Stored LOCALLY in db.sqlite3
   - NOT sent to GitHub
   - Each developer has their own version
```

---

## ✅ CURRENT SETUP STATUS

### Database Configuration (settings.py)
```python
# ✓ Using SQLite3 (local development friendly)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# When deployed to production:
# Can switch to MySQL via environment variable
# DB_ENGINE=django.db.backends.mysql
```

### Git Ignore Rules (.gitignore)
```
db.sqlite3               ← ✓ Excluded
db.sqlite3-journal      ← ✓ Excluded
*.log                   ← ✓ Excluded
*.pyc                   ← ✓ Excluded
__pycache__/            ← ✓ Excluded
.env                    ← ✓ Excluded
media/                  ← ✓ Excluded
```

---

## 🚀 RECOMMENDED WORKFLOW

### For New Team Members:
```bash
# 1. Clone repository (gets code + migrations)
git clone https://github.com/Shourov-666/drseba-website.git

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create fresh database with schema
python manage.py migrate

# 5. Create superuser account
python manage.py createsuperuser

# 6. Start server
python manage.py runserver

# 7. Open admin panel
# Go to: http://127.0.0.1:8000/admin/
# Login with superuser credentials
# Add specialties, hospitals, doctors, etc.
```

### For Demo/Testing:
```bash
# Instead of manual entry in Step 7, run:
python setup_enhanced_demo_data.py

# This creates 37 doctors, 10 patients, and test data
# Login with:
# - Doctor: kamal.ahmed@drseba.com / doctor123
# - Patient: ahmed.ali@example.com / patient123
# - Admin: admin / admin123
```

---

## 🎓 KEY LEARNING POINTS

1. **Migrations are Code** - They define table structure and are versioned
2. **Data is Local** - Each environment (dev, test, prod) has its own database
3. **Schema is Shared** - All developers use same migrations
4. **Database is Not Shared** - Each developer maintains their own data
5. **No Merge Conflicts** - Database conflicts are impossible with this setup
6. **Safe to Delete** - Can always recreate db.sqlite3 from migrations

---

**Summary**: The database schema (structure) lives in GitHub via migrations, but the actual data stays on each developer's machine in db.sqlite3!
