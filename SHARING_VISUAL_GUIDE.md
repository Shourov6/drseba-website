# 📤 Share DrSeba Platform - Step-by-Step Visual Guide

## 🎯 Goal: Generate Public URL for SQA Team

### **Method 1: Using Automation Script (EASIEST) ⭐**

**Step-by-Step:**

```
TERMINAL 1 (Keep Open)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ python manage.py runserver 0.0.0.0:8000

Django version 4.2.30
Starting development server at http://0.0.0.0:8000/
✅ Server Running
```

```
TERMINAL 2 (New - Run This)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ python share_with_sqa.py

🌐 DrSeba Platform - Share with SQA Team
═══════════════════════════════════════

📌 Choose Share Method:
1️⃣  Public URL via Ngrok (Recommended)
2️⃣  Local Network IP 
3️⃣  Show Testing Guide
4️⃣  Exit

Enter choice (1-4): 1

✅ Checking Ngrok...
⏳ Installing pyngrok...

✅ Public URL Created Successfully!

🔗 SHARE THIS WITH SQA TEAM:

   https://abc123xyz-45-67-89.ngrok.io

📋 Admin Panel:

   https://abc123xyz-45-67-89.ngrok.io/admin/

👤 Test Credentials:
   Admin User: admin
   Patient: patient1@test.com
   Doctor: doctor1@test.com

⏱️  Keep this terminal OPEN for SQA access
💾 Press Ctrl+C to stop sharing
```

### **Result:** 🎉 SQA team can access from anywhere!

---

## 🎯 What to Share

### **Copy & Paste to SQA Team:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏥 DrSeba Healthcare Platform - Testing Access

🔗 MAIN URL:
https://abc123xyz-45-67-89.ngrok.io

📊 ADMIN PANEL:
https://abc123xyz-45-67-89.ngrok.io/admin/

👤 TEST ACCOUNTS:

Patient Account:
  Email: patient1@test.com
  Password: Test@1234

Doctor Account:
  Email: doctor1@test.com
  Password: Test@1234

Admin Account:
  Username: admin
  Password: (provided separately)

📋 TESTING CHECKLIST:
See attached: SQA_TESTING_GUIDE.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📱 Test Features Available

### ✅ For Patient Testing
```
✓ Register as patient
✓ Search for doctors
✓ View doctor profiles
✓ Book appointments
✓ Pay for appointments
✓ View appointment history
✓ Add reviews
✓ View dashboard
```

### ✅ For Doctor Testing
```
✓ Register as doctor
✓ View schedule
✓ Check availability
✓ View appointments
✓ Check earnings
✓ View dashboard
✓ Update profile
```

### ✅ For Admin Testing
```
✓ Access admin panel
✓ Manage users
✓ Manage doctors
✓ Manage appointments
✓ View statistics
✓ View payments
✓ Edit database
```

---

## 🔄 URL Lifespan

| Feature | Duration | Solution |
|---------|----------|----------|
| **Ngrok Free** | ~2 hours | Restart script, share new URL |
| **Ngrok Paid** | Unlimited | Upgrade account (~$5/month) |
| **Local IP** | Until PC restarts | Good for same-network testing |
| **Cloud Deploy** | Unlimited | Heroku/PythonAnywhere/AWS |

---

## 📊 Sample Test Scenarios

### **Scenario 1: Patient Books Appointment**
```
1. Click: Home → Doctor Search
2. Search for "Cardiologist"
3. Click: View Profile
4. Click: Book Now
5. Select: Date & Time
6. Enter: Patient Details
7. Confirm: Appointment
8. Pay: Select payment method
9. Success: Get confirmation
```

### **Scenario 2: Doctor Checks Schedule**
```
1. Login as: doctor1@test.com
2. Click: Doctor Dashboard
3. View: All appointments
4. Check: Time slots
5. See: Patient details
6. Verify: Earnings
```

### **Scenario 3: Admin Manages System**
```
1. Go to: https://url/admin/
2. Login with: admin credentials
3. Manage: Users, Doctors, Appointments
4. View: Database records
5. Add: New test data if needed
```

---

## 🐛 Quick Troubleshooting

### **URL Not Working?**
```
❌ "Connection Refused"
✅ Solution: Ensure Django server still running in Terminal 1

❌ "URL Expired" 
✅ Solution: Restart share_with_sqa.py for new URL

❌ "Slow Loading"
✅ Solution: Normal, wait 5-10 seconds for response

❌ "Login Fails"
✅ Solution: Double-check credentials, try test account
```

---

## 📞 Communication with SQA

### **Email Template:**

```
Subject: DrSeba Platform - Ready for Testing

Hi SQA Team,

The DrSeba Healthcare Platform is now available for testing!

🔗 Access URL: https://abc123xyz-45-67-89.ngrok.io

📋 Complete testing guide: SQA_TESTING_GUIDE.md (attached)

👤 Test Credentials:
   - Patient: patient1@test.com / Test@1234
   - Doctor: doctor1@test.com / Test@1234
   - Admin: admin / (ask me for password)

✅ Platform Status:
   - All features working
   - 8 test doctors available
   - 24 demo appointments for reference
   - Full payment simulation
   - Complete dashboard for all roles

⏱️ Available Until: [date/time]

Please report any issues using the format in Section 3 of SQA_TESTING_GUIDE.md

Looking forward to your feedback!

Thanks,
[Your Name]
```

---

## 📚 Files to Share with SQA

1. **SQA_TESTING_GUIDE.md** - Complete testing checklist
2. **COMPLETE_AUDIT_REPORT.md** - System status & features
3. **TESTING_AND_FIXES_SUMMARY.md** - What's been tested

---

## 🔒 Security During Testing

✅ **DO:**
- Use test/demo accounts only
- Report bugs found
- Test all features
- Clear browser cache if needed

❌ **DON'T:**
- Share URLs on public channels
- Use real credit card info
- Try SQL injection attacks
- Share admin password in chat

---

## ✨ After SQA Testing

### **When Testing Completes:**
```
1. Stop share_with_sqa.py (Press Ctrl+C)
2. Public URL becomes inactive
3. Reset admin password
4. Archive test results
5. Prepare bug report summary
```

---

## 🚀 For Long-Term Testing

If testing needs >2 hours, consider:

### **Option A: Upgrade Ngrok** (~$5/month)
```
Get permanent public URL
https://console.ngrok.com
```

### **Option B: Deploy to Cloud** (Free tier available)
```
PythonAnywhere: 5 min setup, free tier
Heroku: 10 min setup, free credits available
```

### **Option C: Local Network Only** (For same office)
```
Share IP: http://192.168.x.x:8000
Much faster & no internet dependency
```

---

## ✅ Complete Checklist

Before sharing link:

- [ ] Terminal 1: Django server running
- [ ] Terminal 2: share_with_sqa.py running
- [ ] Public URL generated (ngrok)
- [ ] Homepage loads correctly
- [ ] Admin panel accessible
- [ ] Test accounts verified
- [ ] Demo data loaded
- [ ] No console errors
- [ ] Testing guides prepared
- [ ] SQA team notified

---

**You're Ready to Share!** 🎉

Go to Terminal 2 and execute:
```
python share_with_sqa.py
```

Then share the generated URL with your SQA team!
