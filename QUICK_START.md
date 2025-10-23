# 🚀 Quick Start - HSE Mitigation User Setup

## ✅ 3-Step Setup (Under 5 Minutes!)

### **Step 1: Create the Role** (30 seconds)

Open terminal in backend folder:

```bash
cd IMS_BACKEND
python manage.py create_mitigation_user_role
```

**Expected Output:**

```
✅ Mitigation User role setup complete!
```

---

### **Step 2: Create a Mitigation User** (2 minutes)

#### **Easy Way - Through UI (Recommended):**

1. Login to your app as **Admin**
2. Click **"Users"** in sidebar
3. Click **"Create"** button
4. Fill in the form:
   ```
   Username: mitigation_user1
   Email: mitigation@company.com
   Password: YourSecurePassword123
   Data Groups: Select appropriate groups
   Role: Mitigation User  ← Select this!
   ```
5. Click **"Create"**
6. ✅ Done!

---

### **Step 3: Test It!** (2 minutes)

#### **A. Manager Assigns Work:**

1. Login as **Manager**
2. Go to **"My Risk Assessments"**
3. Find assessment with status **"RiskValidated"**
4. Click on the risk assessment row to open the modal
5. Go to **"Department Assignment"** tab
6. Choose assignment type:
   - **External System (LIMS)** - Sends to external system (existing flow)
   - **Internal User** - Assigns to internal mitigation user (new flow)
7. **Select Department** (same departments for both types)
8. **For Internal**: Select mitigation user from that department
9. **For External**: Enter contact person (optional)
10. Enter target date and instructions
11. Click **"Submit to External System"** or **"Assign to Internal User"**

> **Note:** Both external and internal assignments use the same departments and interface!

#### **B. Mitigation User Sees Task:**

1. **Logout** and login as **mitigation_user1**
2. Go to **"HSE Risk Management"** → **"My Mitigation Tasks"**
3. See the assigned task!
4. Click **"Submit Work"**
5. Fill in mitigation actions and evidence
6. Click **"Submit Work"**

#### **C. Manager Approves:**

1. **Logout** and login as **Manager**
2. Go to **"My Risk Assessments"**
3. Find task with status **"MitigationCompleted"**
4. Review and approve!

---

## 🎉 That's It!

Your system now supports **both**:

- ✅ External Department (LIMS) - Works as before
- ✅ Internal Mitigation User - New feature!

---

## 📸 Screenshots Guide

### **Creating Mitigation User:**

```
Users Page → Create Button:
┌────────────────────────────────────┐
│  Username: mitigation_user1        │
│  Email: mit@company.com            │
│  Password: ••••••••                │
│  Data Groups: [Select]             │
│  Role: [Mitigation User ▼]         │ ← New option!
│                                     │
│  [Create] [Cancel]                 │
└────────────────────────────────────┘
```

### **Manager Assignment:**

```
Department Assignment Tab:
┌────────────────────────────────────────────────────┐
│  🏢 Department Assignment                          │
│  Assign this risk assessment to a department...    │
│                                                    │
│  Assignment Type:                                  │
│  ○ External System (LIMS)                          │
│  ● Internal User                                   │ ← Select this
│                                                    │
│  Select Department: [Environmental Services ▼]    │
│  Select Mitigation User: [mitigation_user1 ▼]     │
│  Target Date: [2025-11-01]                         │
│  Instructions: [Fix the issues...]                 │
│                                                    │
│  [Assign to Internal User]                         │
└────────────────────────────────────────────────────┘
```

### **Mitigation User Dashboard:**

```
My Mitigation Tasks:
┌────────────────────────────────────────────┐
│  Total: 5  │  Pending: 3  │  Completed: 2 │
├────────────────────────────────────────────┤
│  #123  HIGH     Safety    3 days  [Submit] │
│  #124  MEDIUM   Health    5 days  [Submit] │
└────────────────────────────────────────────┘
```

---

## ⚡ Pro Tips

1. **Create multiple mitigation users** for different teams
2. **Assign data groups** to control what they can see
3. **Use meaningful usernames** like `safety_team`, `env_team`, etc.
4. **External system still works** - No changes to existing workflow

---

## 🆘 Need Help?

**Can't find role option?**
→ Make sure you ran Step 1 command

**User can't see tasks?**
→ Check they're logged in with correct username

**Manager can't see internal users?**
→ Refresh the page after creating users

---

## 📚 Full Documentation

For detailed information, see:

- `HSE_MITIGATION_SETUP_GUIDE.md` - Complete guide
- `IMPLEMENTATION_SUMMARY.md` - Technical details

---

**Happy Testing! 🎉**
