"""
Comprehensive Data Migration Script
Migrates ALL data from sample_data.py to database tables.
Run this once to populate the database with all manufacturing data.
"""
import sqlite3
from datetime import datetime, timedelta
import math
import random

# Database path
DB_PATH = "../backend/amis.db"

def migrate_all_data():
    """Main migration function - populates all tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 60)
    print("AMIS DATABASE MIGRATION - ALL DATA")
    print("=" * 60)

    # 1. Products
    print("\n[1/15] Migrating products...")
    migrate_products(cursor)

    # 2. Inventory
    print("[2/15] Migrating inventory...")
    migrate_inventory(cursor)

    # 3. Warehouse zones
    print("[3/15] Migrating warehouse zones...")
    migrate_warehouse_zones(cursor)

    # 4. Stockout events
    print("[4/15] Migrating stockout events...")
    migrate_stockout_events(cursor)

    # 5. Suppliers
    print("[5/15] Migrating suppliers...")
    migrate_suppliers(cursor)

    # 6. Supplier contracts
    print("[6/15] Migrating supplier contracts...")
    migrate_supplier_contracts(cursor)

    # 7. Supplier risk factors
    print("[7/15] Migrating supplier risk factors...")
    migrate_supplier_risk(cursor)

    # 8. Purchase orders
    print("[8/15] Migrating purchase orders...")
    migrate_purchase_orders(cursor)

    # 9. Machines
    print("[9/15] Migrating machines...")
    migrate_machines(cursor)

    # 10. Sensor readings
    print("[10/15] Migrating sensor readings...")
    migrate_sensor_readings(cursor)

    # 11. Maintenance history
    print("[11/15] Migrating maintenance history...")
    migrate_maintenance_history(cursor)

    # 12. Production lines
    print("[12/15] Migrating production lines...")
    migrate_production_lines(cursor)

    # 13. Shift configuration
    print("[13/15] Migrating shift configuration...")
    migrate_shift_config(cursor)

    # 14. BOM (Bill of Materials)
    print("[14/15] Migrating bill of materials...")
    migrate_bom(cursor)

    # 15. Production schedule
    print("[15/15] Migrating production schedule...")
    migrate_production_schedule(cursor)

    conn.commit()
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)

    # Show summary
    print_migration_summary(cursor)

    conn.close()


def migrate_products(cursor):
    """Migrate product data."""
    cursor.execute("""
        INSERT OR REPLACE INTO products (id, name, category, status)
        VALUES ('PROD-A', 'Industrial Valve Assembly - Type A', 'Industrial Equipment', 'active')
    """)
    print("  [OK] 1 product inserted")


def migrate_inventory(cursor):
    """Migrate inventory data."""
    cursor.execute("""
        INSERT OR REPLACE INTO inventory (
            product_id, current_stock, safety_stock, reorder_point,
            avg_daily_usage, lead_time, stockout_risk,
            warehouse_location, bin_location,
            last_replenishment_date, last_stockout_date,
            unit_cost, holding_cost, last_updated
        ) VALUES (
            'PROD-A', 1850, 300, 961,
            142, 5, 0.15,
            'WH-MAIN', 'A-12-B',
            '2026-01-31', '2025-06-03',
            52.00, 2.30, CURRENT_TIMESTAMP
        )
    """)
    print("  [OK] 1 inventory record inserted")


def migrate_warehouse_zones(cursor):
    """Migrate warehouse zone data."""
    zones = [
        ('ZONE-A', 'PROD-A', 2500, 1200, 48.0, 'bulk', 0),
        ('ZONE-B', 'PROD-A', 1000, 450, 45.0, 'pick_pack', 0),
        ('ZONE-C', 'PROD-A', 1500, 200, 13.3, 'overflow', 0),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO warehouse_zones (
            zone_id, product_id, capacity, current_units, utilization,
            zone_type, temperature_controlled
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, zones)
    print(f"  [OK] {len(zones)} warehouse zones inserted")


def migrate_stockout_events(cursor):
    """Migrate historical stockout events."""
    events = [
        ('PROD-A', '2025-10-15', 3, 420, 'Supplier A delayed shipment by 4 days', 37590.00, 8),
        ('PROD-A', '2025-08-22', 1, 180, 'Unexpected demand spike from enterprise client', 16110.00, 3),
        ('PROD-A', '2025-06-03', 5, 650, 'Quality issue forced batch recall, depleted safety stock', 58175.00, 12),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO stockout_events (
            product_id, event_date, duration_days, units_short,
            root_cause, revenue_lost, customers_affected
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, events)
    print(f"  [OK] {len(events)} stockout events inserted")


def migrate_suppliers(cursor):
    """Migrate supplier data."""
    suppliers = [
        ('SUP-A', 'Supplier A', 'USA - Regional', 92, 'A', 92.5, 98.8, 100, 52.00, 4, 0.8, 'low', 100, 'NET-30', 'USD'),
        ('SUP-B', 'Supplier B', 'USA - Regional', 85, 'B+', 85.0, 97.9, 95, 49.50, 7, 1.5, 'medium', 200, 'NET-45', 'USD'),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO suppliers (
            id, name, location, score, rating,
            on_time_delivery, quality_score, cost_index, base_cost,
            lead_time, lead_time_variability, risk,
            moq, payment_terms, currency
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, suppliers)
    print(f"  [OK] {len(suppliers)} suppliers inserted")


def migrate_supplier_contracts(cursor):
    """Migrate supplier contracts."""
    contracts = [
        ('CTR-SUP-A-2026', 'SUP-A', '2026-01-01', '2026-12-31', 420000, 'active'),
        ('CTR-SUP-B-2026', 'SUP-B', '2026-01-01', '2026-06-30', 120000, 'active'),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO supplier_contracts (
            id, supplier_id, start_date, end_date, volume, status
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, contracts)
    print(f"  [OK] {len(contracts)} supplier contracts inserted")


def migrate_supplier_risk(cursor):
    """Migrate supply chain risk factors."""
    risks = [
        ('SH-100', 'Steel Housing', 'single_source', 1, 'low', 'medium', 65, 'Qualify SUP-B for Steel Housing; maintain 3-week safety stock'),
        ('VSA-200', 'Valve Seat Assembly', 'dual_source', 2, 'low', 'medium', 35, 'Maintain dual sourcing; increase SUP-A share if SUP-B contract lapses'),
        ('AM-300', 'Actuator Motor', 'single_source', 1, 'medium', 'low', 72, 'Identify domestic alternative; increase safety stock to 4 weeks'),
        ('SOR-400', 'Seals & O-rings Kit', 'multi_source', 3, 'low', 'low', 15, 'Commodity item — no action required'),
        ('FS-500', 'Fastener Set', 'multi_source', 3, 'low', 'low', 10, 'Commodity item — no action required'),
        ('IL-600', 'Inspection Labels & Packaging', 'multi_source', 2, 'low', 'low', 8, 'Commodity item — no action required'),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO supplier_risk (
            component_id, component_name, sourcing_type, qualified_suppliers,
            geographic_risk, lead_time_risk, risk_score, mitigation_strategy
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, risks)
    print(f"  [OK] {len(risks)} supplier risk records inserted")


def migrate_purchase_orders(cursor):
    """Migrate purchase order data (historical + open orders)."""
    # Historical orders (delivered)
    historical = [
        ('PO-2026-010', 'PROD-A', 'SUP-A', '2026-01-27', '2026-01-31', '2026-01-31', 500, 52.00, 26000.00, 'delivered', 'Delivered on time'),
        ('PO-2026-011', 'PROD-A', 'SUP-B', '2026-01-20', '2026-01-27', '2026-01-27', 300, 49.50, 14850.00, 'delivered', 'Delivered on time'),
        ('PO-2026-012', 'PROD-A', 'SUP-A', '2026-01-13', '2026-01-18', '2026-01-18', 600, 52.00, 31200.00, 'delivered', 'Delivered on time'),
        ('PO-2026-013', 'PROD-A', 'SUP-A', '2026-01-06', '2026-01-10', '2026-01-10', 500, 52.00, 26000.00, 'delivered', 'Delivered on time'),
        ('PO-2026-014', 'PROD-A', 'SUP-B', '2025-12-30', '2026-01-06', '2026-01-06', 400, 49.50, 19800.00, 'delivered', 'Delivered on time'),
        ('PO-2026-015', 'PROD-A', 'SUP-A', '2025-12-23', '2025-12-29', '2025-12-29', 700, 52.00, 36400.00, 'delivered', 'Delivered on time'),
        ('PO-2026-016', 'PROD-A', 'SUP-A', '2025-12-16', '2025-12-20', '2025-12-20', 500, 52.00, 26000.00, 'delivered', 'Delivered on time'),
        ('PO-2026-017', 'PROD-A', 'SUP-B', '2025-12-09', '2025-12-17', '2025-12-17', 300, 49.50, 14850.00, 'delivered', 'Delivered on time'),
    ]

    # Open orders (in transit or processing)
    open_orders = [
        ('PO-2026-018', 'PROD-A', 'SUP-A', '2026-02-17', '2026-02-21', None, 600, 52.00, 31200.00, 'in_transit', 'Shipment confirmed, on time'),
        ('PO-2026-019', 'PROD-A', 'SUP-B', '2026-02-14', '2026-02-21', None, 400, 49.50, 19800.00, 'in_transit', 'Shipment confirmed, on time'),
        ('PO-2026-020', 'PROD-A', 'SUP-A', '2026-02-18', '2026-02-22', None, 500, 52.00, 26000.00, 'processing', 'Awaiting dispatch from supplier warehouse'),
        ('PO-2026-021', 'PROD-A', 'SUP-A', '2026-02-19', '2026-02-22', None, 800, 52.00, 41600.00, 'processing', 'Awaiting dispatch'),
    ]

    all_orders = historical + open_orders

    cursor.executemany("""
        INSERT OR REPLACE INTO purchase_orders (
            po_id, product_id, supplier_id, order_date,
            expected_delivery_date, actual_delivery_date,
            quantity, unit_cost, total_cost, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, all_orders)
    print(f"  [OK] {len(all_orders)} purchase orders inserted ({len(open_orders)} open, {len(historical)} delivered)")


def migrate_machines(cursor):
    """Migrate machine fleet data."""
    machines = [
        ('MCH-001', 'Assembly Robot - Line 1', 'robotic_assembly', 'Line 1', 'operational', 0.896, 0.96, 0.92, 0.992, 0.09, 55, 0.92, 2.3, 47, 18.5, 25000, 180000, '2026-01-10', '2026-03-10'),
        ('MCH-002', 'CNC Machining Center - Line 2', 'cnc_machining', 'Line 2', 'operational', 0.634, 0.85, 0.77, 0.968, 0.58, 60, 0.75, 4.2, 81, 47, 48000, 412000, '2025-11-20', '2026-02-28'),
        ('MCH-003', 'Hydraulic Press - Line 3', 'hydraulic_press', 'Line 3', 'operational', 0.789, 0.91, 0.88, 0.984, 0.26, 50, 0.88, 3.8, 78, 37, 33000, 285000, '2025-12-15', '2026-03-01'),
        ('MCH-004', 'Conveyor & Material Handling - Line 4', 'conveyor_system', 'Line 4', 'down', 0.0, 0.0, 0.0, 0.0, 1.0, 45, 0.0, 11.2, 74, 0, 68000, 580000, '2026-02-18', '2026-02-23'),
        ('MCH-005', 'Welding Station - Line 5', 'welding_station', 'Line 5', 'operational', 0.937, 0.98, 0.96, 0.996, 0.04, 58, 0.96, 1.3, 39, 28, 18000, 98000, '2026-01-25', '2026-04-25'),
        ('MCH-006', 'Automated Quality Inspection System', 'quality_inspection', 'All Lines', 'operational', 0.969, 0.99, 0.98, 0.999, 0.02, 0, 0.98, 0.5, 33, 5, 10500, 8500, '2026-02-01', '2026-08-01'),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO machines (
            id, name, type, line, status, oee, availability, performance, quality,
            failure_risk, production_capacity, current_utilization,
            vibration_level, temperature, power_consumption, runtime_hours, cycle_count,
            last_maintenance, next_maintenance
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, machines)
    print(f"  [OK] {len(machines)} machines inserted")


def migrate_sensor_readings(cursor):
    """Migrate latest sensor readings for each machine."""
    # Create multiple sensor readings per machine (latest 7 days of key sensors)
    sensor_data = []
    base_date = datetime.now()

    # MCH-001 - Assembly Robot
    for i in range(7):
        date = base_date - timedelta(days=6-i)
        sensor_data.append(('MCH-001', date.strftime('%Y-%m-%d %H:%M:%S'), 'vibration', 2.0 + i*0.05, 'mm/s²', 2.1, 3.5, 5.0, 'normal'))
        sensor_data.append(('MCH-001', date.strftime('%Y-%m-%d %H:%M:%S'), 'temperature', 44 + i*0.5, '°C', 45, 65, 80, 'normal'))

    # MCH-002 - CNC Machine (WARNING)
    for i in range(7):
        date = base_date - timedelta(days=6-i)
        sensor_data.append(('MCH-002', date.strftime('%Y-%m-%d %H:%M:%S'), 'vibration', 2.0 + i*0.37, 'mm/s²', 1.8, 3.0, 5.5, 'warning' if i >= 5 else 'normal'))
        sensor_data.append(('MCH-002', date.strftime('%Y-%m-%d %H:%M:%S'), 'temperature', 73 + i*1.3, '°C', 72, 85, 95, 'warning' if i >= 5 else 'normal'))

    # MCH-003 - Hydraulic Press
    for i in range(7):
        date = base_date - timedelta(days=6-i)
        sensor_data.append(('MCH-003', date.strftime('%Y-%m-%d %H:%M:%S'), 'temperature', 69 + i*1.5, '°C', 68, 85, 100, 'normal'))
        sensor_data.append(('MCH-003', date.strftime('%Y-%m-%d %H:%M:%S'), 'hydraulic_pressure', 180 - i, 'bar', 180, 160, 150, 'normal'))

    # MCH-004 - Conveyor (DOWN - show failure spike)
    for i in range(5):  # Only 5 days before failure
        date = base_date - timedelta(days=6-i)
        sensor_data.append(('MCH-004', date.strftime('%Y-%m-%d %H:%M:%S'), 'vibration', 3.2 + i*2.0, 'mm/s²', 3.0, 6.0, 10.0, 'critical' if i >= 4 else 'warning' if i >= 2 else 'normal'))
        sensor_data.append(('MCH-004', date.strftime('%Y-%m-%d %H:%M:%S'), 'temperature', 55 + i*4.75, '°C', 55, 65, 75, 'critical' if i >= 4 else 'normal'))

    # MCH-005 - Welding Station
    for i in range(7):
        date = base_date - timedelta(days=6-i)
        sensor_data.append(('MCH-005', date.strftime('%Y-%m-%d %H:%M:%S'), 'vibration', 1.2 + (i % 2) * 0.1, 'mm/s²', 1.2, 2.5, 4.0, 'normal'))
        sensor_data.append(('MCH-005', date.strftime('%Y-%m-%d %H:%M:%S'), 'temperature', 38 + (i % 2), '°C', 38, 55, 70, 'normal'))

    # MCH-006 - Quality Inspection
    for i in range(7):
        date = base_date - timedelta(days=6-i)
        sensor_data.append(('MCH-006', date.strftime('%Y-%m-%d %H:%M:%S'), 'temperature', 32 + (i % 2), '°C', 32, 45, 55, 'normal'))

    cursor.executemany("""
        INSERT OR REPLACE INTO sensor_readings (
            machine_id, timestamp, sensor_type, value, unit,
            baseline, threshold_high, threshold_critical, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sensor_data)
    print(f"  [OK] {len(sensor_data)} sensor readings inserted")


def migrate_maintenance_history(cursor):
    """Migrate maintenance history."""
    history = [
        ('MCH-002', '2025-08-14', 'unplanned', 'Maintenance Team Lead', '2.5 days', 'Spindle bearing replacement after vibration alarm'),
        ('MCH-001', '2026-01-10', 'planned', 'Technician B', '1.0 days', 'Scheduled 3-month preventive maintenance'),
        ('MCH-003', '2025-09-28', 'unplanned', 'Technician C', '1.5 days', 'Hydraulic seal replacement — oil leak detected'),
        ('MCH-005', '2026-01-25', 'planned', 'Technician D', '0.5 days', 'Scheduled 6-month preventive maintenance + torch inspection'),
        ('MCH-004', '2026-02-18', 'unplanned', 'Maintenance Team Lead', '5.0 days', 'Bearing seizure — conveyor drive shaft failure'),
        ('MCH-003', '2025-12-15', 'planned', 'Technician C', '0.5 days', 'Hydraulic fluid change + filter replacement'),
        ('MCH-002', '2025-11-20', 'planned', 'Technician B', '1.0 days', 'Quarterly PM — lubrication, tool changer inspection'),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO maintenance_history (
            machine_id, date, type, technician, duration, notes
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, history)
    print(f"  [OK] {len(history)} maintenance records inserted")


def migrate_production_lines(cursor):
    """Migrate production lines."""
    lines = [
        ('Line 1', 'Assembly Line 1', 'PROD-A', 55, 'operational', 0.92, 'MCH-001', 0.92, 0.008, 45),
        ('Line 2', 'CNC Machining Line 2', 'PROD-A', 60, 'operational', 0.75, 'MCH-002', 0.75, 0.021, 60),
        ('Line 3', 'Hydraulic Press Line 3', 'PROD-A', 50, 'operational', 0.88, 'MCH-003', 0.88, 0.016, 50),
        ('Line 4', 'Conveyor Line 4', None, 45, 'down', 0.0, 'MCH-004', 0.0, 0.0, 0),
        ('Line 5', 'Welding Line 5', 'PROD-A', 58, 'operational', 0.96, 'MCH-005', 0.96, 0.004, 40),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO production_lines (
            id, name, current_product_id, capacity_per_hour, status, utilization,
            bottleneck_machine_id, efficiency, scrap_rate, changeover_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, lines)
    print(f"  [OK] {len(lines)} production lines inserted")


def migrate_shift_config(cursor):
    """Migrate shift configuration."""
    cursor.execute("""
        INSERT OR REPLACE INTO shift_config (
            shifts_per_day, hours_per_shift, days_per_week,
            overtime_available, max_overtime_hours, shift_names
        ) VALUES (2, 8, 5, 1, 4, 'Day Shift,Night Shift')
    """)
    print("  [OK] 1 shift configuration inserted")


def migrate_bom(cursor):
    """Migrate Bill of Materials."""
    components = [
        ('BOM-001', 'PROD-A', 'SH-100', 'Steel Housing', 1, 2100, 'SUP-A', 25.00),
        ('BOM-002', 'PROD-A', 'VSA-200', 'Valve Seat Assembly', 1, 1650, 'SUP-B', 14.00),
        ('BOM-003', 'PROD-A', 'AM-300', 'Actuator Motor', 1, 1900, 'SUP-A', 8.50),
        ('BOM-004', 'PROD-A', 'SOR-400', 'Seals & O-rings Kit', 1, 3200, 'SUP-A', 2.50),
        ('BOM-005', 'PROD-A', 'FS-500', 'Fastener Set', 1, 4100, 'SUP-A', 1.50),
        ('BOM-006', 'PROD-A', 'IL-600', 'Inspection Labels & Packaging', 1, 5000, 'SUP-A', 0.50),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO bom_items (
            id, product_id, component_id, component_name, quantity,
            stock, supplier_id, cost
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, components)
    print(f"  [OK] {len(components)} BOM items inserted")


def migrate_production_schedule(cursor):
    """Migrate production schedule (8 weeks history)."""
    schedule = [
        ('PROD-A', 46, '2025-11-10', 1050, 1050, 1048, 1050, -2, 0),
        ('PROD-A', 47, '2025-11-17', 1050, 1050, 1035, 1050, -15, 2),
        ('PROD-A', 48, '2025-11-24', 1050, 1050, 1050, 1050, 0, 0),
        ('PROD-A', 49, '2025-12-01', 1050, 1050, 972, 1050, -78, 8),
        ('PROD-A', 50, '2025-12-08', 1050, 1050, 1044, 1050, -6, 4),
        ('PROD-A', 3, '2026-01-13', 1050, 1050, 1038, 1050, -12, 2),
        ('PROD-A', 6, '2026-02-03', 1050, 945, 987, 1050, -63, 12),
        ('PROD-A', 7, '2026-02-10', 1050, 945, None, 980, None, None),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO production_schedule (
            product_id, week_number, week_start_date, demand,
            planned_production, actual_production, capacity, gap, overtime_hours
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, schedule)
    print(f"  [OK] {len(schedule)} production schedule records inserted")


def print_migration_summary(cursor):
    """Print summary of all migrated data."""
    tables = [
        'products', 'inventory', 'warehouse_zones', 'stockout_events',
        'suppliers', 'supplier_contracts', 'supplier_risk', 'purchase_orders',
        'machines', 'sensor_readings', 'maintenance_history',
        'production_lines', 'shift_config', 'bom_items', 'production_schedule',
        'historical_demand_data', 'market_context_data'
    ]

    print("\n" + "=" * 60)
    print("DATABASE SUMMARY")
    print("=" * 60)

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table:30} {count:5} records")

    print("=" * 60)


if __name__ == "__main__":
    migrate_all_data()
