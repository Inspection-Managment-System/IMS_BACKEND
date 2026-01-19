# Sami Pharma - HSE Risk Assessment Demo Data

## Complete Data Entry Guide (Step-by-Step)

---

## **STEP 1: COMPANY**

- **Name:** Sami Pharma
- **Description:** Pharmaceutical Manufacturing Company

---

## **STEP 2: SITE**

- **Name:** Sami Pharma - Main Manufacturing Facility
- **Description:** Primary production facility
- **Company:** Sami Pharma

---

## **STEP 3: BUSINESS UNITS** (Only 2 for Testing)

1. **Production Unit A**

   - Description: Main production line for tablets
   - Site: Sami Pharma - Main Manufacturing Facility

2. **Quality Control Lab**
   - Description: QC testing and analysis
   - Site: Sami Pharma - Main Manufacturing Facility

---

## **STEP 4: INSPECTION POINTS** (Only 2 for Testing)

1. **Tablet Compression Area**

   - Business Unit: Production Unit A
   - Description: Tablet compression machine inspection point

2. **Air Quality Monitoring Point**
   - Business Unit: Quality Control Lab
   - Description: Air quality testing station

---

## **STEP 5: UNITS** (Master Data)

1. **mg/L**

   - Description: Milligrams per liter

2. **ppm**

   - Description: Parts per million

3. **%**

   - Description: Percentage

4. **°C**

   - Description: Degrees Celsius

5. **dB**

   - Description: Decibels

6. **m/s**

   - Description: Meters per second

7. **Yes/No**

   - Description: Binary response

8. **Satisfactory/Unsatisfactory**
   - Description: Status check

---

## **STEP 6: ANALYSIS TYPES** (Master Data - Just 2 for Testing)

1. **Air Quality Analysis**

   - Description: Air quality monitoring and testing

2. **Noise Level Analysis**
   - Description: Noise pollution monitoring

---

## **STEP 7: LOCATIONS** (Required for Inspection Analysis)

**Note:** Create locations for the 2 inspection points.

1. **Production Unit A Location**

   - Name: Production Unit A - Main Floor
   - Description: Location for Production Unit A - Tablet Compression Area
   - Address: Building A, Floor 1
   - Building: Building A
   - Zip Code: (Optional)

2. **Quality Control Lab Location**
   - Name: QC Lab - Monitoring Station
   - Description: Location for Quality Control Lab - Air Quality Monitoring
   - Address: Building B, Floor 2
   - Building: Building B
   - Zip Code: (Optional)

---

## **STEP 7A: EQUIPMENT TYPES** (Master Data - Just a Few)

1. **Air Quality Monitor**

   - Description: Air quality monitoring equipment

2. **Noise Level Meter**

   - Description: Sound level measurement device

3. **Tablet Compression Machine**
   - Description: Pharmaceutical tablet compression equipment

---

## **STEP 7B: EQUIPMENT** (Just a Few Items)

1. **Air Quality Monitor - QC Lab**

   - Name: AQM-001
   - Description: Air quality monitoring device for QC Lab
   - Location: Quality Control Lab Location
   - Equipment Type: Air Quality Monitor
   - Serial No: AQM-2024-001
   - Asset Number: (Optional)
   - Calibration Date: (Today's date)
   - Calibration Expiry: (6 months from today)
   - Operator: (Select a user)

2. **Noise Level Meter - Production**

   - Name: NLM-001
   - Description: Noise level measurement device for Production Area
   - Location: Production Unit A Location
   - Equipment Type: Noise Level Meter
   - Serial No: NLM-2024-001
   - Asset Number: (Optional)
   - Calibration Date: (Today's date)
   - Calibration Expiry: (6 months from today)
   - Operator: (Select a user)

3. **Tablet Compression Machine - Unit A**
   - Name: TCM-001
   - Description: Tablet compression machine in Production Unit A
   - Location: Production Unit A Location
   - Equipment Type: Tablet Compression Machine
   - Serial No: TCM-2024-001
   - Asset Number: (Optional)
   - Calibration Date: (Today's date)
   - Calibration Expiry: (12 months from today)
   - Operator: (Select a user)

---

## **STEP 8: INSPECTION ANALYSIS** (Links Analysis Types to Inspection Points)

1. **Air Quality - QC Lab Monitoring**

   - Analysis Type: Air Quality Analysis
   - Location: Quality Control Lab Location
   - Reported Name: AQ_QC_Lab
   - Alias Name: Air Quality QC
   - Equipment: Air Quality Monitor - QC Lab (Optional)

2. **Noise Level - Compression Area**
   - Analysis Type: Noise Level Analysis
   - Location: Production Unit A Location
   - Reported Name: Noise_Prod_A
   - Alias Name: Noise Production
   - Equipment: Noise Level Meter - Production (Optional)

---

## **STEP 9: PARAMETERS** (For HSE Risk Assessment)

### **For "Air Quality - QC Lab Monitoring" Inspection Analysis:**

1. **Particulate Matter (PM2.5)**

   - Description: Fine particulate matter concentration
   - Inspection Analysis: Air Quality - QC Lab Monitoring
   - Unit: mg/L
   - Min Value: 0
   - Max Value: 25
   - Avg Value: 12

2. **Air Quality Index**
   - Description: Overall air quality rating
   - Inspection Analysis: Air Quality - QC Lab Monitoring
   - Unit: %
   - Min Value: 0
   - Max Value: 100
   - Avg Value: 50

### **For "Noise Level - Compression Area" Inspection Analysis:**

3. **Noise Level (dB)**

   - Description: Sound pressure level measurement
   - Inspection Analysis: Noise Level - Compression Area
   - Unit: dB
   - Min Value: 40
   - Max Value: 85
   - Avg Value: 65

4. **Hearing Protection Required**
   - Description: Whether hearing protection is needed
   - Inspection Analysis: Noise Level - Compression Area
   - Unit: Yes/No
   - Checklist Data Type: Yes/No
   - (Leave Min/Max/Avg blank for checklist types)

---

## **STEP 10: RISK LEVELS** (Master Data)

1. **Low**

   - Value: LOW
   - Description: Minimal risk, routine handling
   - Priority: (Auto - will be assigned as 1)

2. **Medium**

   - Value: MEDIUM
   - Description: Moderate risk, requires attention
   - Priority: (Auto - will be assigned as 2)

3. **High**

   - Value: HIGH
   - Description: Significant risk, immediate action
   - Priority: (Auto - will be assigned as 3)

4. **Critical**
   - Value: CRITICAL
   - Description: Severe risk, emergency response
   - Priority: (Auto - will be assigned as 4)

---

## **STEP 11: RISK CATEGORIES** (Master Data)

1. **Safety**

   - Value: Safety
   - Description: Safety-related risks
   - Priority: (Auto - will be assigned as 1)

2. **Environmental**

   - Value: Environmental
   - Description: Environmental impacts
   - Priority: (Auto - will be assigned as 2)

3. **Equipment**

   - Value: Equipment
   - Description: Equipment-related risks
   - Priority: (Auto - will be assigned as 3)

4. **Health**

   - Value: Health
   - Description: Health hazards
   - Priority: (Auto - will be assigned as 4)

5. **Process**
   - Value: Process
   - Description: Process deviations
   - Priority: (Auto - will be assigned as 5)

---

## **STEP 12: HSE OBSERVATION TYPES** (Master Data)

1. **Slip/Trip Hazard**

   - Value: slip_trip
   - Description: Slipping or tripping hazards
   - Priority: (Auto - will be assigned as 1)

2. **Equipment Safety Issue**

   - Value: equipment_safety
   - Description: Equipment safety concerns
   - Priority: (Auto - will be assigned as 2)

3. **Personal Protective Equipment**

   - Value: ppe
   - Description: PPE-related observations
   - Priority: (Auto - will be assigned as 3)

4. **Emergency Procedure**

   - Value: emergency
   - Description: Emergency response issues
   - Priority: (Auto - will be assigned as 4)

5. **Chemical Exposure**

   - Value: chemical
   - Description: Chemical handling concerns
   - Priority: (Auto - will be assigned as 5)

6. **Noise Pollution**

   - Value: noise
   - Description: Excessive noise levels
   - Priority: (Auto - will be assigned as 6)

7. **Air Quality**

   - Value: air_quality
   - Description: Air quality issues
   - Priority: (Auto - will be assigned as 7)

8. **Waste Management**
   - Value: waste
   - Description: Waste disposal concerns
   - Priority: (Auto - will be assigned as 8)

---

## **STEP 13: DEPARTMENTS** (For Assignment)

1. **Internal Maintenance**

   - Department Type: MAINTENANCE
   - Assignment Type: INTERNAL
   - Description: Internal maintenance department
   - Status: ACTIVE
   - Is Available: Yes

2. **Internal Safety Engineering**

   - Department Type: SAFETY
   - Assignment Type: INTERNAL
   - Description: Internal safety department
   - Status: ACTIVE
   - Is Available: Yes

3. **Internal Environmental Services**

   - Department Type: ENVIRONMENTAL
   - Assignment Type: INTERNAL
   - Description: Internal environmental department
   - Status: ACTIVE
   - Is Available: Yes

4. **Internal Quality Control**
   - Department Type: QUALITY
   - Assignment Type: INTERNAL
   - Description: Internal QC department
   - Status: ACTIVE
   - Is Available: Yes

---

## **STEP 14: SAMPLE HSE RISK ASSESSMENT RECORDS** (For Demo - Using Only 2 Inspection Points)

### **Assessment 1: Air Quality Monitoring - QC Lab**

- **Name:** Air Quality Monitoring - QC Lab
- **Type:** HSE Risk Management
- **Business Unit:** Quality Control Lab
- **Inspection Point:** Air Quality Monitoring Point
- **Observation Type:** Air Quality
- **Risk Level:** Medium
- **Risk Category:** Environmental
- **Status:** RiskValidated
- **Observation Details:** "Dust particles detected above normal levels. Requires immediate attention."
- **Inspection Analysis:** Air Quality - QC Lab Monitoring
- **Parameters to Add:**
  - Particulate Matter (PM2.5): 28 mg/L (Out of spec - max is 25)
  - Air Quality Index: 65%

### **Assessment 2: Noise Level Assessment - Production**

- **Name:** Noise Level Assessment - Production
- **Type:** HSE Risk Management
- **Business Unit:** Production Unit A
- **Inspection Point:** Tablet Compression Area
- **Observation Type:** Noise Pollution
- **Risk Level:** High
- **Risk Category:** Health
- **Status:** MitigationInProgress
- **Observation Details:** "Noise levels exceed safe limits. Hearing protection mandatory."
- **Inspection Analysis:** Noise Level - Compression Area
- **Parameters to Add:**
  - Noise Level (dB): 92 dB (Out of spec - max is 85)
  - Hearing Protection Required: Yes

---

## **QUICK REFERENCE CHECKLIST**

✅ **Step 1:** Company (1 item)
✅ **Step 2:** Site (1 item)
✅ **Step 3:** Business Units (2 items - Production Unit A, Quality Control Lab)
✅ **Step 4:** Inspection Points (2 items - Tablet Compression Area, Air Quality Monitoring Point)
✅ **Step 5:** Units (8 items)
✅ **Step 6:** Analysis Types (2 items - Air Quality Analysis, Noise Level Analysis)
✅ **Step 7:** Locations (2 items)
✅ **Step 7A:** Equipment Types (3 items)
✅ **Step 7B:** Equipment (3 items)
✅ **Step 8:** Inspection Analysis (2 items)
✅ **Step 9:** Parameters (4 items)
✅ **Step 10:** Risk Levels (4 items)
✅ **Step 11:** Risk Categories (5 items)
✅ **Step 12:** HSE Observation Types (8 items)
✅ **Step 13:** Departments (4 items)
✅ **Step 14:** Sample HSE Risk Assessments (2 items - optional for demo)

---

## **IMPORTANT NOTES:**

1. **Priority fields** are auto-incremented - don't enter them manually
2. **Data Group** - Make sure you select the correct Data Group for all master data items
3. **Locations** - If your system already has locations for Business Units, use those instead of creating new ones
4. **Equipment** - Leave blank in Inspection Analysis if not needed
5. **Checklist Parameters** - For Yes/No or Satisfactory/Unsatisfactory parameters, leave Min/Max/Avg values blank
6. **Order Matters** - Follow the steps in sequence as later steps depend on earlier ones

---

**Total Items to Create:**

- Master Data: ~35 items (simplified for 2 inspection points)
- Sample Assessments: 2 items (optional)

**Estimated Time:** 20-30 minutes for complete setup

---

## **SIMPLIFIED FOR TESTING - ONLY 2 INSPECTION POINTS**

This guide is simplified to work with only:

- **Tablet Compression Area** (Production Unit A)
- **Air Quality Monitoring Point** (Quality Control Lab)

All other data (Locations, Equipment Types, Equipment, Inspection Analysis, Parameters) is focused on supporting these 2 inspection points only.
