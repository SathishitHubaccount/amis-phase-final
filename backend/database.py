"""
AMIS Database Module
SQLite database operations for manufacturing data
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

DATABASE_PATH = Path(__file__).parent / "amis.db"

def get_db_connection():
    """Get database connection with row factory for dict-like access"""
    conn = sqlite3.connect(str(DATABASE_PATH), timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Makes rows behave like dicts
    # Enable WAL mode for better concurrent access
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")  # 30 second timeout
    return conn

def init_database():
    """Initialize database with schema"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Read and execute schema
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
    print("[OK] Database initialized successfully")

# ============================================================================
# PRODUCT OPERATIONS
# ============================================================================

def get_all_products() -> List[Dict]:
    """Get all products"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id")
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

def get_product(product_id: str) -> Optional[Dict]:
    """Get single product by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# ============================================================================
# INVENTORY OPERATIONS
# ============================================================================

def get_inventory(product_id: str) -> Optional[Dict]:
    """Get inventory for specific product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, p.name as product_name, p.category
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        WHERE i.product_id = ?
    """, (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_inventory() -> List[Dict]:
    """Get inventory for all products"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, p.name as product_name, p.category
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        ORDER BY p.id
    """)
    inventory = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return inventory

def update_inventory(product_id: str, updates: Dict) -> bool:
    """Update inventory for a product"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Build UPDATE query dynamically
    fields = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [product_id]

    cursor.execute(f"""
        UPDATE inventory
        SET {fields}, last_updated = CURRENT_TIMESTAMP
        WHERE product_id = ?
    """, values)

    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# ============================================================================
# MACHINE OPERATIONS
# ============================================================================

def get_all_machines() -> List[Dict]:
    """Get all machines"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM machines ORDER BY id")
    machines = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return machines

def get_machine(machine_id: str) -> Optional[Dict]:
    """Get detailed machine info including alarms, spare parts, and maintenance history"""
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
        SELECT id, machine_id, time, severity, message
        FROM machine_alarms
        WHERE machine_id = ?
        ORDER BY time DESC
        LIMIT 10
    """, (machine_id,))
    machine_dict['alarms'] = [dict(row) for row in cursor.fetchall()]

    # Get spare parts
    cursor.execute("""
        SELECT part_name as part, stock, min_stock as minStock, status
        FROM spare_parts
        WHERE machine_id = ?
    """, (machine_id,))
    machine_dict['spareParts'] = [dict(row) for row in cursor.fetchall()]

    # Get maintenance history
    cursor.execute("""
        SELECT date, type, technician, duration, notes
        FROM maintenance_history
        WHERE machine_id = ?
        ORDER BY date DESC
        LIMIT 5
    """, (machine_id,))
    machine_dict['maintenanceHistory'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return machine_dict

def get_machines_by_product(product_id: str) -> List[Dict]:
    """Get machines that produce a specific product"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.* FROM machines m
        JOIN product_machines pm ON m.id = pm.machine_id
        WHERE pm.product_id = ?
        ORDER BY m.id
    """, (product_id,))

    machines = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return machines

def update_machine(machine_id: str, updates: Dict) -> bool:
    """Update machine data"""
    conn = get_db_connection()
    cursor = conn.cursor()

    fields = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [machine_id]

    cursor.execute(f"""
        UPDATE machines
        SET {fields}
        WHERE id = ?
    """, values)

    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# ============================================================================
# WORK ORDER OPERATIONS
# ============================================================================

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

def get_work_orders(machine_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """Get work orders, optionally filtered by machine"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if machine_id:
        cursor.execute("""
            SELECT wo.*, m.name as machine_name
            FROM work_orders wo
            JOIN machines m ON wo.machine_id = m.id
            WHERE wo.machine_id = ?
            ORDER BY wo.created_at DESC
            LIMIT ?
        """, (machine_id, limit))
    else:
        cursor.execute("""
            SELECT wo.*, m.name as machine_name
            FROM work_orders wo
            JOIN machines m ON wo.machine_id = m.id
            ORDER BY wo.created_at DESC
            LIMIT ?
        """, (limit,))

    work_orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return work_orders

def update_work_order_status(wo_id: str, status: str) -> bool:
    """Update work order status"""
    conn = get_db_connection()
    cursor = conn.cursor()

    updates = {'status': status}
    if status == 'completed':
        updates['completed_at'] = datetime.now().isoformat()

    fields = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [wo_id]

    cursor.execute(f"""
        UPDATE work_orders
        SET {fields}
        WHERE id = ?
    """, values)

    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# ============================================================================
# ACTIVITY LOG OPERATIONS
# ============================================================================

def log_activity(user: str, action: str, details: str):
    """Log an activity for audit trail"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO activity_log (user, action, details)
        VALUES (?, ?, ?)
    """, (user, action, details))
    conn.commit()
    conn.close()

def get_activity_log(limit: int = 100) -> List[Dict]:
    """Get recent activity log entries"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, user, action, details
        FROM activity_log
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return logs


# ============================================================================
# DECISIONS (AUDIT) OPERATIONS
# ============================================================================

def ensure_decisions_table():
    """Create decisions table if it doesn't exist (safe to call on startup)"""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_type TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            action_by TEXT NOT NULL,
            note TEXT,
            outcome TEXT,
            detail TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_decision(agent_type: str, title: str, status: str, action_by: str,
                  note: str = None, detail: str = None) -> int:
    """Save an Accept/Modify/Dismiss decision to the DB"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO decisions (agent_type, title, status, action_by, note, detail)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (agent_type, title, status, action_by, note or '', detail or ''))
    conn.commit()
    decision_id = cursor.lastrowid
    conn.close()
    # Also write to activity_log so Dashboard shows it
    log_activity(action_by, f'Decision {status}', f'[{agent_type.upper()}] {title}')
    return decision_id


def get_decisions(limit: int = 50) -> List[Dict]:
    """Get all recorded decisions ordered newest-first"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, agent_type, title, status, action_by, note, detail, timestamp
        FROM decisions
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

# ============================================================================
# SUPPLIER OPERATIONS
# ============================================================================

def get_all_suppliers() -> List[Dict]:
    """Get all suppliers"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers ORDER BY id")
    suppliers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return suppliers

def get_supplier(supplier_id: str) -> Optional[Dict]:
    """Get detailed supplier info including certifications, contracts, and incidents"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get supplier details
    cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
    supplier = cursor.fetchone()
    if not supplier:
        conn.close()
        return None

    supplier_dict = dict(supplier)

    # Get certifications
    cursor.execute("""
        SELECT certification
        FROM supplier_certifications
        WHERE supplier_id = ?
    """, (supplier_id,))
    supplier_dict['certifications'] = [row['certification'] for row in cursor.fetchall()]

    # Get contracts
    cursor.execute("""
        SELECT id, start_date as startDate, end_date as endDate, volume, status
        FROM supplier_contracts
        WHERE supplier_id = ?
        ORDER BY end_date DESC
    """, (supplier_id,))
    supplier_dict['contracts'] = [dict(row) for row in cursor.fetchall()]

    # Get incidents
    cursor.execute("""
        SELECT date, type, severity, resolution
        FROM supplier_incidents
        WHERE supplier_id = ?
        ORDER BY date DESC
        LIMIT 10
    """, (supplier_id,))
    supplier_dict['incidents'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return supplier_dict

# ============================================================================
# BOM OPERATIONS
# ============================================================================

def get_bom(product_id: str) -> List[Dict]:
    """Get Bill of Materials for a product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, component_id, component_name as name, quantity, stock, supplier_id as supplier, cost
        FROM bom_items
        WHERE product_id = ?
        ORDER BY component_name
    """, (product_id,))
    bom = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return bom

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_database_stats() -> Dict:
    """Get database statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()

    stats = {}

    # Count records in each table
    tables = ['products', 'machines', 'suppliers', 'work_orders', 'activity_log']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        stats[table] = cursor.fetchone()['count']

    # Get database file size
    stats['database_size_kb'] = DATABASE_PATH.stat().st_size / 1024 if DATABASE_PATH.exists() else 0

    conn.close()
    return stats

# ============================================================================
# PRODUCTION PLANNING OPERATIONS
# ============================================================================

def get_production_lines(product_id: Optional[str] = None) -> List[Dict]:
    """Get production lines, optionally filtered by product"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if product_id:
        cursor.execute("""
            SELECT pl.*, p.name as product_name, m.name as bottleneck_machine_name
            FROM production_lines pl
            LEFT JOIN products p ON pl.current_product_id = p.id
            LEFT JOIN machines m ON pl.bottleneck_machine_id = m.id
            WHERE pl.current_product_id = ?
        """, (product_id,))
    else:
        cursor.execute("""
            SELECT pl.*, p.name as product_name, m.name as bottleneck_machine_name
            FROM production_lines pl
            LEFT JOIN products p ON pl.current_product_id = p.id
            LEFT JOIN machines m ON pl.bottleneck_machine_id = m.id
        """)

    lines = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return lines

def get_production_schedule(product_id: str, weeks: int = 4) -> List[Dict]:
    """Get production schedule for a product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM production_schedule
        WHERE product_id = ?
        ORDER BY week_number
        LIMIT ?
    """, (product_id, weeks))
    schedule = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return schedule

def create_production_schedule(schedule_data: Dict) -> int:
    """Create new production schedule entry"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO production_schedule
        (product_id, week_number, week_start_date, demand, planned_production,
         capacity, gap, overtime_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        schedule_data['product_id'],
        schedule_data['week_number'],
        schedule_data['week_start_date'],
        schedule_data.get('demand', 0),
        schedule_data.get('planned_production', 0),
        schedule_data.get('capacity', 0),
        schedule_data.get('gap', 0),
        schedule_data.get('overtime_hours', 0)
    ))
    schedule_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return schedule_id

# ============================================================================
# HISTORY DATA FOR CHARTS
# ============================================================================

def get_inventory_history(product_id: str, days: int = 30) -> List[Dict]:
    """Get inventory history for trend charts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM inventory_history
        WHERE product_id = ?
        ORDER BY date DESC
        LIMIT ?
    """, (product_id, days))
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history[::-1]  # Reverse to chronological order

def add_inventory_snapshot(product_id: str):
    """Add current inventory state to history"""
    inventory = get_inventory(product_id)
    if not inventory:
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # Calculate days supply
    avg_daily_usage = inventory.get('avg_daily_usage', 1) or 1
    days_supply = inventory['current_stock'] / avg_daily_usage if avg_daily_usage > 0 else 0

    cursor.execute("""
        INSERT INTO inventory_history
        (product_id, date, stock_level, stockout_risk, days_supply)
        VALUES (?, DATE('now'), ?, ?, ?)
    """, (
        product_id,
        inventory['current_stock'],
        inventory.get('stockout_risk', 0),
        days_supply
    ))
    conn.commit()
    conn.close()

def get_machine_oee_history(machine_id: str, days: int = 30) -> List[Dict]:
    """Get machine OEE history for trend charts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM machine_oee_history
        WHERE machine_id = ?
        ORDER BY date DESC
        LIMIT ?
    """, (machine_id, days))
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history[::-1]  # Reverse to chronological order

def add_machine_oee_snapshot(machine_id: str):
    """Add current machine OEE to history"""
    machine = get_machine(machine_id)
    if not machine:
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO machine_oee_history
        (machine_id, date, oee, availability, performance, quality)
        VALUES (?, DATE('now'), ?, ?, ?, ?)
    """, (
        machine_id,
        machine.get('oee', 0),
        machine.get('availability', 0),
        machine.get('performance', 0),
        machine.get('quality', 0)
    ))
    conn.commit()
    conn.close()

# ============================================================================
# INVENTORY ADJUSTMENT
# ============================================================================

def adjust_inventory(product_id: str, quantity: int, reason: str, user: str = "System User") -> bool:
    """Adjust inventory quantity (can be positive or negative)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get current stock
    cursor.execute("SELECT current_stock FROM inventory WHERE product_id = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    current_stock = row['current_stock']
    new_stock = current_stock + quantity

    if new_stock < 0:
        conn.close()
        return False  # Can't have negative inventory

    # Update inventory
    cursor.execute("""
        UPDATE inventory
        SET current_stock = ?, last_updated = CURRENT_TIMESTAMP
        WHERE product_id = ?
    """, (new_stock, product_id))

    # Log the adjustment
    log_activity(
        user=user,
        action="Inventory Adjustment",
        details=f"Adjusted {product_id} by {quantity:+d} units (from {current_stock} to {new_stock}). Reason: {reason}"
    )

    conn.commit()
    conn.close()
    return True

def reset_database():
    """Reset database (delete and reinitialize) - USE WITH CAUTION"""
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
        print("[OK] Database deleted")

    init_database()
    print("[OK] Database reset complete")

# ============================================================================
# USER AUTHENTICATION OPERATIONS
# ============================================================================

def create_users_table():
    """Create users table for authentication"""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            hashed_password TEXT NOT NULL,
            role TEXT NOT NULL,
            disabled BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("[OK] Users table created")

def create_default_users():
    """Create default admin, manager, and operator users"""
    from auth import get_password_hash

    conn = get_db_connection()

    # Default admin user
    conn.execute("""
        INSERT OR IGNORE INTO users (username, email, full_name, hashed_password, role)
        VALUES (?, ?, ?, ?, ?)
    """, ("admin", "admin@amis.com", "System Administrator",
          get_password_hash("admin123"), "admin"))

    # Default manager user
    conn.execute("""
        INSERT OR IGNORE INTO users (username, email, full_name, hashed_password, role)
        VALUES (?, ?, ?, ?, ?)
    """, ("manager", "manager@amis.com", "Plant Manager",
          get_password_hash("manager123"), "manager"))

    # Default operator user
    conn.execute("""
        INSERT OR IGNORE INTO users (username, email, full_name, hashed_password, role)
        VALUES (?, ?, ?, ?, ?)
    """, ("operator", "operator@amis.com", "Production Operator",
          get_password_hash("operator123"), "operator"))

    conn.commit()
    conn.close()
    print("[OK] Default users created: admin, manager, operator")

def get_user(username: str) -> Optional[Dict]:
    """Get user by username"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return dict(user)
    return None

def update_last_login(username: str):
    """Update last login timestamp for user"""
    conn = get_db_connection()
    conn.execute(
        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?",
        (username,)
    )
    conn.commit()
    conn.close()

# ============================================================================
# DEMAND FORECASTING OPERATIONS
# ============================================================================

def create_demand_forecast(product_id: str, week_number: int, forecast_data: Dict) -> int:
    """Create new demand forecast"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO demand_forecasts
        (product_id, week_number, forecast_date, optimistic, base_case, pessimistic, actual)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        product_id,
        week_number,
        forecast_data.get('forecast_date'),
        forecast_data.get('optimistic'),
        forecast_data.get('base_case'),
        forecast_data.get('pessimistic'),
        forecast_data.get('actual', None)
    ))

    conn.commit()
    forecast_id = cursor.lastrowid
    conn.close()

    log_activity('System', 'Demand Forecast Created', f'Created forecast for {product_id} week {week_number}')
    return forecast_id

def get_demand_forecasts(product_id: str, weeks: int = 12) -> List[Dict]:
    """Get demand forecasts for product"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM demand_forecasts
        WHERE product_id = ?
        ORDER BY week_number
        LIMIT ?
    """, (product_id, weeks))

    forecasts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return forecasts

def update_actual_demand(product_id: str, week_number: int, actual: int) -> bool:
    """Update actual demand for forecast accuracy tracking"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE demand_forecasts
        SET actual = ?
        WHERE product_id = ? AND week_number = ?
    """, (actual, product_id, week_number))

    conn.commit()
    success = cursor.rowcount > 0
    conn.close()

    if success:
        log_activity('System', 'Actual Demand Updated', f'Updated actual demand for {product_id} week {week_number}: {actual}')

    return success

# ============================================================================
# PRODUCTION SCHEDULE UPDATE
# ============================================================================

def update_production_schedule(schedule_id: int, updates: Dict) -> bool:
    """Update production schedule and recalculate gap"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get current values
    cursor.execute("""
        SELECT demand, planned_production, capacity
        FROM production_schedule WHERE id = ?
    """, (schedule_id,))
    current = cursor.fetchone()

    if not current:
        conn.close()
        return False

    current_dict = dict(current)

    # Calculate new gap if needed
    planned = updates.get('planned_production', current_dict['planned_production'])
    capacity = updates.get('capacity', current_dict['capacity'])
    demand = current_dict['demand']

    updates['gap'] = demand - min(planned, capacity)

    # Build update query
    fields = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [schedule_id]

    cursor.execute(f"""
        UPDATE production_schedule
        SET {fields}
        WHERE id = ?
    """, values)

    conn.commit()
    success = cursor.rowcount > 0
    conn.close()

    if success:
        log_activity(
            updates.get('updated_by', 'System'),
            'Production Schedule Updated',
            f'Updated schedule {schedule_id}: {updates}'
        )

    return success

if __name__ == "__main__":
    # Initialize database if run directly
    print("Initializing AMIS database...")
    init_database()

    stats = get_database_stats()
    print("\nDatabase Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
