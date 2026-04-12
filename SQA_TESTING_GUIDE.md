# DrSeba Healthcare Platform - SQA Testing Guide

## 📱 How to Access the Project for Testing

### **Option 1: Using Ngrok (Recommended - Easiest)**

#### **Step 1: Install Ngrok**

1. Download from: https://ngrok.com/download
2. Extract the file to a folder
3. Add to PATH or run from extraction folder

#### **Step 2: Get Public URL**

```batch
# Terminal 1 - Start Django Server
python manage.py runserver 0.0.0.0:8000

# Terminal 2 - Start Ngrok
ngrok http 8000
```

**You'll see:**
```
Forwarding    https://abc123xyz-45-67-89.ngrok.io -> http://localhost:8000
```

Copy the HTTPS URL and share with SQA team!

---

### **Option 2: Python Alternative (No Install Needed)**

If Ngrok isn't available, use Python's built-in solution:

```powershell
# Install flask-cors
pip install pyngrok

# Then in Python terminal:
python -c "from pyngrok import ngrok; print(ngrok.connect(8000))"
```

---

### **Option 3: Local Network Sharing**

If SQA team is on the same office/home network:

```powershell
# Find your IP
ipconfig

# Look for IPv4 Address (e.g., 192.168.1.100)
# Share with SQA team:
http://192.168.1.100:8000  (or your actual IP)
```

---

## 🔐 Test Credentials

### **Admin Panel Access**
```
URL: https://your-public-url/admin/

Username: admin
Password: (the password you set during initial setup)
```

### **Test Patient Account**
```
Email: patient1@test.com
Password: Test@1234
```

### **Test Doctor Account**
```
Email: doctor1@test.com
Password: Test@1234
```

### **Additional Test Accounts**
Use any of these for testing:
- patient2@test.com through patient6@test.com
- doctor1@test.com through doctor5@test.com
- All use same pattern password

---

## ✅ SQA Testing Checklist

### **User Management**
- [ ] Patient Registration
- [ ] Doctor Registration
- [ ] User Login
- [ ] User Logout
- [ ] Profile Update
- [ ] Password Change

### **Doctor Management**
- [ ] View Doctor List
- [ ] Search Doctors by Name/Specialty
- [ ] Filter Doctors by Location/Specialty
- [ ] View Doctor Detail Page
- [ ] View Doctor Reviews
- [ ] Add Review (as Patient)

### **Appointment Booking**
- [ ] Browse Doctor Profile
- [ ] Click "Book Now"
- [ ] Select Date from Calendar
- [ ] Select Time Slot
- [ ] Choose Consultation Type (Online/In-Person)
- [ ] Enter Patient Information
- [ ] Review Appointment Summary
- [ ] Complete Booking

### **Dashboard Features**
- [ ] Patient Dashboard (View Appointments, Payments)
- [ ] Doctor Dashboard (View Schedule, Earnings)
- [ ] Admin Dashboard (Statistics, User Management)
- [ ] View Appointment History
- [ ] View Payment History

### **Payment Processing**
- [ ] Proceed to Cart
- [ ] View Cart Items
- [ ] Select Payment Method (Cash, Card, bKash, Nagad)
- [ ] Complete Payment
- [ ] View Invoice
- [ ] Download Invoice (if available)

### **Search & Filter**
- [ ] Search Doctor by Name
- [ ] Search Doctor by Specialty
- [ ] Filter by Location
- [ ] Filter by Price Range
- [ ] Filter by Rating
- [ ] Pagination Works

### **UI/UX Verification**
- [ ] Responsive Design (Mobile, Tablet, Desktop)
- [ ] All Icons Display Correctly
- [ ] Forms Properly Aligned
- [ ] Buttons Functional
- [ ] Navigation Works
- [ ] Search Bar Functional

### **Data Display**
- [ ] Doctor Info Displays Correctly
- [ ] Appointment Details Show Properly
- [ ] Payment Records Visible
- [ ] Ratings/Reviews Display
- [ ] Hospital Info Shows
- [ ] Availability Slots Display

### **Error Handling**
- [ ] Invalid Login Shows Error
- [ ] Required Fields Validation
- [ ] Session Timeout Handling
- [ ] 404 Page Display
- [ ] Error Messages Clear

---

## 📊 Sample Test Data Available

### **Doctors Available for Testing:** 8
- Cardiologist
- Gynecologist
- Dentist
- Neurologist
- And 4 more...

### **Hospitals Available:** 4
- Apollo Hospital
- Square Hospital
- National Hospital
- United Hospital

### **Specialties Available:** 8+

### **Demo Appointments:** 24
(Various statuses: Pending, Confirmed, Completed)

---

## 🐛 Bug Reporting Template

When reporting issues, use this format:

```
**Title:** [Brief description]
**URL:** [Where the issue occurred]
**Steps to Reproduce:**
1. ...
2. ...
**Expected Result:**
[What should happen]

**Actual Result:**
[What actually happened]

**Environment:**
- Browser: [Chrome/Firefox/Safari/Edge]
- Device: [Desktop/Mobile/Tablet]
- OS: [Windows/Mac/Linux]

**Screenshots:** [If applicable]
```

---

## 🚀 Important Notes for SQA

1. **Data Persistence:** All data is stored in SQLite database, changes persist across sessions
2. **User Sessions:** Inactive sessions timeout after 2 weeks (configurable)
3. **Payment:** Currently simulated - no real charges
4. **Email Notifications:** Not configured in test environment
5. **Admin Access:** Limited to admin users only

---

## 📞 Support During Testing

If issues arise:
1. Check application logs in terminal
2. Verify internet connection (for Ngrok URL)
3. Clear browser cache
4. Try incognito/private mode
5. Contact development team with bug report

---

## 🔧 Quick Troubleshooting

### **"Connection Refused"**
- Ensure Django server is running on Terminal 1
- Check if port 8000 is available: `netstat -ano | findstr :8000`

### **"Ngrok URL Not Working"**
- Session may have expired (free Ngrok lasts ~2 hours)
- Restart Ngrok to get new URL
- Share new URL with SQA team

### **"Page Not Loading"**
- Check if server is running
- Hard refresh page (Ctrl+F5)
- Clear cookies
- Try private/incognito mode

### **"Login Not Working"**
- Verify credentials are correct
- Check if user account exists in admin panel
- Try registering new test account

---

## 📝 Testing Timeline

- **Initial Setup:** 5 minutes
- **Smoke Testing:** 15 minutes
- **Full Feature Testing:** 2-3 hours
- **Bug Reporting:** Ongoing

---

## ✨ Key URLs for Testing

```
Home Page:              {your-url}/
Admin Panel:            {your-url}/admin/
Doctor Listing:         {your-url}/doctors/
Doctor Search:          {your-url}/doctors/search/
Appointment Booking:    {your-url}/appointments/book/{doctor-id}/
My Appointments:        {your-url}/appointments/my-appointments/
Patient Dashboard:      {your-url}/dashboard/patient/
Doctor Dashboard:       {your-url}/dashboard/doctor/
Admin Dashboard:        {your-url}/dashboard/admin/
Login:                  {your-url}/accounts/login/
Register:               {your-url}/accounts/register/patient/
```

---

**Last Updated:** April 12, 2026  
**Version:** 1.0  
**Status:** Ready for SQA Testing ✅
