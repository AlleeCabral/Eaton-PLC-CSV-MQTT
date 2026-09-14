# HYPHEN GREEN HYDROGEN PROJECT
## FEED PACKAGE EP6 - DESALINATION FACILITY

# INFORMATION MANAGEMENT SYSTEMS & DIGITALIZATION STRATEGY
## FOR SMALL ENGINEERING COMPANY (BOREAL LIGHT)

---

## EXECUTIVE SUMMARY

Boreal Light is pleased to present a straightforward Information Management and Digitalization Strategy for FEED Package EP6 (Desalination Facility) for the Hyphen Green Hydrogen Project in Namibia.

Our approach uses **simple, proven tools already available in Microsoft 365** to ensure:
- Clear document control without complexity
- Real-time team collaboration
- Client transparency
- No expensive software subscriptions
- Easy transition to Execution phase

**Total Cost:** €400/month for Primavera Cloud only
**Team Size:** 8-10 people (all disciplines)
**FEED Duration:** 12-18 months

---

## 1. INFORMATION MANAGEMENT SYSTEM

### 1.1 Document Storage & Sharing (SharePoint)

**Tool:** Microsoft SharePoint (you already have in Microsoft 365)
**Cost:** €0 (included in Microsoft 365)

**How it works:**

All FEED documents stored in one SharePoint folder:

```
Hyphen-EP6-FEED/
│
├─ P&IDs/
│  ├─ PID_Intake_v1.pdf (OLD - Archive)
│  ├─ PID_Intake_v2.pdf (OLD - Archive)
│  └─ PID_Intake_v3.pdf ← CURRENT (everyone uses this)
│
├─ GA_Drawings/
│  ├─ GA_Site_Layout_v1.pdf (OLD)
│  └─ GA_Site_Layout_v2.pdf ← CURRENT
│
├─ Calculations/
│  ├─ Flow_Balance_v1.xlsx (OLD)
│  └─ Flow_Balance_v2.xlsx ← CURRENT
│
├─ Specifications/
│  ├─ Equipment_List_v1.xlsx (OLD)
│  └─ Equipment_List_v2.xlsx ← CURRENT
│
├─ 3D_Model/
│  ├─ Plant_Model_v1.SLDPRT (OLD)
│  └─ Plant_Model_v2.SLDPRT ← CURRENT
│
├─ Cost_Estimate/
│  ├─ Cost_v1.xlsx (Month 6 - Class 3)
│  ├─ Cost_v2.xlsx (Month 12 - Class 2)
│  └─ Cost_v3.xlsx ← FINAL
│
├─ Schedule/
│  ├─ Schedule_v1.pdf (from Primavera)
│  ├─ Schedule_v2.pdf (updated)
│  └─ Schedule_v3.pdf ← CURRENT
│
├─ Meeting_Minutes/
│  ├─ Weekly_Design_Review_2026-01-28.docx
│  ├─ Weekly_Design_Review_2026-02-04.docx
│  └─ [Continue for each meeting]
│
├─ Procurement/
│  ├─ RFQ_Issued.xlsx (list of quotes sent)
│  ├─ PO_Register.xlsx (orders placed)
│  └─ Equipment_Delivery_Status.xlsx
│
└─ Approvals/
   ├─ Approved_P&ID_v3.pdf
   ├─ Approved_GA_v2.pdf
   └─ Client_Sign-off_List.xlsx
```

**Rules:**
- Only current version used by team
- Old versions stay in folder (for history)
- File naming: `[Type]_[System]_v[Number].pdf`
- Version numbers: v1, v2, v3, etc.
- Only PM updates version numbers
- Everyone else: Read and download, don't modify

**Backup:** SharePoint automatically backs up daily (Microsoft handles)

---

### 1.2 Real-Time Team Collaboration (Microsoft Teams)

**Tool:** Microsoft Teams (included in Microsoft 365)
**Cost:** €0

**How it works:**

Create one Teams channel for the project:

```
CHANNEL: "Hyphen-EP6-FEED"

CONVERSATION THREADS:
├─ Daily (9 AM CET): "Good morning - Any blockers today?"
│  └─ Team reports: On schedule? Any issues?
│
├─ Weekly Design Review (Wednesday 10 AM)
│  └─ What we completed
│  └─ What we'll do next week
│  └─ Any changes needed
│
├─ Procurement Updates
│  └─ RFQs issued
│  └─ Quotes received
│  └─ POs placed
│  └─ Delivery status
│
├─ Technical Questions
│  └─ Engineers ask questions
│  └─ Experts answer immediately
│  └─ No email delays
│
└─ Action Items
   └─ Who needs to do what
   └─ By when
```

**Files Tab:**
- Links to SharePoint folder
- Everyone sees latest documents
- No confusion about which version

**Calendar:**
- Daily standup (15 min, 9 AM CET)
- Weekly design review (90 min, Wednesday 10 AM)
- Monthly cost & schedule review (60 min, 1st Friday)

---

### 1.3 Client Communication

**How it works:**

Every **Friday at 5 PM CET**, export current status from SharePoint:

```
Email to Client:
├─ Latest P&IDs (PDF)
├─ Latest GA Drawings (PDF)
├─ Latest 3D model screenshots (PDF)
├─ Updated equipment list (Excel)
├─ Updated schedule (PDF from Primavera)
├─ Cost status (Excel)
└─ Any changes approved this week (Word doc)
```

**Frequency:** Weekly (Friday)
**Format:** Email with PDF attachments
**Client Access:** Read-only - they see approved documents only

---

## 2. DIGITALIZATION STRATEGY

### 2.1 3D MODELING

**Software:** SolidWorks (you already have)
**Cost:** €0

**What we'll do:**

Create one 3D model of the entire desalination plant showing:
- Building structure and layout
- All major equipment (RO skids, tanks, pumps)
- Piping connections (main lines only)
- Location of electrical equipment (rough)
- Equipment locations and coordinates

**Model Progression:**

| Month | What | Detail Level | Question it answers |
|---|---|---|---|
| **1-2** | Rough layout | 20% | Does it fit in the space? |
| **3-6** | Equipment added | 50% | Do pipes connect? Any clashes? |
| **6-12** | Detailed | 70% | Can we build this? |

**Deliverables:**
- SolidWorks file (you keep, Client gets copy)
- PDF 3D views (for Client to review)
- 2D GA drawings extracted from model (for construction)

**Who owns it:** You keep master file during FEED. Client gets a copy when FEED ends.

---

### 2.2 ENGINEERING SUITE

**Software we'll use:**

| Tool | What | Cost | You Have? |
|---|---|---|---|
| **SolidWorks** | 3D CAD modeling | €0 | Yes |
| **AutoCAD** | 2D drawings (P&IDs, layouts) | €0 | Yes |
| **Excel** | Calculations, estimates, tracking | €0 | Yes |
| **Primavera Cloud** | Project scheduling | €400/mo | Subscribe |
| **CODESYS** | PLC programming (I&C) | €0-200 | Maybe |

**How we integrate:**

1. **Process Engineer** → Excel calculations
   - Calculates flow rates, sizing, energy
   - Results fed to Mechanical

2. **Mechanical Engineer** → SolidWorks 3D model
   - Receives sizing from Process
   - Draws equipment in 3D
   - Creates 2D P&IDs (AutoCAD)
   - Models piping connections
   
3. **Electrical Engineer** → AutoCAD
   - Receives equipment list from Mechanical
   - Draws single-line diagram
   - Plans cable routing
   
4. **I&C Engineer** → CODESYS (if used)
   - Receives control requirements
   - Programs PLC logic
   - Or uses standard controllers
   
5. **All disciplines** → Primavera Cloud
   - Schedule updates weekly
   - Track progress
   - Export to PDF for Client

**Document Control (Simple Method):**

```
NAMING CONVENTION:
[Type]_[System]_v[Number]_[Date]

Examples:
├─ PID_IntakeSys_v1_2026-02-15.pdf
├─ GA_PlantLayout_v2_2026-03-01.pdf
└─ FlowCalc_v1_2026-02-10.xlsx

VERSION RULE:
├─ v1 = Draft (team only)
├─ v2 = Review (sent to Client for comment)
├─ v3 = Approved (final, everyone uses this)
├─ v4+ = Only if major changes needed

STORAGE:
├─ All versions in SharePoint
├─ Current version labeled clearly
├─ Old versions in same folder (archive)
├─ Retention: 7 years (per contract)
```

---
// Where we need to send the output of our programs and what is the format? check lot 10

### 2.3 INTERFACE MANAGEMENT

**Definition:** Tracking where desalination plant connects to other systems

**Interfaces for this project:**

```
INCOMING TO EP6:
├─ INT-001: Seawater intake from port facility
│         Owner: Lot 7 (other package)
│         Spec: 55,000 m³/day @ salinity 35 ppt
│         Status: Confirm with Lot 7
│
├─ INT-002: Electrical power supply
│         Owner: Lot 4 (other package)
│         Spec: 12 MWh/day @ 33 kV
│         Status: Confirm spec with Lot 4
│
└─ INT-003: Control signals
          Owner: Lot 10 (other package)
          Spec: SCADA connection for monitoring
          Status: Pending

OUTGOING FROM EP6:
├─ OUT-001: Clean water to CEF (Lot 5)
│          Spec: 47,000 m³/day @ <500 ppm
│          Status: Confirm water quality with Lot 5
│
├─ OUT-002: Brine discharge
│          Spec: 8,000 m³/day
│          Status: Confirm disposal method with Lot 7
│
└─ OUT-003: Status data to control room (Lot 10)
           Spec: Daily performance reports
           Status: Define format with Lot 10
```

**How to manage:**

**NO NEED OR THIS PART??**

Simple Excel spreadsheet with columns:

```
| Interface | From/To | Owner | Spec | Status | Confirmed? | Date Confirmed |
|-----------|---------|-------|------|--------|-----------|-----------------|
| INT-001 | From Lot 7 | [Name] | 55k m³/day | OK | YES | 15-Feb |
| INT-002 | From Lot 4 | [Name] | 12 MWh/day | Pending | NO | - |
| OUT-001 | To Lot 5 | [Name] | 47k m³/day | OK | YES | 22-Feb |
```

**Update:** Monthly in meetings
**Storage:** SharePoint folder "Interfaces"

---

### 2.4 CHANGE MANAGEMENT

**Definition:** Process for approving changes to design/scope/schedule

**When changes happen:**

```
EXAMPLE: Client says "We need 10% more water output"

STEP 1: SUBMIT CHANGE REQUEST
  ├─ Who: Engineer submits one-page form
  ├─ Form has: Description, reason, impacts
  └─ Where: Email to PM + save in SharePoint

STEP 2: ASSESS IMPACT
  ├─ PM calculates:
  │  ├─ Cost impact: How much more? (+€200k?)
  │  ├─ Schedule impact: How much longer? (+3 weeks?)
  │  └─ Technical impact: What changes? (Larger RO? More power?)
  ├─ Takes: 2-3 days
  └─ Result: One-page impact summary

STEP 3: CLIENT DECISION
  ├─ PM presents impacts to Client
  ├─ Client decides: Approve or reject?
  ├─ If approve: Get written sign-off (email OK)
  └─ Takes: 1 week typically

STEP 4: IMPLEMENT
  ├─ If approved: Team updates design
  ├─ All affected disciplines updated
  ├─ New cost/schedule baseline created
  └─ Takes: Depends on change

STEP 5: CLOSE-OUT
  ├─ Mark change request as CLOSED
  ├─ File in SharePoint "Approvals" folder
  ├─ Send to Client: "Change approved and incorporated"
  └─ Done
```

**Change Request Form (Simple):**

```
CHANGE REQUEST FORM

Date: ___________
Requested by: ___________

DESCRIPTION:
What needs to change?
[Text here]

REASON:
Why does it need to change?
[Text here]

IMPACT:
- Cost impact: [€ increase]
- Schedule impact: [weeks added]
- Technical changes: [Description]

APPROVED BY CLIENT:
☐ Yes (date: ___)
☐ No (date: ___)

NOTES:
[Any other info]
```

**Storage:** SharePoint folder "Changes"
**Tracking:** Excel list of all CRs submitted + status

---

### 2.5 PROJECT CONTROLS (SCHEDULING & COST)

**Software:** Oracle Primavera Cloud
**Cost:** €400/month
**Why:** Client requires it (per tender document HSD-ILF-Z-GEN-PC-TEN-0201)

**What we'll track:**

#### Schedule:

```
LEVEL I: Summary (Big picture)
├─ Design Phase: Months 1-9
├─ Procurement: Months 3-10
├─ Cost Estimation: Months 6-12
└─ Handover: Months 12-13

LEVEL II: Detail
├─ Week 1-2: System setup
├─ Week 3-6: Design kickoff
├─ Week 7-36: Full design
├─ Week 37-52: Handover

LEVEL III: Detailed tasks
├─ P&ID development (process engineer - 8 weeks)
├─ 3D model update (mechanical - 10 weeks)
├─ Equipment sizing (mechanical - 6 weeks)
├─ Electrical design (electrical - 8 weeks)
├─ I&C design (I&C engineer - 10 weeks)
└─ [100+ individual tasks]
```

**How to use:**
- Primavera P6 Cloud (web-based, no installation)
- PM + Scheduler enter progress weekly
- Every Friday: Update actual work, recalculate schedule
- Export to PDF for Client

**Export schedule every Friday** at 4 PM CET

#### Cost Tracking:

**Month 6 Milestone:** Class 3 Cost Estimate
- Accuracy: -30% to +50%
- Based on equipment budgetary quotes
- Used for Go/No-Go decision

**Month 12 Milestone:** Class 2 Cost Estimate
- Accuracy: -5% to +10%
- Based on actual equipment quotes
- Used for EPC contract

**Simple Excel tracking:**

```
COST ESTIMATE (Month 12 - FINAL)

EQUIPMENT:
├─ RO Skid: €150,000 (quote from Grundfos)
├─ Intake Pump: €45,000
├─ Tanks: €60,000
├─ UV System: €25,000
├─ Electrical Equipment: €80,000
├─ Instrumentation: €30,000
└─ Subtotal Equipment: €390,000

MATERIALS:
├─ Piping & Fittings: €50,000
├─ Structural Steel: €40,000
├─ Electrical Cable: €20,000
└─ Subtotal Materials: €110,000

LABOR (your team):
├─ Design: €150,000 (3 people × 6 months)
├─ Procurement: €20,000
├─ Administration: €10,000
└─ Subtotal Labor: €180,000

TOTAL DIRECT COSTS: €680,000

CONTINGENCY (10%): €68,000

PROFIT & OVERHEAD (15%): €102,000

TOTAL FEED COST: €850,000
```

**Update:** Every month, review actual costs vs estimate

---

### 2.6 PROCUREMENT MANAGEMENT

**Definition:** Managing the process of buying equipment

**Process:**

```
MONTH 1-2: SPECIFICATION
├─ Equipment list created
├─ Technical specs written
├─ Performance requirements defined
└─ Long-lead items identified (>12 weeks delivery)

MONTH 2-3: RFQ ISSUANCE
├─ RFQ document prepared (what do we need?)
├─ Issued to 3 qualified suppliers minimum
├─ Deadline for quotes: 4 weeks
└─ Tracked in Excel

MONTH 3-5: QUOTE EVALUATION
├─ Quotes received from suppliers
├─ Compare: Price, delivery, specs
├─ Select best value supplier
├─ Negotiate if needed
└─ Make decision

MONTH 5-6: PURCHASE ORDERS
├─ POs issued to selected suppliers
├─ Supplier confirms: Delivery date OK?
├─ Payment terms agreed
└─ PO number assigned

MONTH 6-11: EXPEDITING
├─ Weekly supplier status updates
├─ Long-lead items tracked closely
├─ If delay: Alert team, adjust schedule
├─ FAT (Factory Acceptance Test) arranged for major equipment

MONTH 11+: DELIVERY & RECEIPT
├─ Receive shipment
├─ Inspect goods
├─ Pay invoice
├─ Store or send to job site
```

**Tracking (Simple Excel):**

```
PROCUREMENT TRACKER

| Item | Supplier | Quote $ | PO Issued | Delivery Expected | Status |
|------|----------|---------|-----------|------------------|---------|
| RO Skid | Grundfos | €150k | 01-Mar | 30-May | On-track |
| Pump | Ebara | €45k | 01-Mar | 15-May | On-track |
| Tanks | Criveller | €60k | 05-Mar | 20-May | At-risk (delayed quote) |
```

**Update:** Weekly
**Storage:** SharePoint "Procurement" folder
**Risk:** If any item shows "At-risk", alert team immediately

---

### 2.7 MATERIAL MANAGEMENT

**Definition:** Tracking physical equipment and materials from receipt to installation

**Process:**

```
RECEIVE: Equipment arrives at warehouse
├─ Check against PO: Quantity correct?
├─ Inspect: Any damage?
├─ Photo (if damaged)
├─ Record in Excel

STORE: Assign storage location
├─ Warehouse location code: A-01-01 (Aisle-Rack-Shelf)
├─ Note in inventory system
├─ Label equipment with ID tag
└─ Update Excel

USE: Material sent to job site
├─ Remove from warehouse
├─ Note in Excel: "Status = Shipped"
├─ Send with work order
└─ Track delivery

INSTALL: Equipment installed in plant
├─ Update Excel: "Status = Installed"
├─ Record actual installation location
├─ Take photos of installation
├─ Assign asset tag (e.g., "PUMP-001")
└─ Link to equipment manual
```

**Simple Excel Inventory:**

```
| Item | Qty | Supplier | Date Received | Location | Status | Cost | Notes |
|------|-----|----------|---------------|----------|--------|------|-------|
| 250mm Pipe | 500m | ABC Steel | 15-Mar | A-02-01 | In Stock | €50k | Stainless |
| RO Membrane | 20 | Dow | 20-Mar | A-01-02 | In Stock | €8k | Keep cool |
| Pump | 1 | Ebara | 10-Apr | B-01-01 | Installed | €45k | Asset PUMP-001 |
```

**Update:** When items arrive, shipped, or installed
**Storage:** SharePoint "Materials" folder

---

### 2.8 SUPPLY CHAIN & LOGISTICS

**How we manage delivery risks:**

```
EARLY ORDERING
├─ Critical items ordered 6+ months early
├─ Builds buffer for supply delays
└─ Reduces risk

DUAL SOURCING
├─ For critical items: Have backup supplier
├─ If primary delays: Use backup
└─ Costs little, saves schedule

EXPEDITING
├─ Weekly calls with major suppliers
├─ Status updates on shipments
├─ Alert team to any delays
└─ Arrange air freight if needed (costs more but saves time)

TRACKING
├─ Shipment register in Excel
├─ Track each shipment: Shipped date, Est arrival, Actual arrival
├─ Alert if delayed
└─ Arrange storage if early arrival
```

**Simple Tracking (Excel):**

```
| Item | Supplier | Ship Date | Est Arrival | Actual Arrival | Status |
|------|----------|-----------|-------------|-----------------|---------|
| RO Skid | Grundfos | 15-May | 30-May | TBD | In-transit |
| Pump | Ebara | 10-May | 25-May | 26-May | ARRIVED |
```

---

### 2.9 DOCUMENT CONTROL (ISO 10007)

**What is ISO 10007?**

Standard for managing document versions and changes. Simple approach:

**Naming Convention:**

```
[Document Type]_[System]_v[Number]_[Date]

Examples:
├─ PID_IntakeSys_v1_2026-02-15.pdf
├─ GA_Layout_v2_2026-03-01.pdf
├─ EquipList_v3_2026-04-10.xlsx
```

**Version Management:**

```
VERSION HISTORY:
├─ v1 = Draft (internal only)
├─ v2 = Ready for Client review
├─ v3 = Approved (CURRENT - everyone uses)
├─ v4 = Only if major changes
└─ v5 = Only if massive rework needed
```

**Approval Process:**

```
STEP 1: Author writes document (v1 - DRAFT)
        └─ Saved in SharePoint "Drafts" folder

STEP 2: Discipline lead reviews (3-5 days)
        ├─ Comments? Ask author to revise
        └─ OK? Move to v2

STEP 3: PM reviews (2-3 days)
        ├─ Check consistency with other documents
        └─ Approve or ask revisions

STEP 4: If major document, send to Client (1 week for review)
        ├─ Client comments?
        ├─ Author revises
        └─ Back to Client for final approval

STEP 5: PM approves final version (v3)
        ├─ Marked "APPROVED"
        ├─ Moved to "Approved" folder
        ├─ Everyone notified via Teams
        └─ This is the VERSION EVERYONE USES
```

**Storage Structure:**

```
SharePoint Folder:

Hyphen-EP6/
├─ Drafts/ (Work in progress)
│  ├─ PID_v1.pdf (Author working on this)
│  └─ GA_v1.pdf (In review with lead)
│
├─ In_Review/ (Awaiting approval)
│  ├─ PID_v2.pdf (Sent to Client)
│  └─ Cost_v1.pdf (Waiting PM review)
│
├─ Approved/ (Final versions - USE THESE)
│  ├─ PID_v3.pdf ← CURRENT
│  ├─ GA_v2.pdf ← CURRENT
│  ├─ Equipment_List_v3.xlsx ← CURRENT
│  └─ Cost_v3.xlsx ← FINAL
│
└─ Archive/ (Old versions - reference only)
   ├─ PID_v1.pdf
   ├─ PID_v2.pdf
   ├─ GA_v1.pdf
   └─ Equipment_v1.xlsx
```

**Approval Tracking:**

Simple Excel spreadsheet:

```
DOCUMENT CONTROL LOG

| Document | Current Ver | Author | Status | Approved By | Date | Notes |
|----------|-------------|--------|--------|------------|------|-------|
| PID | v3 | [Name] | APPROVED | PM | 15-Mar | Ready to use |
| GA | v2 | [Name] | APPROVED | PM | 20-Mar | Ready to use |
| EquipList | v3 | [Name] | APPROVED | Client | 10-Apr | Client signed off |
```

**Retention:** Keep all versions for 7 years (per contract)

---

### 2.10 CONSTRUCTION MANAGEMENT & DRONES

**During FEED Phase:**

We'll develop (not execute):
- Construction plan (what will be built first, second, third)
- Mechanical completion checklist (what needs to be done to finish)
- Inspection procedures (how to check quality)
- FAT/SAT procedures (Factory Acceptance Test, Site Acceptance Test)

**For Execution Phase (after FEED):**

If drones available, could use for:
- Weekly site progress photos (compare to schedule)
- 3D laser scans (high accuracy surveying)
- Documentation of as-built condition

**For Boreal Light:** Keep simple
- No drones during FEED
- Photography with regular camera
- Document progress manually

---

## 3. TRANSITION FROM FEED TO EXECUTION

### Timeline

```
MONTH 11-12: FINAL DESIGN COMPLETION
├─ All drawings finalized
├─ All equipment specified
├─ All costs finalized
├─ Class 2 cost estimate complete
└─ EPC contract prepared

MONTH 12-13: HANDOVER
├─ Execution contractor assigned
├─ Your team trains their team (1 week)
├─ All documents transferred to them
├─ Systems access granted
├─ You step back, they take over
└─ FEED officially closed

MONTH 13+: EXECUTION PHASE
├─ Execution contractor builds the plant
├─ You may provide ongoing support (if contract allows)
├─ Original design used as basis
└─ Handover to Operations when complete
```

### What Gets Handed Over

```
DOCUMENTS:
├─ All P&IDs (final versions)
├─ All GA drawings (final versions)
├─ Equipment specifications
├─ 3D model (SolidWorks files + PDFs)
├─ Cost estimates (all versions for reference)
├─ All calculations
└─ All approvals from Client

SYSTEMS:
├─ SharePoint access granted to Execution team
├─ Primavera schedule transferred
├─ Cost baseline files
├─ Procurement database (suppliers, quotes, POs)
├─ Material inventory list
└─ All procedures documented

TRAINING:
├─ 1-week training for Execution team
├─ How to use SharePoint
├─ How to use Primavera
├─ How documents are organized
├─ How to make changes
└─ How to contact Client
```

---

## 4. TEAM ORGANIZATION

### Boreal Light FEED Team

```
Hyphen-EP6 FEED Team (8-10 people)

PROJECT MANAGER (1 person)
├─ Overall coordination
├─ Client interface
├─ Schedule tracking
├─ Cost tracking
├─ Document control
└─ Change management

SENIOR MECHANICAL ENGINEER (1 person)
├─ Lead mechanical design
├─ P&ID lead
├─ Equipment sizing
├─ 3D model oversight
└─ Specifications

MECHANICAL ENGINEER / DRAFTSPERSON (1 person)
├─ GA drawings
├─ 3D modeling details
├─ Piping design
└─ Equipment coordination

PROCESS ENGINEER (0.5 person - Part-time or shared)
├─ Process flow design
├─ Sizing calculations
├─ Heat balance
├─ Material balance
└─ Performance specs

SENIOR ELECTRICAL ENGINEER (1 person)
├─ Electrical design lead
├─ Single-line diagram
├─ Cable sizing
├─ Equipment selection
└─ Specifications

ELECTRICAL TECHNICIAN (0.5 person - Part-time)
├─ Cable schedules
├─ Load calculations
├─ Equipment details
└─ Technical drawings

I&C ENGINEER (0.5-1 person)
├─ Control system design
├─ PLC programming (CODESYS if needed)
├─ Instrumentation selection
├─ Loop diagrams
└─ SCADA interface

COST & PROCUREMENT (1 person)
├─ RFQ preparation
├─ Quote evaluation
├─ Equipment purchasing
├─ Cost tracking
└─ Supplier management

TOTAL TEAM: 8-10 people (varies by discipline needs)
```

### Responsibilities

| Task | Who | When |
|------|-----|------|
| Schedule updates | PM | Every Friday |
| Cost tracking | Cost person | Monthly |
| Document approval | PM | As documents ready |
| Client communication | PM | Weekly (Friday email) |
| Design coordination | Senior Mech Eng | Weekly |
| Procurement | Cost person | Ongoing |
| 3D model updates | Mech Eng | Weekly |
| Meeting minutes | PM | After each meeting |

---

## 5. MEETINGS & COMMUNICATION

### Weekly Schedule

| Day | Time | Meeting | Duration | Who |
|-----|------|---------|----------|-----|
| **Monday** | 9 AM | Daily standup (Teams) | 15 min | All |
| **Wednesday** | 10 AM | Design review | 90 min | All team + Client |
| **Friday** | 4 PM | Schedule/cost review | 60 min | PM + Cost person |
| **Friday** | 5 PM | Client email | 30 min | PM (send weekly status) |

### Monthly Schedule

| When | Meeting | Purpose | Duration |
|------|---------|---------|----------|
| **1st Friday** | Cost & Procurement Review | Budget vs actual, PO status | 60 min |
| **2nd Friday** | Interface Coordination | Check all connections | 60 min |
| **3rd Friday** | Quality & Progress | Design completion %, issues | 60 min |

---

## 6. COSTS & BUDGET

### Software (12-18 months FEED)

| Software | Cost/Month | Duration | Total |
|----------|-----------|----------|-------|
| **Primavera Cloud** | €400 | 18 months | €7,200 |
| **Microsoft 365** | €0 | 18 months | €0 (you have) |
| **SolidWorks** | €0 | 18 months | €0 (you have) |
| **AutoCAD** | €0 | 18 months | €0 (you have) |
| **CODESYS** (if used) | €0-20 | 6 months | €0-120 |
| **Total Software** | | | **€7,200-7,320** |

### Team Costs (Estimated)

| Role | FTE | Months | Total Cost |
|------|-----|--------|-----------|
| Project Manager | 1.0 | 18 | €150,000 |
| Senior Mech Engineer | 1.0 | 18 | €140,000 |
| Mechanical/Draft | 0.8 | 18 | €100,000 |
| Process Engineer | 0.5 | 18 | €50,000 |
| Senior Elec Engineer | 1.0 | 18 | €135,000 |
| Electrical Tech | 0.5 | 18 | €50,000 |
| I&C Engineer | 0.8 | 18 | €110,000 |
| Cost/Procurement | 1.0 | 18 | €100,000 |
| **Total Labor** | | | **€835,000** |

### Total FEED Cost (Estimate)

```
Labor:              €835,000
Software:           €7,200
Travel/Meetings:    €20,000
Contingency (5%):   €43,000
─────────────────
TOTAL:              €905,200
```

**This is realistic for Boreal Light - a 30-person company with existing software.**

---

## 7. SUCCESS METRICS

Track these weekly:

| Metric | Target | How Often | Owner |
|--------|--------|-----------|-------|
| Schedule on-track | ≥90% complete by deadline | Weekly | PM |
| Cost on-track | Within ±5% of budget | Monthly | Cost person |
| Documents approved | <10 days v1→v3 | Per document | PM |
| Interface confirmations | 100% confirmed | Monthly | PM |
| Equipment POs issued | On schedule | Monthly | Cost person |
| No critical issues | Zero escalations | Weekly | PM |

---

## 8. RISKS & MITIGATION

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|-----------|
| Schedule delay | Missed milestones | Medium | Weekly schedule reviews, early warning |
| Equipment late | Affects Execution | Low | Dual sourcing, early orders |
| Design conflicts | Rework needed | Medium | 3D clash detection, weekly reviews |
| Client delays | Project halts | Medium | Clear approval path, escalation |
| Cost overrun | Budget exceeded | Medium | Detailed tracking, contingency allocated |
| Staff turnover | Knowledge loss | Low | Document everything, backup people |

---

## CONCLUSION

Boreal Light is committed to delivering a successful FEED study for the Hyphen Green Hydrogen Project using:

✓ **Simple tools** - SharePoint, Excel, Teams (you already have)
✓ **Low cost** - Only €7,200 for Primavera Cloud
✓ **Clear processes** - Easy to follow, no complexity
✓ **Client transparency** - Weekly updates
✓ **Realistic team** - 8-10 people, standard disciplines
✓ **Professional approach** - Industry best practices

**We understand our company size and capability, and we've designed this approach to fit our reality.**

---

**Prepared by:** Boreal Light
**Date:** January 2026
**Status:** READY FOR SUBMISSION ✓

---

## APPENDIX A: Simple Templates

### Change Request Form

```
CHANGE REQUEST

Project: Hyphen EP6
Date: ___________
Requested by: ___________

WHAT IS CHANGING?
[Description]

WHY?
[Reason]

IMPACTS:
- Cost change: € ________
- Schedule change: _________ weeks
- Other impacts: _________________

APPROVED?
☐ YES - Date: ___________
☐ NO - Date: ___________

Notes:
_________________________
```

### Interface Register (Excel)

```
Interface # | From | To | Owner | Spec | Confirmed | Date | Notes
INT-001 | Lot 7 | EP6 | [Name] | 55k m³/day | YES | 15-Feb | OK
INT-002 | Lot 4 | EP6 | [Name] | 12 MWh/day | NO | - | Pending
```

### Document Control Log (Excel)

```
Document | Version | Author | Status | Approved | Date | Link
PID_Intake | v3 | [Name] | APPROVED | PM | 15-Mar | SharePoint link
GA_Layout | v2 | [Name] | APPROVED | PM | 20-Mar | SharePoint link
```

---

**END OF DOCUMENT**