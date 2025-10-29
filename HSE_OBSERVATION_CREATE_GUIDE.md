# How to Create Observation-Only HSE Risk Assessment

## ✅ **UPDATED: Now You Can Create Observation-Only from UI!**

---

## 🎯 **Create HSE Risk Assessment Without Parameters**

### **Step 1: Open Create HSE Risk Assessment Modal**

From the admin or manager dashboard, click **"Create HSE Risk Assessment"** button.

---

### **Step 2: Select Assessment Type**

At the top of the modal, you'll now see **two radio button options**:

#### **Option 1: 📊 Parameter-Based Assessment**

- For inspections with parameter measurements
- Requires selecting inspection analysis and parameters
- Auto-triggers risk when parameters are out of spec

#### **Option 2: 👁️ Observation-Only Assessment** ✅ **SELECT THIS**

- For observations without parameter measurements
- **NO parameters required**
- Manual risk assessment based on observations

**Select: "👁️ Observation-Only Assessment"**

---

### **Step 3: Notice the Changes**

When you select "Observation-Only Assessment":

✅ **Parameters Tab Disappears** - You don't need to select parameters!  
✅ **Only 2 Tabs Remain:**

- General Information
- Additional Information

---

### **Step 4: Fill General Information Tab**

**Required Fields:**

- **Organization** - Select the organization
- **Facility** - Select the facility
- **Process Unit** - Select business unit
- **Operator Round Point** - Select inspection point/location
- **Managed By** - Select manager/reviewer
- **Assigned To** - Select inspector (optional)
- **Start Date Time** - When inspection starts
- **End Date Time** - When inspection ends

**NOT Required for Observation-Only:**

- ~~Analysis Type~~ - Skip this
- ~~Inspection Analysis~~ - Skip this
- ~~Parameters~~ - Skip this

---

### **Step 5: Fill Additional Information Tab** (Optional)

- Sample requirements
- Critical instructions
- Other notes

---

### **Step 6: Click "Create HSE Risk Assessment"**

The system will:

- ✅ Create evince with type `hse_risk_management`
- ✅ Set `hse_risk_trigger_type = 'MANUAL_OBSERVATION'`
- ✅ Set `hse_has_parameters = False`
- ✅ Skip parameter requirements
- ✅ Assign to inspector for observation entry

---

## 🔄 **What Happens Next?**

### **Inspector Workflow:**

1. **Inspector receives the assignment**
2. **Inspector enters observation details:**
   - What they observed
   - Risk level (LOW, MEDIUM, HIGH, CRITICAL)
   - Risk category (Safety, Environmental, Equipment, etc.)
   - Observation notes
3. **Inspector submits assessment**

### **Same as Parameter-Based After This:**

4. Manager validates the risk
5. Manager assigns mitigation (Internal/External)
6. Mitigation work is done
7. Manager approves
8. Risk closed ✅

---

## 📊 **Comparison: Parameter-Based vs Observation-Only**

| Feature                        | Parameter-Based    | Observation-Only   |
| ------------------------------ | ------------------ | ------------------ |
| **Requires Parameters**        | ✅ Yes             | ❌ No              |
| **Inspection Analysis**        | ✅ Required        | ❌ Not Required    |
| **Creation Method**            | Auto/Manual        | Manual Only        |
| **Trigger**                    | Out-of-spec values | Manual observation |
| **Technical Measurements Tab** | ✅ Shown           | ❌ Hidden          |
| **Rest of Workflow**           | ✅ Same            | ✅ Same            |

---

## 💡 **When to Use Each Type?**

### **Use Parameter-Based When:**

- You have equipment with measurable parameters
- You're monitoring temperature, pressure, flow rates, etc.
- You want auto-detection of out-of-spec conditions
- Example: "HVAC temperature exceeds 25°C limit"

### **Use Observation-Only When:**

- You observe a hazard visually
- No measurable parameters involved
- Manual inspection finds issues
- Example: "Observed oil leak on floor", "Fire extinguisher missing", "Unsafe working conditions"

---

## 🎉 **Benefits**

✅ **Faster Creation** - No need to select parameters  
✅ **Clearer Intent** - Explicitly marked as observation-only  
✅ **Same Workflow** - No confusion after creation  
✅ **Flexible** - Support both types in same system  
✅ **No Breaking Changes** - Existing parameter-based still works

---

## 🔍 **Verification**

After creation, you can verify it's observation-only by:

1. **Check the evince details:**

   - `hse_risk_trigger_type = 'MANUAL_OBSERVATION'`
   - `hse_has_parameters = False`

2. **Open the assessment modal:**

   - Technical Measurements tab is hidden
   - Only observation details are shown

3. **In database:**
   ```sql
   SELECT
     id,
     name,
     hse_risk_trigger_type,
     hse_has_parameters
   FROM inspection_management_evince
   WHERE evince_type = 'hse_risk_management'
     AND hse_risk_trigger_type = 'MANUAL_OBSERVATION';
   ```

---

## 📞 **Support**

If you have questions:

- Frontend: `IMS-frontend/src/container/dashboardPages/hseRiskManagement/CreateRiskAssessmentModal.jsx`
- Backend: `IMS_BACKEND/api/viewsets/hse_risk_assessment.py`
- Database: `IMS_BACKEND/inspection_management/models/evince.py`

---

**Updated:** October 26, 2025  
**Status:** ✅ **FULLY IMPLEMENTED - Frontend & Backend**
