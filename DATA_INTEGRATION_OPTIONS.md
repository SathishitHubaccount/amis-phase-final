# Data Integration Options for AMIS
## From Mock Data to Real Data: A Practical Guide

---

## The Problem

Currently, AMIS uses **hardcoded mock data** in two places:

1. **Frontend**: `mockData.js` - JavaScript objects with fake inventory, machines, suppliers
2. **Backend**: Hardcoded values in API endpoints (Dashboard metrics)

**Result**: The system looks great but doesn't reflect real manufacturing data.

---

## Option 1: SQLite Database (Easiest - Recommended for Hackathon++)

### **What It Is**:
SQLite is a file-based database. No server needed, just a `.db` file on your computer.

### **Pros**:
✅ **Zero setup** - Python has SQLite built-in
✅ **No server required** - Just a file (`amis.db`)
✅ **Perfect for demos** - Can pre-populate with realistic data
✅ **Fast to implement** - Can be done in 2-3 hours
✅ **Real SQL queries** - Learn database concepts

### **Cons**:
❌ Not for production (multi-user issues)
❌ Limited to single machine
❌ No advanced features (replication, clustering)

### **Use Cases**:
- ✅ Hackathon demo (with better data than mockData)
- ✅ Local development
- ✅ Prototype/MVP
- ❌ Real factory deployment

### **Implementation Complexity**: ⭐ (1/5)

---

## Option 2: PostgreSQL/MySQL Database (Medium - Best for Startups)

### **What It Is**:
Full database server running locally or in cloud (AWS RDS, Heroku, etc.)

### **Pros**:
✅ **Production-ready** - Used by real companies
✅ **Multi-user support** - Many people can use simultaneously
✅ **Advanced features** - Transactions, backups, replication
✅ **Scalable** - Can handle 1000s of products/machines
✅ **Free tier available** - Heroku, Supabase, Neon

### **Cons**:
❌ Requires setup (install PostgreSQL or use cloud)
❌ More complex than SQLite
❌ Needs connection management

### **Use Cases**:
- ✅ MVP for real customers
- ✅ Startup/small company deployment
- ✅ Cloud-based SaaS
- ❌ Enterprise with existing ERP (see Option 4)

### **Implementation Complexity**: ⭐⭐⭐ (3/5)

---

## Option 3: CSV/Excel Files (Simplest - Quick & Dirty)

### **What It Is**:
Store data in CSV/Excel files, read them in backend

### **Pros**:
✅ **Super easy** - Everyone understands Excel
✅ **No database needed** - Just files
✅ **Easy to edit** - Open in Excel, change values
✅ **Can be done in 30 minutes**

### **Cons**:
❌ Slow for large datasets
❌ No concurrent writes (file locking issues)
❌ No relationships between tables
❌ Not scalable

### **Use Cases**:
- ✅ Quick prototype
- ✅ Small datasets (< 1000 rows)
- ❌ Anything production
- ❌ Multiple users

### **Implementation Complexity**: ⭐ (1/5)

---

## Option 4: ERP/MES Integration (Hard - Real Manufacturing)

### **What It Is**:
Connect to existing enterprise systems like SAP, Oracle, Siemens MES

### **Pros**:
✅ **Real live data** - From actual factory
✅ **No duplicate data** - Single source of truth
✅ **Production-grade** - What real companies need

### **Cons**:
❌ **Very complex** - Requires IT department support
❌ **Slow** - Weeks/months of integration work
❌ **Expensive** - May require SAP consultants ($200+/hour)
❌ **Requires access** - Need VPN, credentials, permissions

### **Use Cases**:
- ✅ Real factory deployment
- ✅ Enterprise customer
- ❌ Hackathon/demo
- ❌ Startup without existing ERP

### **Implementation Complexity**: ⭐⭐⭐⭐⭐ (5/5)

---

## Option 5: API-Based Data Services (Medium - Modern Approach)

### **What It Is**:
Use third-party APIs or build your own data API layer

### **Examples**:
- Supabase (PostgreSQL with REST API)
- Firebase (NoSQL database with real-time sync)
- Airtable (Spreadsheet + API)

### **Pros**:
✅ **Fast setup** - 1-2 hours with Supabase
✅ **Real-time updates** - Data syncs automatically
✅ **Authentication included** - User management built-in
✅ **Free tier** - Good for demos/MVPs

### **Cons**:
❌ Vendor lock-in
❌ Costs money at scale
❌ Less control than own database

### **Use Cases**:
- ✅ Modern SaaS app
- ✅ Rapid prototyping
- ✅ Mobile + web sync
- ❌ Air-gapped factories (no internet)

### **Implementation Complexity**: ⭐⭐ (2/5)

---

## Recommended Path for YOU

### **For Your Hackathon (Next 2-3 Days):**

**Use SQLite Database** ✅

**Why?**
1. Can implement in 2-3 hours
2. Still have time before deadline
3. Shows "real database" not just mockData
4. Data persists between sessions
5. Can demo CRUD operations (Create, Read, Update, Delete)

**What You'll Gain:**
- ✅ Work orders actually save to database
- ✅ Inventory updates when you run analysis
- ✅ Activity log persists
- ✅ Can show "before/after" of creating work order
- ✅ Judges see you understand databases

---

## Implementation Guide: SQLite for AMIS

### **Step 1: Create Database Schema** (30 min)

```sql
-- products.sql

CREATE TABLE products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory (
    product_id TEXT PRIMARY KEY,
    current_stock INTEGER,
    safety_stock INTEGER,
    reorder_point INTEGER,
    avg_daily_usage REAL,
    lead_time INTEGER,
    stockout_risk REAL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE machines (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT,
    line TEXT,
    status TEXT,
    oee REAL,
    availability REAL,
    performance REAL,
    quality REAL,
    failure_risk REAL,
    production_capacity INTEGER,
    current_utilization REAL,
    last_maintenance DATE,
    next_maintenance DATE
);

CREATE TABLE machine_alarms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT,
    time TIMESTAMP,
    severity TEXT,
    message TEXT,
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

CREATE TABLE spare_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT,
    part_name TEXT,
    stock INTEGER,
    min_stock INTEGER,
    status TEXT,
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

CREATE TABLE work_orders (
    id TEXT PRIMARY KEY,
    machine_id TEXT,
    type TEXT,
    priority TEXT,
    assigned_to TEXT,
    scheduled_date DATE,
    estimated_duration REAL,
    description TEXT,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

CREATE TABLE suppliers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT,
    score INTEGER,
    rating TEXT,
    on_time_delivery REAL,
    quality_score REAL,
    base_cost REAL,
    lead_time INTEGER,
    risk TEXT
);

CREATE TABLE activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user TEXT,
    action TEXT,
    details TEXT
);

CREATE TABLE bom_items (
    id TEXT PRIMARY KEY,
    product_id TEXT,
    component_id TEXT,
    component_name TEXT,
    quantity INTEGER,
    stock INTEGER,
    supplier_id TEXT,
    cost REAL,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);
```

### **Step 2: Initialize Database in Backend** (30 min)

Create `backend/database.py`:

```python
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

DATABASE_PATH = Path(__file__).parent / "amis.db"

def get_db_connection():
    """Get database connection with row factory for dict-like access"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This makes rows behave like dicts
    return conn

def init_database():
    """Initialize database with schema"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Read and execute schema
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path) as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()

# Product operations
def get_all_products() -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

def get_product(product_id: str) -> Optional[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# Inventory operations
def get_inventory(product_id: str) -> Optional[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, p.name as product_name
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        WHERE i.product_id = ?
    """, (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_inventory(product_id: str, updates: Dict) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()

    # Build UPDATE query dynamically
    fields = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [product_id]

    cursor.execute(f"""
        UPDATE inventory
        SET {fields}
        WHERE product_id = ?
    """, values)

    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# Machine operations
def get_all_machines() -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM machines")
    machines = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return machines

def get_machine(machine_id: str) -> Optional[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get machine details
    cursor.execute("SELECT * FROM machines WHERE id = ?", (machine_id,))
    machine = cursor.fetchone()
    if not machine:
        conn.close()
        return None

    machine_dict = dict(machine)

    # Get alarms
    cursor.execute("""
        SELECT * FROM machine_alarms
        WHERE machine_id = ?
        ORDER BY time DESC
    """, (machine_id,))
    machine_dict['alarms'] = [dict(row) for row in cursor.fetchall()]

    # Get spare parts
    cursor.execute("""
        SELECT * FROM spare_parts
        WHERE machine_id = ?
    """, (machine_id,))
    machine_dict['spare_parts'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return machine_dict

def get_machines_by_product(product_id: str) -> List[Dict]:
    """Get machines that produce a specific product"""
    # This requires a product_machines mapping table
    # For now, use simple logic based on mockData mapping
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get from product_machines junction table
    cursor.execute("""
        SELECT m.* FROM machines m
        JOIN product_machines pm ON m.id = pm.machine_id
        WHERE pm.product_id = ?
    """, (product_id,))

    machines = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return machines

# Work Order operations
def create_work_order(work_order: Dict) -> str:
    """Create new work order and return ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    wo_id = f"WO-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    cursor.execute("""
        INSERT INTO work_orders
        (id, machine_id, type, priority, assigned_to, scheduled_date,
         estimated_duration, description, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        wo_id,
        work_order['machine_id'],
        work_order['type'],
        work_order['priority'],
        work_order['assigned_to'],
        work_order['scheduled_date'],
        work_order['estimated_duration'],
        work_order['description'],
        work_order.get('created_by', 'System User')
    ))

    conn.commit()
    conn.close()

    return wo_id

def get_work_orders(machine_id: Optional[str] = None) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()

    if machine_id:
        cursor.execute("""
            SELECT * FROM work_orders
            WHERE machine_id = ?
            ORDER BY created_at DESC
        """, (machine_id,))
    else:
        cursor.execute("SELECT * FROM work_orders ORDER BY created_at DESC")

    work_orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return work_orders

# Activity Log operations
def log_activity(user: str, action: str, details: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO activity_log (user, action, details)
        VALUES (?, ?, ?)
    """, (user, action, details))
    conn.commit()
    conn.close()

def get_activity_log(limit: int = 100) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM activity_log
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return logs

# Supplier operations
def get_all_suppliers() -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers")
    suppliers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return suppliers

def get_supplier(supplier_id: str) -> Optional[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
```

### **Step 3: Migrate Mock Data to Database** (30 min)

Create `backend/migrate_mock_data.py`:

```python
import sys
sys.path.append('..')

from database import (
    get_db_connection, init_database,
    create_work_order, log_activity
)
from frontend.src.lib.mockData import PRODUCTS, MACHINES, SUPPLIERS

def migrate_all():
    print("Initializing database...")
    init_database()

    print("Migrating products...")
    migrate_products()

    print("Migrating machines...")
    migrate_machines()

    print("Migrating suppliers...")
    migrate_suppliers()

    print("Migration complete!")

def migrate_products():
    conn = get_db_connection()
    cursor = conn.cursor()

    for product_id, data in PRODUCTS.items():
        # Insert product
        cursor.execute("""
            INSERT OR REPLACE INTO products (id, name, category, status)
            VALUES (?, ?, ?, ?)
        """, (product_id, data['name'], data['category'], data['status']))

        # Insert inventory
        inv = data['inventory']
        cursor.execute("""
            INSERT OR REPLACE INTO inventory
            (product_id, current_stock, safety_stock, reorder_point,
             avg_daily_usage, lead_time, stockout_risk)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            product_id,
            inv['currentStock'],
            inv['safetyStock'],
            inv['reorderPoint'],
            inv['avgDailyUsage'],
            inv['leadTime'],
            inv['stockoutRisk']
        ))

        # Insert BOM items
        for bom_item in data['bom']:
            cursor.execute("""
                INSERT OR REPLACE INTO bom_items
                (id, product_id, component_id, component_name,
                 quantity, stock, cost)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                bom_item['id'],
                product_id,
                bom_item['id'],
                bom_item['name'],
                bom_item['quantity'],
                bom_item['stock'],
                bom_item['cost']
            ))

    conn.commit()
    conn.close()

def migrate_machines():
    conn = get_db_connection()
    cursor = conn.cursor()

    for machine_id, data in MACHINES.items():
        # Insert machine
        cursor.execute("""
            INSERT OR REPLACE INTO machines
            (id, name, type, line, status, oee, availability, performance,
             quality, failure_risk, production_capacity, current_utilization,
             last_maintenance, next_maintenance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            machine_id, data['name'], data['type'], data['line'],
            data['status'], data['oee'], data['availability'],
            data['performance'], data['quality'], data['failureRisk'],
            data['productionCapacity'], data['currentUtilization'],
            data['lastMaintenance'], data['nextMaintenance']
        ))

        # Insert alarms
        if 'alarms' in data:
            for alarm in data['alarms']:
                cursor.execute("""
                    INSERT INTO machine_alarms
                    (machine_id, time, severity, message)
                    VALUES (?, ?, ?, ?)
                """, (machine_id, alarm['time'], alarm['severity'], alarm['message']))

        # Insert spare parts
        if 'spareParts' in data:
            for part in data['spareParts']:
                cursor.execute("""
                    INSERT INTO spare_parts
                    (machine_id, part_name, stock, min_stock, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (machine_id, part['part'], part['stock'],
                      part['minStock'], part['status']))

    conn.commit()
    conn.close()

def migrate_suppliers():
    conn = get_db_connection()
    cursor = conn.cursor()

    for supplier_id, data in SUPPLIERS.items():
        cursor.execute("""
            INSERT OR REPLACE INTO suppliers
            (id, name, location, score, rating, on_time_delivery,
             quality_score, base_cost, lead_time, risk)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            supplier_id, data['name'], data['location'], data['score'],
            data['rating'], data['onTimeDelivery'], data['quality'],
            data['baseCost'], data['leadTime'], data['risk']
        ))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate_all()
```

### **Step 4: Update API Endpoints** (1 hour)

Modify `backend/main.py`:

```python
from database import (
    get_all_products, get_product, get_inventory, update_inventory,
    get_all_machines, get_machine, get_machines_by_product,
    create_work_order, get_work_orders,
    log_activity, get_activity_log,
    get_all_suppliers, get_supplier
)

# Replace hardcoded endpoints with database calls

@app.get("/api/products")
async def get_products():
    """Get all products"""
    products = get_all_products()
    return {"products": products}

@app.get("/api/products/{product_id}/inventory")
async def get_product_inventory(product_id: str):
    """Get inventory for specific product"""
    inventory = get_inventory(product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Product not found")
    return inventory

@app.get("/api/machines")
async def get_machines(product_id: Optional[str] = None):
    """Get all machines or filter by product"""
    if product_id:
        machines = get_machines_by_product(product_id)
    else:
        machines = get_all_machines()
    return {"machines": machines}

@app.get("/api/machines/{machine_id}")
async def get_machine_details(machine_id: str):
    """Get detailed machine info including alarms and spare parts"""
    machine = get_machine(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@app.post("/api/work-orders")
async def create_new_work_order(work_order: dict):
    """Create a work order"""
    wo_id = create_work_order(work_order)

    # Log activity
    log_activity(
        user=work_order.get('created_by', 'System User'),
        action='Work Order Created',
        details=f"Created {work_order['type']} work order for {work_order['machine_id']}"
    )

    return {"work_order_id": wo_id, "status": "created"}

@app.get("/api/activity-log")
async def get_activities(limit: int = 100):
    """Get activity log"""
    activities = get_activity_log(limit)
    return {"activities": activities}
```

### **Step 5: Update Frontend to Use Real API** (30 min)

Modify `frontend/src/pages/InventoryControl.jsx`:

```javascript
import { useQuery } from '@tanstack/react-query'

export default function InventoryControl() {
  const [selectedProduct, setSelectedProduct] = useState('PROD-A')

  // Fetch real inventory data from database
  const { data: inventoryData, isLoading } = useQuery({
    queryKey: ['inventory', selectedProduct],
    queryFn: () => apiClient.getProductInventory(selectedProduct),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const inventory = inventoryData?.data

  return (
    <div className="space-y-6">
      <ProductSelector
        value={selectedProduct}
        onChange={setSelectedProduct}
      />

      {/* NOW SHOWING REAL DATA FROM DATABASE */}
      <MetricCard
        title="Current Stock"
        value={`${inventory?.current_stock || 0} units`}
        subtitle={`${Math.round((inventory?.current_stock || 0) / (inventory?.avg_daily_usage || 1))} days supply`}
      />

      <MetricCard
        title="Stockout Risk"
        value={`${inventory?.stockout_risk || 0}%`}  {/* REAL DATA! */}
        subtitle="Next 14 days"
      />
    </div>
  )
}
```

---

## Timeline Estimate

### **If You Start Now**:

**Day 1 (3-4 hours)**:
- ✅ Create SQLite schema
- ✅ Write database.py with CRUD functions
- ✅ Write migration script
- ✅ Run migration (populate database)

**Day 2 (3-4 hours)**:
- ✅ Update backend API endpoints to use database
- ✅ Test all endpoints with Postman/curl
- ✅ Update frontend to fetch real data

**Day 3 (2-3 hours)**:
- ✅ Add work order creation (saves to DB)
- ✅ Add activity logging (persists)
- ✅ Test full workflow: create work order → see in database → shows in UI

**Total**: 8-11 hours of work

---

## What You Gain

### **Before (Mock Data)**:
```
User: "Create work order for MCH-002"
System: Shows success message
User: Refreshes page
System: Work order is gone (never saved)
```

### **After (SQLite Database)**:
```
User: "Create work order for MCH-002"
System: Saves to database, returns WO-20260228-143022
User: Refreshes page
System: Work order still there! Shows in list
User: Closes browser, comes back tomorrow
System: All data persists!
```

### **Demo Impact**:
- ✅ "This work order is saved in a SQLite database"
- ✅ "If I refresh, the data persists"
- ✅ "The activity log shows all my actions"
- ✅ Shows you understand databases, not just frontend

---

## Beyond SQLite: Next Steps

### **After Hackathon (If You Want to Continue)**:

**Week 1**: PostgreSQL migration
- Deploy to Heroku/Render with Postgres
- Multiple users can access
- Production-ready

**Week 2**: API Improvements
- Add authentication (JWT tokens)
- Add pagination (don't return 10,000 rows at once)
- Add caching (Redis)

**Week 3**: Real-Time Updates
- WebSocket support
- Dashboard auto-updates when data changes
- No need to refresh

**Month 2**: ERP Integration (If You Get a Real Customer)
- SAP OData connector
- Pull real production data
- Push work orders back to SAP

---

## My Recommendation

### **For Hackathon Deadline (Next 2-3 Days)**:

**Option A**: Keep mock data, focus on polish
- ✅ Add charts (Recharts)
- ✅ Fix product filtering on all pages
- ✅ Add BOM tree view
- ❌ Still fake data

**Option B**: Add SQLite, sacrifice some polish
- ✅ Real database
- ✅ Data persists
- ✅ Work orders save
- ❌ Less time for charts/polish

**Option C (Best)**: Hybrid approach
- ✅ Add SQLite for critical pages (Inventory, Machines, Work Orders)
- ✅ Keep mock data for less important pages
- ✅ Get 80% benefit with 40% effort

---

## Conclusion

**You DON'T need to keep mock data.**

**Easiest path**: SQLite (can implement in 8-11 hours)

**Benefits**:
- Data persists
- Shows database knowledge
- Enables CRUD operations
- More impressive demo

**After hackathon**: Migrate to PostgreSQL for real deployment

---

**Want me to implement SQLite database for you RIGHT NOW?** I can:
1. Create schema.sql
2. Write database.py
3. Write migration script
4. Update API endpoints
5. Update frontend pages

**Time needed**: 1-2 hours of guided implementation

**Your choice**: Should we do it? 🚀
