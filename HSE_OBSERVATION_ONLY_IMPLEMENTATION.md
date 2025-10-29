# HSE Observation-Only Risk Assessment Implementation

## ✅ COMPLETED IMPLEMENTATION

This document describes the implementation of **Observation-Only HSE Risk Assessments** - a new feature that allows creating HSE risk assessments based on manual observations without requiring parameter measurements.

---

## 🎯 Overview

### **Two Types of HSE Risk Assessments:**

1. **Parameter-Based (Existing - AUTO)**

   - Automatically triggered when parameter values are out of spec
   - Has parameter measurements
   - Trigger Type: `AUTO_OUT_OF_SPEC`

2. **Observation-Only (NEW - MANUAL)**
   - Manually flagged by inspector/user
   - No parameter measurements required
   - Trigger Type: `MANUAL_OBSERVATION`

### **Same Workflow After Creation:**

Both types follow the EXACT SAME workflow after creation:

- Inspector assessment
- Manager validation
- Mitigation assignment
- Mitigation work
- Manager approval
- Risk closure

---

## 📊 Database Changes

### **New Fields Added to `Evince` Model:**

```python
# In inspection_management/models/evince.py

hse_risk_trigger_type = models.CharField(
    max_length=25,
    blank=True,
    null=True,
    choices=[
        ('AUTO_OUT_OF_SPEC', 'Automatic - Out of Spec Parameters'),
        ('MANUAL_OBSERVATION', 'Manual - Observation Only'),
    ],
    help_text="How this HSE risk assessment was triggered"
)

hse_has_parameters = models.BooleanField(
    default=True,
    help_text="Whether this HSE risk assessment has associated parameter measurements"
)
```

### **Migration:**

- ✅ Migration file created: `0050_evince_hse_has_parameters_and_more.py`
- ✅ Migration applied successfully
- ✅ Existing data NOT affected (NULL/default values)

---

## 🔧 Backend Changes

### **1. Serializers Updated**

**File:** `IMS_BACKEND/api/serializers/hse_risk_assessment.py`

Added new fields to all serializers:

- `HSERiskAssessmentSerializer`
- `HSERiskAssessmentCreateSerializer`
- `HSERiskAssessmentUpdateSerializer`

Fields added:

```python
'hse_risk_trigger_type', 'hse_has_parameters',
```

### **2. New API Endpoint**

**File:** `IMS_BACKEND/api/viewsets/hse_risk_assessment.py`

**Endpoint:** `POST /api/hse_risk_assessments/create-observation-risk/`

**Purpose:** Create manual observation-only HSE risk assessment

**Request Body:**

```json
{
  "evince_id": 123,
  "hse_observation_details": "Observed unsafe condition...",
  "hse_risk_level": "HIGH",
  "hse_risk_category": "Safety",
  "hse_risk_notes": "Additional notes..."
}
```

**Response:**

```json
{
  "message": "Observation-only HSE risk created successfully",
  "evince": { ... }
}
```

**What it does:**

- Takes an existing evince
- Marks it as observation-only (`hse_risk_trigger_type = 'MANUAL_OBSERVATION'`)
- Sets `hse_has_parameters = False`
- Updates status to `InspectorReview`
- Saves observation details

### **3. Auto-Trigger Logic Updated**

**File:** `IMS_BACKEND/api/services/hse_risk_evince_service.py`

Updated `inspector_review` method to automatically set trigger type for parameter-based assessments:

```python
# NEW: Set trigger type for parameter-based assessments
if not evince.hse_risk_trigger_type:  # Only set if not already set
    evince.hse_risk_trigger_type = 'AUTO_OUT_OF_SPEC'
    evince.hse_has_parameters = True
```

**✅ Existing behavior UNCHANGED** - this only adds metadata, doesn't change workflow

---

## 🎨 Frontend Changes (TODO)

### **1. Flag as HSE Risk Button**

**Location:** Inspector evince list/dashboard

**Button:**

```jsx
<button
  onClick={() => handleFlagAsRisk(evince.id)}
  className="bg-orange-500 text-white px-4 py-2 rounded"
>
  🚨 Flag as HSE Risk
</button>
```

**Modal:** Opens modal to collect:

- Observation details
- Risk level
- Risk category
- Notes

**API Call:**

```javascript
const response = await fetch(
  "/api/hse_risk_assessments/create-observation-risk/",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      evince_id: evince.id,
      hse_observation_details: observationDetails,
      hse_risk_level: selectedRiskLevel,
      hse_risk_category: selectedCategory,
      hse_risk_notes: notes,
    }),
  }
);
```

### **2. Results Modal Update**

**Location:** `IMS-frontend/src/container/dashboardPages/evinces/results/HSEResultsModal.jsx`

**Change:** Hide "Technical Measurements" tab for observation-only assessments

```jsx
{
  /* Only show Technical Measurements tab if evince has parameters */
}
{
  evince?.hse_has_parameters !== false && (
    <button
      className={`px-6 py-3 font-medium text-sm ${
        activeTab === "technical"
          ? "border-b-2 border-blue-500 text-blue-600"
          : "text-gray-500 hover:text-gray-700"
      }`}
      onClick={() => setActiveTab("technical")}
    >
      📊 Technical Measurements
    </button>
  );
}
```

---

## 🔄 Complete Workflow

### **Parameter-Based (Automatic):**

```
1. Admin creates Evince
2. Inspector enters parameter values
3. System detects out of spec ⚙️
   → Auto-creates HSE Risk with:
     - hse_risk_trigger_type = 'AUTO_OUT_OF_SPEC'
     - hse_has_parameters = True
4. Inspector assesses risk (fills details)
5. Manager validates
6. Manager assigns mitigation
7. Mitigation work
8. Manager approves
9. Risk closed ✅
```

### **Observation-Only (Manual):**

```
1. Admin creates Evince (or Inspector has existing evince)
2. Inspector observes hazard 👀
3. Inspector clicks "Flag as HSE Risk" button 🚨
   → Creates HSE Risk with:
     - hse_risk_trigger_type = 'MANUAL_OBSERVATION'
     - hse_has_parameters = False
4. Inspector fills observation details in modal
5. Manager validates
6. Manager assigns mitigation
7. Mitigation work
8. Manager approves
9. Risk closed ✅
```

---

## 🧪 Testing

### **Test 1: Existing Parameter-Based Workflow**

**Status:** ⏳ TODO

**Steps:**

1. Create evince with parameters
2. Enter parameter values (some out of spec)
3. Verify HSE risk auto-created with:
   - `hse_risk_trigger_type = 'AUTO_OUT_OF_SPEC'`
   - `hse_has_parameters = True`
4. Complete full workflow
5. Verify NO BREAKING CHANGES

**Expected:** Everything works as before

### **Test 2: New Observation-Only Workflow**

**Status:** ⏳ TODO

**Steps:**

1. Create evince (any type)
2. Click "Flag as HSE Risk" button
3. Fill observation modal
4. Submit
5. Verify HSE risk created with:
   - `hse_risk_trigger_type = 'MANUAL_OBSERVATION'`
   - `hse_has_parameters = False`
6. Verify Technical Measurements tab hidden
7. Complete full workflow

**Expected:** New workflow works correctly

---

## 📝 Summary of Changes

### **✅ COMPLETED:**

1. ✅ Database fields added (`hse_risk_trigger_type`, `hse_has_parameters`)
2. ✅ Migration created and applied
3. ✅ Serializers updated
4. ✅ New API endpoint created (`create-observation-risk`)
5. ✅ Auto-trigger logic updated (sets trigger type for parameter-based)
6. ✅ Existing workflow preserved (NO BREAKING CHANGES)

### **⏳ TODO (Frontend):**

1. ⏳ Add "Flag as HSE Risk" button to inspector interface
2. ⏳ Create observation input modal
3. ⏳ Hide Technical Measurements tab for observation-only
4. ⏳ Test existing parameter-based workflow
5. ⏳ Test new observation-only workflow

---

## 🚀 Next Steps

### **Option 1: Add Button to Evince List**

- Add button in evince cards/rows
- Shows for all evinces
- Inspector can flag any evince as HSE risk

### **Option 2: Add Button to Inspector Dashboard**

- Add button in inspector stats dashboard
- Quick access to flag risks
- May need to select evince first

### **Option 3: Add Button to Results Entry Modal**

- Add button when inspector is entering results
- Context-aware (already viewing evince)
- Natural workflow

**Recommendation:** Option 3 (Results Entry Modal) is most intuitive

---

## 💡 Benefits

1. **Flexibility:** Handle both parameter-based and observation-only assessments
2. **Same Workflow:** No confusion, same process after creation
3. **No Breaking Changes:** Existing system works exactly as before
4. **Clear Tracking:** Know how each risk was triggered
5. **Future-Proof:** Easy to add more trigger types if needed

---

## 🔒 Safety & Backward Compatibility

- ✅ All new fields are NULL/default safe
- ✅ Existing evinces NOT affected
- ✅ Existing workflow UNCHANGED
- ✅ New feature is ADDITIVE only
- ✅ Can be rolled back if needed (fields are optional)

---

## 📞 Support

For questions or issues, refer to:

- Database schema: `inspection_management/models/evince.py`
- API endpoint: `api/viewsets/hse_risk_assessment.py`
- Workflow service: `api/services/hse_risk_evince_service.py`
- Migration: `inspection_management/migrations/0050_evince_hse_has_parameters_and_more.py`

---

**Implementation Date:** October 26, 2025  
**Status:** Backend Complete ✅ | Frontend In Progress ⏳
