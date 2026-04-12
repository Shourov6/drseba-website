# DATABASE SETUP GUIDE - Django Admin Panel Method

## ⚠️ IMPORTANT: Database SQLite is NOT in GitHub

The `db.sqlite3` database file is **NOT** included in the GitHub repository. This is intentional for the following reasons:

1. **Database is a Binary File** - SQLite stores data in a binary format that can't be merged
2. **Different States** - Each developer/user has their own data state
3. **Production Safety** - Production databases should never be in version control
4. **Fresh Installation** - Each new setup gets a fresh, clean database

---

## 🔧 SETUP INSTRUCTIONS FOR NEW INSTALLATIONS

### Step 1: Clone the Repository
```bash
git clone https://github.com/Shourov-666/drseba-website.git
cd drseba-website
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create Fresh Database
```bash
# This creates a NEW blank db.sqlite3
python manage.py migrate
```

### Step 5: Create Superuser Admin Account
```bash
python manage.py createsuperuser
```

**When prompted, enter:**
- Username: `admin` (or your choice)
- Email: `admin@drseba.com`
- Password: (create strong password)

**💾 Save these credentials!**

### Step 6: Start Development Server
```bash
python manage.py runserver
```

---

## 📊 ADDING DATA VIA DJANGO ADMIN PANEL

### Access Admin Panel
1. Open browser: **http://127.0.0.1:8000/admin/**
2. Login with superuser credentials created in Step 5

### Add Specialties (Required First)
1. Click **Specialties** (under Doctors app)
2. Click **+ Add Specialty**
3. Add each specialty:

| Name | Icon | Description | Color |
|------|------|-------------|-------|
| Cardiology | ❤️ | Heart and cardiovascular specialists | #FF6B6B |
| Dermatology | 🩹 | Skin specialists | #4ECDC4 |
| Neurology | 🧠 | Neurological specialists | #45B7D1 |
| Pediatrics | 👶 | Child healthcare specialists | #96CEB4 |
| Orthopedics | 🦴 | Bone and joint specialists | #FFEAA7 |
| (Add more as needed) | | | |

### Add Hospitals
1. Click **Hospitals**
2. Click **+ Add Hospital**
3. Enter hospital details (name, address, phone, beds, etc.)

### Add Doctors
1. Click **Doctors**
2. Click **+ Add Doctor**
3. Fill in:
   - User (create new user or select existing)
   - BMDC Number (e.g., BMDC00001)
   - Specialties (select from added specialties)
   - Consultation Fees (online & in-person)
   - Qualifications
   - Hospital Links

### Add Users (Doctors & Patients)
1. Click **Users** (under Accounts app)
2. Click **+ Add User**
3. Set:
   - Username
   - Email
   - Password
   - First Name / Last Name
   - Phone
   - Role (doctor, patient, admin, employee)

---

## 📋 ADMIN PANEL CHECKLIST

After fresh installation, superuser should:

- [ ] Create at least 5-10 Specialties
- [ ] Create at least 2-3 Hospitals
- [ ] Create at least 3-5 Doctors with specialties
- [ ] Create at least 5 Patient accounts
- [ ] Create Employee account (for employee dashboard)

---

## 🚀 QUICK START FOR TESTING

If you want demo data without manual entry, use the enhanced setup script:

```bash
python setup_enhanced_demo_data.py
```

This creates:
- ✓ 1 Admin user (admin/admin123)
- ✓ 37 Doctors across 18 specialties
- ✓ 10 Patient accounts
- ✓ 46 Appointments
- ✓ 25 Payments

Then access demo accounts:
- **Doctor**: kamal.ahmed@drseba.com / doctor123
- **Patient**: ahmed.ali@example.com / patient123
- **Admin**: admin / admin123

---

## ⚙️ DATABASE FILE EXPLAINED

### What Gets Created
When you run `python manage.py migrate`, a new `db.sqlite3` file is created containing:
- **Empty database schema** (tables structure only)
- **No data** (blank tables)

### Why It's Local Only
- `.gitignore` prevents `db.sqlite3` from being uploaded to GitHub
- Each developer/user has their own local copy
- No two databases interfere with each other
- Safe to delete and recreate anytime

### If You Delete db.sqlite3
```bash
# Simply recreate it:
python manage.py migrate
python manage.py createsuperuser
```

---

## 🔄 WORKFLOW FOR TEAM DEVELOPMENT

1. **Developer A**: Clones repo → Creates local db → Adds data in admin panel
2. **Developer B**: Clones repo → Creates local db → Adds their own data
3. **Each developer has their own independent database**
4. **No conflicts, no corruption, no merge issues!**

---

## 💡 KEY POINTS TO REMEMBER

✅ **DO:**
- Add data via Django Admin Panel
- Keep `.gitignore` excluding `db.sqlite3`
- Commit code changes, not database files
- Share SQL scripts for data schemas

❌ **DON'T:**
- Commit `db.sqlite3` to GitHub
- Share local database files
- Merge database files
- Use production database for development

---

## 📞 TROUBLESHOOTING

### "Table doesn't exist" error
```bash
# Rerun migrations
python manage.py migrate
```

### Can't login to admin
```bash
# Recreate superuser
python manage.py createsuperuser
```

### Want fresh database
```bash
# Delete database and recreate
rm db.sqlite3  # or del db.sqlite3 on Windows
python manage.py migrate
python manage.py createsuperuser
```

---

**Now you have a clean, maintainable database setup that works perfectly for team collaboration!** 🎉
