# AMIS Production-Ready Implementation Plan
## Complete System Enhancement - All Critical Gaps

---

## PRIORITY 1: CRITICAL PRODUCTION BLOCKERS (Week 1)

### 1. ✅ Work Order Management UI (BACKEND EXISTS - NEED UI)
**Status:** Backend complete, Frontend missing
**Files to Create/Modify:**
- Create: `frontend/src/components/WorkOrderModal.jsx`
- Modify: `frontend/src/pages/MachineHealth.jsx`
- Modify: `frontend/src/lib/api.js`

**Features:**
- Create work order button
- Work order form (type, priority, assigned_to, scheduled_date, description)
- Work order list table with status
- Status update (open → in_progress → completed)
- Filter by machine
- Visual status indicators

**API Endpoints (EXISTING):**
- POST /api/work-orders
- GET /api/work-orders?machine_id={id}
- PATCH /api/work-orders/{id}/status

---

### 2. ❌ Demand Forecasting System (COMPLETELY MISSING)
**Status:** Empty table, fake UI data, no AI agent
**Files to Create/Modify:**
- Modify: `backend/database.py` - add demand forecast functions
- Modify: `backend/main.py` - add demand forecast endpoints
- Create: `agents/demand_agent.py`
- Modify: `frontend/src/pages/DemandIntelligence.jsx` - replace all mock data
- Create: `frontend/src/components/ForecastInputModal.jsx`

**Database Functions Needed:**
```python
def create_demand_forecast(product_id, week_number, forecast_data)
def get_demand_forecasts(product_id, weeks=12)
def update_actual_demand(product_id, week_number, actual)
```

**API Endpoints Needed:**
- POST /api/demand/forecast
- GET /api/demand/forecast/{product_id}?weeks=12
- PATCH /api/demand/actual/{product_id}/{week}
- POST /api/agents/run/demand

**Features:**
- Manual forecast entry form
- Actual sales input
- AI forecast generation using demand_agent
- Variance analysis (forecast vs actual)
- Trend charts with real data
- Export to CSV

---

### 3. ❌ CSV/Excel Export System
**Status:** No export functionality anywhere
**Files to Create/Modify:**
- Create: `backend/exports.py` - CSV generation utilities
- Modify: ALL frontend pages - add export buttons
- Modify: `backend/main.py` - add export endpoints

**Export Endpoints Needed:**
- GET /api/export/inventory/{product_id}
- GET /api/export/machines/{machine_id}/oee
- GET /api/export/production-schedule/{product_id}
- GET /api/export/suppliers
- GET /api/export/work-orders
- GET /api/export/demand-forecast/{product_id}

**Export Features:**
- CSV format (UTF-8 with BOM for Excel)
- Filename with timestamp
- All visible data columns
- Filtered data respects UI filters

---

### 4. ❌ Editable Production Schedule
**Status:** Read-only, can't modify
**Files to Modify:**
- `backend/database.py` - add update_production_schedule()
- `backend/main.py` - add PUT endpoint
- `frontend/src/pages/ProductionPlanning.jsx` - make editable
- Create: `frontend/src/components/ScheduleEditModal.jsx`

**Features:**
- Click to edit schedule row
- Modify planned_production, capacity, overtime_hours
- Save changes to database
- Recalculate gap automatically
- Audit trail (who changed what, when)
- Validation (can't exceed capacity)

---

## PRIORITY 2: MAJOR FUNCTIONALITY GAPS (Week 2)

### 5. ❌ Purchase Order System
**Status:** Hardcoded mock data
**Files to Create:**
- Add PO schema to `schema.sql`
- Add PO functions to `database.py`
- Add PO endpoints to `main.py`
- Modify: `frontend/src/pages/SupplierManagement.jsx`
- Create: `frontend/src/components/PurchaseOrderModal.jsx`

**Database Schema:**
```sql
CREATE TABLE purchase_orders (
  id TEXT PRIMARY KEY,
  supplier_id TEXT NOT NULL,
  product_id TEXT,
  quantity INTEGER NOT NULL,
  unit_price REAL NOT NULL,
  total_value REAL NOT NULL,
  status TEXT DEFAULT 'pending',
  order_date DATE NOT NULL,
  expected_delivery DATE,
  actual_delivery DATE,
  notes TEXT,
  created_by TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);
```

**Features:**
- Create PO form
- PO list with filters (status, supplier, date range)
- Update PO status
- Track deliveries (expected vs actual)
- Link to supplier performance metrics

---

### 6. ❌ Alert Management System
**Status:** Alerts shown but can't acknowledge/dismiss
**Files to Modify:**
- Add alerts table to `schema.sql`
- Add alert functions to `database.py`
- Modify: `frontend/src/pages/Dashboard.jsx`

**Database Schema:**
```sql
CREATE TABLE system_alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL,
  severity TEXT NOT NULL,
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  source_id TEXT,
  acknowledged BOOLEAN DEFAULT 0,
  acknowledged_by TEXT,
  acknowledged_at TIMESTAMP,
  dismissed BOOLEAN DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Features:**
- Acknowledge button on alerts
- Dismiss/archive alerts
- Alert history view
- Filter (show only active/acknowledged/all)
- Click alert to drill-down to source (machine/inventory/etc)

---

### 7. ❌ Drill-Down Navigation
**Status:** Can't click alerts to see details
**Files to Modify:**
- `frontend/src/pages/Dashboard.jsx`
- `frontend/src/App.jsx` - handle query params

**Features:**
- Click inventory alert → navigate to /inventory?product={id}
- Click machine alert → navigate to /machines?machine={id}
- Click production alert → navigate to /production?product={id}
- Highlight relevant item on destination page

---

### 8. ❌ Shift Comparison Dashboard
**Status:** Only current metrics shown
**Files to Modify:**
- `backend/database.py` - add shift_summary table
- `backend/main.py` - add shift summary endpoint
- `frontend/src/pages/Dashboard.jsx` - add shift comparison cards

**Features:**
- Show current shift vs previous shift metrics
- Production count comparison
- Quality rate comparison
- Downtime comparison
- Shift handover notes

---

### 9. ❌ Editable Inventory Parameters
**Status:** Reorder points not editable in UI
**Files to Modify:**
- `backend/database.py` - update_inventory() exists but need UI endpoint
- `frontend/src/pages/InventoryControl.jsx`
- Create: `frontend/src/components/InventorySettingsModal.jsx`

**Features:**
- Edit reorder_point
- Edit safety_stock
- Edit avg_daily_usage
- Edit lead_time
- Recalculate stockout_risk automatically
- Show impact of changes (before/after comparison)

---

### 10. ❌ Maintenance Calendar View
**Status:** Only list view available
**Files to Create:**
- `frontend/src/components/MaintenanceCalendar.jsx`
- Install: `npm install react-big-calendar date-fns`

**Features:**
- Month/week/day calendar views
- Show scheduled maintenance (from machines.next_maintenance)
- Show completed maintenance (from maintenance_history)
- Drag-and-drop to reschedule
- Color coding by priority/type
- Click event to see details
- Export calendar to iCal

---

## PRIORITY 3: ENTERPRISE FEATURES (Week 3)

### 11. ❌ Mobile Responsiveness
**Status:** Desktop-only layout
**Files to Modify:**
- `frontend/tailwind.config.js` - ensure mobile breakpoints
- ALL pages in `frontend/src/pages/*.jsx`
- `frontend/src/components/Layout.jsx`

**Responsive Changes:**
- Hamburger menu for mobile
- Stack cards vertically on small screens
- Touch-friendly buttons (min 44x44px)
- Responsive tables (horizontal scroll or card layout)
- Charts scale properly
- Forms work on mobile

**Test Devices:**
- iPhone SE (375px)
- iPad (768px)
- Desktop (1920px)

---

### 12. ❌ Email/SMS Notifications
**Status:** No notification system
**Files to Create:**
- `backend/notifications.py`
- `backend/notification_config.json`
- Install: `pip install python-dotenv smtplib`

**Notification Triggers:**
- Machine failure risk > 80%
- Inventory below ROP
- Work order overdue
- Maintenance due in 3 days
- Production schedule delayed

**Notification Methods:**
- Email (SMTP)
- SMS (Twilio API) - optional
- In-app notifications (WebSocket) - future

**Database Schema:**
```sql
CREATE TABLE notification_settings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  event_type TEXT NOT NULL,
  email_enabled BOOLEAN DEFAULT 1,
  sms_enabled BOOLEAN DEFAULT 0,
  threshold_value REAL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

### 13. ❌ ERP Integration Layer
**Status:** No external system integration
**Files to Create:**
- `backend/integrations/erp_connector.py`
- `backend/integrations/webhook_handler.py`

**Integration Features:**
- REST API endpoints for ERP to push data
- Webhook endpoints for real-time updates
- API key authentication for external systems
- Data mapping/transformation layer
- Error handling and retry logic
- Integration audit log

**Endpoints:**
```
POST /api/integration/production-orders
POST /api/integration/inventory-update
POST /api/integration/supplier-delivery
GET /api/integration/status
```

---

### 14. ❌ Advanced Reporting
**Status:** No custom reports
**Files to Create:**
- `frontend/src/pages/Reports.jsx`
- `backend/reports.py`
- Install: `pip install reportlab` (for PDF)

**Report Types:**
- Daily production summary
- Weekly inventory report
- Monthly machine health report
- Supplier performance scorecard
- Custom date range reports
- Scheduled automated reports (email delivery)

---

### 15. ❌ User Management & Permissions
**Status:** Basic auth only, no role-based permissions
**Files to Modify:**
- `backend/auth.py` - add permission decorators
- Create: `frontend/src/pages/UserManagement.jsx`
- Add permissions table to schema

**Permission Levels:**
- Admin: Full access
- Manager: Read/write, can't manage users
- Operator: Read-only + work order updates
- Viewer: Read-only all pages

**Features:**
- User CRUD operations
- Role assignment
- Permission matrix
- Activity log per user
- Password reset workflow

---

### 16. ❌ Real-Time Data Integration
**Status:** All data is static/seeded
**Files to Create:**
- `backend/mqtt_client.py` - for IoT machine data
- `backend/opcua_client.py` - for industrial protocols
- `backend/data_ingestion.py` - ETL layer

**Integration Points:**
- MQTT broker for machine sensors
- OPC-UA server for PLC data
- REST API for ERP data feed
- File upload for CSV imports
- Database views for existing data warehouses

---

## IMPLEMENTATION ORDER

### Week 1 (Priority 1):
**Day 1-2:**
- ✅ Work Order UI
- ✅ CSV Export System

**Day 3-4:**
- ✅ Demand Forecasting (backend + frontend + AI agent)

**Day 5:**
- ✅ Editable Production Schedule
- Testing & Bug Fixes

### Week 2 (Priority 2):
**Day 1-2:**
- ✅ Purchase Order System
- ✅ Alert Management

**Day 3:**
- ✅ Drill-down Navigation
- ✅ Shift Comparison

**Day 4:**
- ✅ Editable Inventory Parameters
- ✅ Maintenance Calendar

**Day 5:**
- Testing & Refinement

### Week 3 (Priority 3):
**Day 1-2:**
- ✅ Mobile Responsiveness (all pages)

**Day 3:**
- ✅ Email Notifications

**Day 4-5:**
- ✅ ERP Integration Layer
- ✅ Advanced Reporting
- Final testing

### Week 4 (Optional - Enterprise):
- User Management & Permissions
- Real-Time Data Integration
- Performance optimization
- Production deployment

---

## SUCCESS METRICS

### Before (Current State):
- Usability Score: 7.2/10
- Feature Completeness: 5/10
- Production Ready: 4/10
- Work Order Management: 0% functional
- Demand Forecasting: 0% functional
- Data Export: 0% functional
- Mobile Support: 0% functional

### After (Target State):
- Usability Score: 9.5/10
- Feature Completeness: 9.5/10
- Production Ready: 9/10
- Work Order Management: 100% functional
- Demand Forecasting: 100% functional
- Data Export: 100% functional
- Mobile Support: 100% functional

---

## FILES CHECKLIST

### Backend Files to Modify:
- [ ] backend/database.py - Add demand forecast, PO, alert functions
- [ ] backend/main.py - Add 15+ new endpoints
- [ ] backend/schema.sql - Add PO, alerts, notifications tables
- [ ] backend/exports.py - NEW FILE
- [ ] backend/notifications.py - NEW FILE
- [ ] backend/reports.py - NEW FILE
- [ ] agents/demand_agent.py - NEW FILE
- [ ] backend/integrations/erp_connector.py - NEW FILE

### Frontend Files to Modify:
- [ ] frontend/src/pages/Dashboard.jsx
- [ ] frontend/src/pages/MachineHealth.jsx
- [ ] frontend/src/pages/InventoryControl.jsx
- [ ] frontend/src/pages/ProductionPlanning.jsx
- [ ] frontend/src/pages/DemandIntelligence.jsx
- [ ] frontend/src/pages/SupplierManagement.jsx
- [ ] frontend/src/components/Layout.jsx
- [ ] frontend/src/lib/api.js - Add 20+ new API methods

### Frontend Files to Create:
- [ ] frontend/src/components/WorkOrderModal.jsx
- [ ] frontend/src/components/PurchaseOrderModal.jsx
- [ ] frontend/src/components/ForecastInputModal.jsx
- [ ] frontend/src/components/ScheduleEditModal.jsx
- [ ] frontend/src/components/InventorySettingsModal.jsx
- [ ] frontend/src/components/MaintenanceCalendar.jsx
- [ ] frontend/src/pages/Reports.jsx
- [ ] frontend/src/pages/UserManagement.jsx

---

## ESTIMATED EFFORT

| Task | Backend | Frontend | Testing | Total Hours |
|------|---------|----------|---------|-------------|
| Work Order UI | 1h | 4h | 1h | 6h |
| CSV Export | 4h | 3h | 1h | 8h |
| Demand Forecasting | 6h | 6h | 2h | 14h |
| Editable Schedule | 2h | 4h | 1h | 7h |
| Purchase Orders | 6h | 5h | 2h | 13h |
| Alert Management | 4h | 4h | 1h | 9h |
| Drill-down Nav | 1h | 3h | 1h | 5h |
| Shift Comparison | 3h | 4h | 1h | 8h |
| Editable Inventory | 1h | 3h | 1h | 5h |
| Maintenance Calendar | 2h | 8h | 2h | 12h |
| Mobile Responsive | 0h | 16h | 4h | 20h |
| Email Notifications | 8h | 2h | 2h | 12h |
| ERP Integration | 12h | 4h | 4h | 20h |
| Advanced Reporting | 8h | 8h | 2h | 18h |
| User Management | 6h | 6h | 2h | 14h |
| Real-Time Data | 16h | 4h | 4h | 24h |
| **TOTAL** | **80h** | **84h** | **31h** | **195h** |

**Timeline:** ~5 weeks (40h/week) for 1 developer
**Timeline:** ~2.5 weeks (40h/week) for 2 developers
**Timeline:** ~3 weeks (with testing & QA)

---

## DEPLOYMENT CHECKLIST

### Before Production:
- [ ] All 16 tasks completed
- [ ] End-to-end testing on staging
- [ ] Load testing (100+ concurrent users)
- [ ] Security audit
- [ ] API documentation complete
- [ ] User training materials
- [ ] Backup/restore procedures tested
- [ ] Monitoring/alerting configured
- [ ] SSL certificates installed
- [ ] Environment variables secured

### Production Environment:
- [ ] Gunicorn/uWSGI for Python backend
- [ ] Nginx reverse proxy
- [ ] PostgreSQL (migrate from SQLite)
- [ ] Redis for caching
- [ ] Docker containers
- [ ] CI/CD pipeline
- [ ] Automated backups
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring (New Relic/Datadog)

---

Let's implement this plan systematically!
