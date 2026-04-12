# 🚀 Share DrSeba with SQA Team - Quick Start

## ⚡ Fastest Method (2 steps, 30 seconds)

### **Step 1: Start Django Server**
```powershell
python manage.py runserver 0.0.0.0:8000
```
Keep this terminal open ✅

### **Step 2: Run Share Script**
In a NEW terminal:
```powershell
python share_with_sqa.py
```

Select option `1` (Public URL via Ngrok)

✅ Done! You'll get a public link like: `https://abc123-xyz456.ngrok.io`

---

## 📋 What to Share with SQA Team

```
🔗 PLATFORM URL:
https://your-generated-ngrok-url

📊 ADMIN PANEL:
https://your-generated-ngrok-url/admin/
- Username: admin
- Password: (your setup password)

✅ TEST ACCOUNTS:
Patient: patient1@test.com / Test@1234
Doctor: doctor1@test.com / Test@1234
Admin: admin / (your password)

📚 TESTING GUIDE:
See included SQA_TESTING_GUIDE.md for:
- Complete test checklist
- Sample data available
- Bug reporting format
- Troubleshooting guide
```

---

## 🎯 For Different Scenarios

### **Scenario A: SQA Team NOT on Your Network**
✅ Use **Ngrok** (Option 1)
- Works from anywhere
- Easiest for remote teams
- Free tier available

### **Scenario B: SQA Team ON Your Network** 
✅ Use **Local IP** (Option 2)
- Faster response times
- No 3rd party dependency
- Share: `http://your-ip:8000`

### **Scenario C: Deploy Permanently**
✅ Use **Cloud Services**:
- **PythonAnywhere** (5 min setup)
- **Heroku** (10 min setup)  
- **AWS/Azure** (More control)

See `DEPLOYMENT_OPTIONS.md` for details

---

## 🔐 Important Security Notes

⚠️ **While Sharing:**
- Don't commit sensitive passwords to git
- Check your `.env` file is NOT shared
- Use strong admin password
- Monitor who accesses the URL
- Consider IP whitelisting

✅ **After Testing:**
- Close Ngrok tunnel (Ctrl+C)
- Reset demo data
- Change admin password
- Delete sensitive URLs from chat history

---

## 📱 Test on Different Devices

### ✅ Desktop
```
Chrome/Firefox/Safari/Edge on Windows/Mac/Linux
Same URL works on all!
```

### ✅ Mobile
```
Use the same public URL on:
- Android phone/tablet
- iPhone/iPad
- Any mobile browser
```

### ✅ Responsive Testing
```
DevTools (F12) → Device Toolbar
Test at different breakpoints
```

---

## ⏱️ URL Duration

- **Ngrok Free Tier:** ~2 hours active session
- **Refresh:** Restart script to get new URL
- **Persistent:** Upgrade Ngrok plan or use cloud deployment

---

## 🆘 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "Connection Refused" | Ensure Django server running (Terminal 1) |
| "Ngrok won't install" | Install pyngrok: `pip install pyngrok` |
| "URL stopped working" | Session expired, restart script |
| "Can't login" | Verify credentials, check demo data loaded |
| "Slow loading" | Check internet, may need to wait 5-10sec |

---

## 📞 Communicate with SQA

**Message Template:**

```
Hi SQA Team! 👋

The DrSeba Healthcare Platform is ready for testing:

🔗 Access URL: https://[your-url]

📋 Testing Guide: See attached SQA_TESTING_GUIDE.md

👤 Test Accounts:
- Admin: admin / password
- Patient: patient1@test.com
- Doctor: doctor1@test.com

⏱️ Available: Until [date/time]

Please report any issues in the bug report format from the guide.

Thanks!
```

---

## 🎓 SQA Team Handbook

Share this with SQA team:
1. **SQA_TESTING_GUIDE.md** - Complete testing checklist
2. **This document** - Quick setup guide
3. **COMPLETE_AUDIT_REPORT.md** - Known features & status

---

## ✅ Pre-Testing Checklist

Before sending link to SQA:

- [ ] Django server is running
- [ ] `python share_with_sqa.py` is running  
- [ ] Public URL is generated
- [ ] Test credentials work
- [ ] All demo data is loaded
- [ ] No console errors
- [ ] Homepage loads correctly
- [ ] Admin panel accessible

---

**Ready to Share!** 🚀

Any questions? Check SQA_TESTING_GUIDE.md for detailed instructions.
