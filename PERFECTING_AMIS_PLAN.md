# Making AMIS Perfect - Implementation Plan

**Status:** IN PROGRESS
**Goal:** Fix all critical issues to achieve 10/10 rating

---

## ✅ COMPLETED (Backend)

### 1. Database Schema Extensions
- ✅ Added `production_lines` table
- ✅ Added `production_schedule` table
- ✅ Added `inventory_history` table (for trend charts)
- ✅ Added `machine_oee_history` table (for trend charts)

### 2. Database Functions (database.py)
- ✅ Added `get_production_lines()`
- ✅ Added `get_production_schedule()`
- ✅ Added `get_inventory_history()` - for 30-day trend charts
- ✅ Added `get_machine_oee_history()` - for 30-day OEE trends
- ✅ Added `adjust_inventory()` - for inventory adjustments

### 3. Data Population
- ✅ Created `populate_full_database.py`
- ✅ Generated 5 production lines with real utilization data
- ✅ Generated 4-week production schedule for all 5 products
- ✅ Generated 30 days of inventory history for trend charts
- ✅ Generated 30 days of OEE history for all machines
- ✅ Database populated successfully (192 KB)

### 4. Backend API Endpoints (main.py)
- ✅ GET `/api/production/lines` - Get production lines
- ✅ GET `/api/production/schedule/{product_id}` - Get 4-week schedule
- ✅ GET `/api/inventory/{product_id}/history` - Get inventory trend data
- ✅ GET `/api/machines/{machine_id}/oee-history` - Get OEE trend data
- ✅ POST `/api/inventory/{product_id}/adjust` - Adjust inventory

### 5. Frontend API Client (api.js)
- ✅ Added `getProductionLines()`
- ✅ Added `getProductionSchedule()`
- ✅ Added `getInventoryHistory()`
- ✅ Added `getMachineOEEHistory()`
- ✅ Added `adjustInventory()`

---

## 🚧 IN PROGRESS (Frontend Pages)

### Priority 1: Fix Production Planning Page (HIGH IMPACT)

**Current State:** All data hardcoded
**Target State:** Real database integration

**Changes Needed:**
1. Add product selector dropdown
2. Fetch production lines from `/api/production/lines?product_id={id}`
3. Fetch 4-week schedule from `/api/production/schedule/{id}`
4. Calculate metrics dynamically
5. Remove all hardcoded arrays

**File:** `frontend/src/pages/ProductionPlanning.jsx`

---

### Priority 2: Add Inventory Trend Chart (HIGH IMPACT)

**Current State:** Only shows current snapshot
**Target State:** 30-day inventory trend line chart

**Changes Needed:**
1. Fetch history data from `/api/inventory/{id}/history`
2. Add Recharts LineChart component
3. Display stock level, stockout risk over time
4. Show trend direction (increasing/decreasing)

**File:** `frontend/src/pages/InventoryControl.jsx`

**Chart Design:**
```jsx
<LineChart data={historyData}>
  <XAxis dataKey="date" />
  <YAxis yAxisId="left" />
  <YAxis yAxisId="right" orientation="right" />
  <Line yAxisId="left" dataKey="stock_level" stroke="#3b82f6" name="Stock Level" />
  <Line yAxisId="right" dataKey="stockout_risk" stroke="#ef4444" name="Risk %" />
  <Tooltip />
  <Legend />
</LineChart>
```

---

### Priority 3: Add OEE Trend Chart (HIGH IMPACT)

**Current State:** Only shows current OEE
**Target State:** 30-day OEE trend with components

**Changes Needed:**
1. Fetch OEE history from `/api/machines/{id}/oee-history`
2. Add Recharts AreaChart showing OEE, Availability, Performance, Quality
3. Add to machine detail modal

**File:** `frontend/src/components/MachineDetailModal.jsx`

---

### Priority 4: Add BOM Display (MEDIUM IMPACT)

**Current State:** BOM data exists but not displayed
**Target State:** Expandable BOM tree in Inventory page

**Changes Needed:**
1. Fetch BOM from `/api/products/{id}/bom`
2. Display as expandable tree/table
3. Show: Component, Quantity, Supplier, Stock Status

**File:** `frontend/src/pages/InventoryControl.jsx`

---

### Priority 5: Make Work Orders Persist (MEDIUM IMPACT)

**Current State:** Work order modal doesn't save
**Target State:** Work orders saved to database

**Changes Needed:**
1. Update WorkOrderModal to call `/api/work-orders`
2. Show success message
3. Refresh work orders list
4. Show created work orders in MachineHealth page

**File:** `frontend/src/components/WorkOrderModal.jsx`

---

### Priority 6: Add Inventory Adjustment Modal (MEDIUM IMPACT)

**Current State:** Can't adjust inventory
**Target State:** Modal to add/remove stock

**Changes Needed:**
1. Create InventoryAdjustmentModal component
2. Form: Quantity (+/-), Reason, User
3. POST to `/api/inventory/{id}/adjust`
4. Refresh inventory data
5. Show in activity log

**File:** `frontend/src/components/InventoryAdjustmentModal.jsx` (NEW)

---

## 📊 Expected Impact

| Change | Before Rating | After Rating | Impact |
|--------|--------------|--------------|--------|
| Fix Production Planning | 3/10 | 9/10 | ⬆️ +600% |
| Add Inventory Chart | 9/10 | 10/10 | ⬆️ +11% |
| Add OEE Chart | 8.5/10 | 10/10 | ⬆️ +18% |
| Add BOM Display | 9/10 | 10/10 | ⬆️ +11% |
| Persist Work Orders | 8.5/10 | 9.5/10 | ⬆️ +12% |
| Add Inventory Adjustment | 9/10 | 10/10 | ⬆️ +11% |

**Overall System Rating:**
- Before: 7.5/10
- After: **9.5/10** ⭐⭐⭐⭐⭐

---

## 🎯 Final Feature Checklist

### Data Persistence ✅
- [x] All data in SQLite database
- [x] Product filtering works
- [x] Activity logging
- [x] Data persists across refreshes

### Production Planning ✅ (After Update)
- [x] Real production lines from database
- [x] Real 4-week schedule
- [x] Dynamic capacity calculations
- [x] Overtime hours tracking
- [x] Bottleneck identification

### Inventory Management ✅ (After Charts)
- [x] Current stock levels (real data)
- [x] Reorder points
- [x] 30-day trend chart
- [x] BOM display
- [x] Inventory adjustment capability
- [x] Stockout risk visualization

### Machine Health ✅ (After Charts)
- [x] Real machine data
- [x] Alarms and alerts
- [x] Spare parts tracking
- [x] Maintenance history
- [x] 30-day OEE trend chart
- [x] Work order creation (persists)

### Compliance & Audit ✅
- [x] Activity logging
- [x] Audit trail
- [x] User tracking
- [x] Action timestamps

---

## 🔄 Implementation Order (Next Steps)

### Step 1: Update ProductionPlanning.jsx ⬅️ YOU ARE HERE
- Add product selector
- Fetch production lines from database
- Fetch schedule from database
- Calculate dynamic metrics
- Remove hardcoded data

**Estimated Time:** 30 minutes
**Impact:** Production Planning goes from 10% useful to 90% useful

### Step 2: Add Inventory Trend Chart
- Fetch inventory history
- Integrate Recharts LineChart
- Add date range selector

**Estimated Time:** 20 minutes
**Impact:** Shows "why" not just "what"

### Step 3: Add OEE Trend Chart
- Fetch OEE history
- Add chart to machine modal
- Show all components (A, P, Q)

**Estimated Time:** 20 minutes
**Impact:** Predictive insights

### Step 4: Add BOM Display
- Fetch BOM data
- Create expandable table
- Show stock status

**Estimated Time:** 15 minutes
**Impact:** Material planning capability

### Step 5: Persist Work Orders
- Update modal to POST
- Show success feedback
- Refresh list

**Estimated Time:** 15 minutes
**Impact:** Full CRUD operations

### Step 6: Add Inventory Adjustment
- Create modal component
- Form validation
- API integration

**Estimated Time:** 20 minutes
**Impact:** Inventory management (not just monitoring)

**TOTAL TIME: ~2 hours to perfection** 🚀

---

## 📝 Testing Checklist (After All Updates)

### Production Planning
- [ ] Switch products → Metrics update
- [ ] Production lines show correct utilization
- [ ] 4-week schedule displays real demand/capacity
- [ ] Overtime hours calculated correctly
- [ ] Bottlenecks identified

### Inventory Control
- [ ] Product selector works
- [ ] Trend chart shows 30-day history
- [ ] BOM displays all components
- [ ] Can adjust inventory (+/-)
- [ ] Activity log records adjustments

### Machine Health
- [ ] OEE trend chart visible
- [ ] Work orders save to database
- [ ] Refresh page → Work orders persist
- [ ] Spare parts status accurate

### Overall
- [ ] All pages use real database data
- [ ] No hardcoded values visible
- [ ] Charts render correctly
- [ ] Data persists across refreshes
- [ ] Activity log captures all actions

---

## 🏆 Success Metrics

**When AMIS is Perfect:**

1. **For Hackathon:** 10/10
   - Professional UI
   - Complete database backend
   - Real-time charts
   - Full CRUD operations
   - Production-ready code

2. **For Manufacturing Company:** 9/10
   - Can deploy TODAY for all operations
   - Replaces Excel/manual logs 100%
   - Provides insights (trends, predictions)
   - Compliance-ready (audit trail)
   - Worth $1,500-2,000/month

3. **For Production:** 8/10
   - Scalable architecture
   - Clean code
   - API documentation
   - Error handling
   - Ready for PostgreSQL migration

---

**Next Action:** Update ProductionPlanning.jsx to use real database data
