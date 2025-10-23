# 🚀 HSE Risk Assessment - Dual Mitigation System Setup Guide

## ✅ What Was Implemented

You now have **TWO mitigation options** for HSE Risk Assessments:

1. **External Department Assignment** (LIMS/LW8 - Existing)
2. **Internal Mitigation User Assignment** (NEW)

---

## 📋 Step 1: Create Mitigation User Role

Run this command to create the Mitigation User role in Django:

```bash
python manage.py create_mitigation_user_role
```

**Expected Output:**

```
Created new Mitigation User role
  Added permission: view_evince
  Added permission: change_evince

✅ Mitigation User role setup complete!
   Permissions granted:
   - View HSE Risk Assessments assigned to them
   - Submit mitigation actions
   - Upload evidence
   - Mark mitigation work as completed
```

---

## 📋 Step 2: Create Mitigation Users

### ⭐ Option A: Through User Management (Recommended - Easiest!)

1. Login to your application as **Admin**
2. Go to **"Users"** page from sidebar
3. Click **"Create"** button
4. Fill in user details:
   - Username
   - Email
   - Password
   - Data Groups
   - **Role: Select "Mitigation User"** ← New option!
5. Click **"Create"**
6. ✅ Done! User is ready to use

> **Note:** "Mitigation User" now appears in the role dropdown when creating or editing users!

### Option B: Through Django Admin

1. Go to Django Admin: `http://localhost:8000/admin/`
2. Navigate to **Users**
3. Create a new user or edit existing user
4. Scroll to **Groups** section
5. Add user to **"Mitigation User"** group
6. Save

### Option C: Through Python Shell

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User, Group

# Get the Mitigation User group
mitigation_group = Group.objects.get(name='Mitigation User')

# Create a new mitigation user
user = User.objects.create_user(
    username='mitigation_user1',
    email='mitigation@example.com',
    password='your_password',
    first_name='John',
    last_name='Doe'
)

# Add to Mitigation User group
user.groups.add(mitigation_group)
user.save()

print(f"✅ Created user: {user.username}")
```

---

## 🔄 Workflow Overview

### **Current Flow (Both Options Supported)**

```
1. Admin Creates HSE Risk Assessment
   ↓
2. Inspector Assesses Risk
   ↓
3. Manager Validates Risk
   ↓
4. Manager Assigns Mitigation:

   ┌─────────────────────────────────────────┐
   │  CHOICE: External OR Internal           │
   ├─────────────────────────────────────────┤
   │  ○ External Department (LIMS)           │
   │     → Sends to LIMS DB                  │
   │     → Syncs updates back                │
   │                                          │
   │  ○ Internal User (Mitigation User)      │
   │     → Assigns to internal user          │
   │     → User logs in to see tasks         │
   └─────────────────────────────────────────┘

   ↓
5. Work Completed (External System OR Mitigation User)
   ↓
6. Manager Reviews & Approves
```

---

## 🎯 Manager Assignment Process

When a manager reviews an HSE Risk Assessment with out-of-spec results:

### **Frontend UI**

The manager sees:

```
⚠️ Out-of-Spec Results Found
This assessment has out-of-spec results that require mitigation.

○ External Department    ○ Internal User

[Dropdown changes based on selection]

Mitigation Plan: [________________]
Target Date: [____________________]

[Assign for Mitigation]
```

### **Backend API Calls**

#### **External Assignment (Existing)**

```
POST /api/hse_risk_assessment_results/{id}/assign-mitigation/
{
  "external_department_id": 1,
  "mitigation_plan": "Fix the issue...",
  "target_date": "2025-11-01"
}
```

#### **Internal Assignment (NEW)**

```
POST /api/hse_risk_assessments/{id}/assign-mitigation/
{
  "hse_mitigation_assigned_to": 5,  // User ID
  "hse_mitigation_actions": "Fix the issue...",
  "hse_mitigation_target_date": "2025-11-01"
}
```

---

## 👤 Mitigation User Experience

### **Login & Dashboard**

1. User logs in with mitigation user credentials
2. Sees **"HSE Risk Management"** in sidebar
3. Clicks **"My Mitigation Tasks"**
4. Dashboard shows:

```
┌────────────────────────────────────────────────────┐
│  My Mitigation Tasks                                │
├────────────────────────────────────────────────────┤
│  Total: 5  │  Pending: 3  │  Completed: 2         │
├────────────────────────────────────────────────────┤
│  Task ID  │  Risk Level  │  Category  │  Due Date  │
│  #123     │  HIGH        │  Safety    │  3 days    │
│  #124     │  MEDIUM      │  Health    │  5 days    │
└────────────────────────────────────────────────────┘
```

### **Submit Mitigation Work**

1. Click **"Submit Work"** button
2. Modal opens showing:
   - Risk details
   - Observation details
   - Input fields for:
     - Mitigation actions taken \*
     - Evidence/Notes (optional)
3. Click **"Submit Work"**
4. Status changes to **"MitigationCompleted"**
5. Manager receives notification for approval

---

## 🔗 API Endpoints Reference

### **For Managers:**

| Endpoint                                                   | Method | Description                   |
| ---------------------------------------------------------- | ------ | ----------------------------- |
| `/api/hse_risk_assessments/mitigation-users/`              | GET    | Get list of mitigation users  |
| `/api/hse_risk_assessments/{id}/assign-mitigation/`        | POST   | Assign to internal user       |
| `/api/hse_risk_assessment_results/{id}/assign-mitigation/` | POST   | Assign to external department |

### **For Mitigation Users:**

| Endpoint                                                 | Method | Description              |
| -------------------------------------------------------- | ------ | ------------------------ |
| `/api/hse_risk_assessments/my-mitigation-tasks/`         | GET    | Get assigned tasks       |
| `/api/hse_risk_assessments/mitigation-dashboard-stats/`  | GET    | Get dashboard statistics |
| `/api/hse_risk_assessments/{id}/submit-mitigation-work/` | POST   | Submit completed work    |

---

## 🧪 Testing Guide

### **Test 1: Create Mitigation User**

```bash
# Create role
python manage.py create_mitigation_user_role

# Create user
python manage.py createsuperuser --username mitigation_test

# Add to group
python manage.py shell
>>> from django.contrib.auth.models import User, Group
>>> user = User.objects.get(username='mitigation_test')
>>> group = Group.objects.get(name='Mitigation User')
>>> user.groups.add(group)
>>> user.save()
```

### **Test 2: Manager Assigns Internal Mitigation**

1. Login as Manager
2. Go to **"My Risk Assessments"**
3. Find an assessment with status **"ManagerAssignment"**
4. Click **"Actions"**
5. Select **"Internal User"** radio button
6. Select a mitigation user from dropdown
7. Enter mitigation plan and target date
8. Click **"Assign for Mitigation"**
9. ✅ Verify: Status should remain **"RiskValidated"** (or change to appropriate status)

### **Test 3: Mitigation User Completes Work**

1. Login as Mitigation User
2. Go to **"My Mitigation Tasks"**
3. See assigned tasks in dashboard
4. Click **"Submit Work"** on a task
5. Fill in mitigation actions and evidence
6. Click **"Submit Work"**
7. ✅ Verify: Status changes to **"MitigationCompleted"**

### **Test 4: Manager Approves Completed Work**

1. Login as Manager
2. Go to **"My Risk Assessments"**
3. Find task with status **"MitigationCompleted"**
4. Review mitigation actions and evidence
5. Approve or reject the work
6. ✅ Verify: Status changes to **"Approved"** or **"Rejected"**

### **Test 5: External Assignment Still Works**

1. Login as Manager
2. Assign to **"External Department"** instead
3. ✅ Verify: Assignment goes to LIMS
4. ✅ Verify: Sync updates work as before

---

## 🎨 Frontend Components

### **Files Modified/Created:**

#### **Backend:**

- ✅ `api/management/commands/create_mitigation_user_role.py` - Role creation command
- ✅ `api/viewsets/hse_risk_assessment.py` - Added mitigation user endpoints
- ✅ Updated filtering for Mitigation User role

#### **Frontend:**

- ✅ `hseRiskManagement/myRiskAssessments.jsx` - Added dual assignment UI
- ✅ `mitigationUser/myMitigationTasks.jsx` - New dashboard for mitigation users
- ✅ `main.jsx` - Added route for mitigation dashboard
- ✅ `sidemenu.jsx` - Added sidebar menu for Mitigation User
- ✅ `en/translation.json` - Added English translations
- ✅ `ar/translation.json` - Added Arabic translations

---

## 📊 Database Fields Used

### **For Internal Mitigation:**

- `hse_mitigation_assigned_to` (ForeignKey to User)
- `hse_mitigation_actions` (TextField)
- `hse_mitigation_evidence` (TextField)
- `hse_mitigation_target_date` (DateTimeField)
- `hse_mitigation_completed` (BooleanField)
- `hse_mitigation_department` (ForeignKey to BusinessUnit)

### **For External Mitigation:**

- `ExternalDepartmentAssignment` model
- `external_task_id`
- `external_status`
- `last_sync_at`

---

## ⚠️ Important Notes

1. **Both systems run independently** - No interference between external and internal
2. **Manager chooses** which system to use per assessment
3. **No database changes needed** - Uses existing fields
4. **Backwards compatible** - External system works as before
5. **Role-based access** - Mitigation users only see their tasks

---

## 🐛 Troubleshooting

### **Issue: Mitigation User role not found**

```bash
python manage.py create_mitigation_user_role
```

### **Issue: User can't see mitigation tasks**

Check:

1. User is in "Mitigation User" group
2. Tasks are assigned to that specific user
3. User has logged in with correct credentials

### **Issue: Manager can't see internal users**

Check:

1. Mitigation User role exists
2. Users are added to the group
3. Frontend is fetching from correct endpoint

---

## ✅ Success Checklist

- [ ] Mitigation User role created
- [ ] At least one mitigation user created
- [ ] Manager can see both assignment options
- [ ] Manager can assign to internal user
- [ ] Mitigation user can see assigned tasks
- [ ] Mitigation user can submit work
- [ ] Manager can approve/reject completed work
- [ ] External assignment still works

---

## 🎉 You're All Set!

Your HSE Risk Assessment system now supports both external (LIMS) and internal (Mitigation User) mitigation workflows!

**Questions? Issues?** Check the code comments or reach out for support.
