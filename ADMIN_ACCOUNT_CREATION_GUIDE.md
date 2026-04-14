# Admin Account Creation Guide

## Overview
This guide explains how admins can create accounts for employees and doctors with custom passwords that they can use to log in.

## Features Added

### 1. **Employee Account Creation**
Admins can now create employee accounts with:
- First Name
- Last Name  
- Email (used as login)
- Phone Number
- Custom Password (set by admin)

### 2. **Doctor Account Creation**
Admins can now create doctor accounts with:
- First Name
- Last Name
- Email (used as login)
- Phone Number
- Custom Password (set by admin)

## How to Use

### Creating a New Employee Account

1. **Go to Django Admin Dashboard**
   - Navigate to: `http://127.0.0.1:8000/admin/`
   - Log in with your admin credentials

2. **Create Employee Account**
   - Click on "Users" in the left sidebar
   - Look for "Create New Employee Account" link/button
   - OR navigate directly to: `http://127.0.0.1:8000/admin/accounts/user/create-employee/`

3. **Fill in the Form**
   - **First Name**: Employee's first name
   - **Last Name**: Employee's last name
   - **Email**: Unique email address (this will be their login username)
   - **Phone**: Contact phone number
   - **Password**: Set a temporary or permanent password
   - **Confirm Password**: Re-enter the same password

4. **Submit**
   - Click "Create Employee Account"
   - Success message will show the email

### Creating a New Doctor Account

1. **Go to Django Admin Dashboard**
   - Navigate to: `http://127.0.0.1:8000/admin/`

2. **Create Doctor Account**
   - Click on "Users" in the left sidebar
   - Look for "Create New Doctor Account" link/button
   - OR navigate directly to: `http://127.0.0.1:8000/admin/accounts/user/create-doctor/`

3. **Fill in the Form**
   - **First Name**: Doctor's first name
   - **Last Name**: Doctor's last name
   - **Email**: Unique email address (this will be their login username)
   - **Phone**: Contact phone number
   - **Password**: Set a temporary or permanent password
   - **Confirm Password**: Re-enter the same password

4. **Submit**
   - Click "Create Doctor Account"
   - Success message will show the email

## Login Process

### For Created Employees/Doctors:
1. Navigate to login page: `http://127.0.0.1:8000/accounts/login/`
2. Enter **Email** as username (or the email prefix if it matches)
3. Enter **Password** as set by admin
4. Click "Sign In"

## Password Requirements
- **Minimum Length**: 4 characters
- **Characters**: Any characters are allowed
- **Both Passwords Must Match**: The password and confirm password fields must be identical

## Important Notes

1. **Unique Email**: Each email must be unique in the system
2. **Email as Username**: The email becomes the user's login identifier
3. **Password Security**: Make sure to:
   - Use strong passwords
   - Don't share passwords in plain text
   - Share passwords securely with employees/doctors
   - Encourage them to change their password on first login

4. **Account Activation**:
   - Employees are activated by default (`is_active = True`)
   - Doctors may need verification before full access
   - Both receive roles automatically (employee/doctor)

## URL Routes

### Create Employee:
```
Admin URL: /admin/accounts/user/create-employee/
Django Admin: Users > Create New Employee Account
```

### Create Doctor:
```
Admin URL: /admin/accounts/user/create-doctor/
Django Admin: Users > Create New Doctor Account
```

## Form Fields Reference

### Email Validation
- Must be a valid email format (e.g., john@example.com)
- Must be unique (no duplicates)

### Phone Validation
- Optional field
- Format: Any format (e.g., +8801711111111 or 01711111111)
- Will be displayed as provided

### Password Validation
- Minimum 4 characters
- Passwords must match between "Password" and "Confirm Password"
- No special requirements, any characters allowed

## Troubleshooting

### Error: "This email is already registered"
- **Solution**: Use a different email address that hasn't been registered before

### Error: "Passwords do not match"
- **Solution**: Make sure both password fields have exactly the same text

### Error: "Password must be at least 4 characters long"
- **Solution**: Use a password with at least 4 characters

### Account Not Appearing
- Go back to the admin panel
- Navigate to the Employees or Doctors section to verify account was created

## Next Steps

After creating an account:
1. Share the email and password with the employee/doctor securely
2. They can log in at: `/accounts/login/`
3. They can update their profile after first login
4. Employees can access their dashboard at: `/dashboard/`
5. Doctors can access their dashboard at: `/dashboard/doctor/`
