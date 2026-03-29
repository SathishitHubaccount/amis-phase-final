"""
AMIS Data Migration Script
Migrate mock data from JavaScript mockData.js to SQLite database
"""
from database import get_db_connection, init_database, get_database_stats

# Mock data defined directly in Python (converted from mockData.js)
PRODUCTS = {
    'PROD-A': {
        'id': 'PROD-A',
        'name': 'Automotive Sensor Unit',
        'category': 'Electronics',
        'status': 'active',
        'inventory': {
            'currentStock': 1850,
            'safetyStock': 500,
            'reorderPoint': 800,
            'avgDailyUsage': 120,
            'leadTime': 7,
            'stockoutRisk': 18,
        },
        'bom': [
            {'id': 'PCB-001', 'name': 'Main Circuit Board', 'quantity': 1, 'stock': 2400, 'supplier': 'SUP-001', 'cost': 12.50},
            {'id': 'SEN-002', 'name': 'Temperature Sensor', 'quantity': 2, 'stock': 4200, 'supplier': 'SUP-003', 'cost': 3.20},
            {'id': 'RES-003', 'name': 'Resistor Pack (10pc)', 'quantity': 1, 'stock': 15000, 'supplier': 'SUP-001', 'cost': 0.85},
            {'id': 'CAP-004', 'name': 'Capacitor Set', 'quantity': 1, 'stock': 8900, 'supplier': 'SUP-001', 'cost': 1.40},
            {'id': 'CASE-005', 'name': 'Plastic Housing', 'quantity': 1, 'stock': 1200, 'supplier': 'SUP-002', 'cost': 2.80},
        ],
    },
    'PROD-B': {
        'id': 'PROD-B',
        'name': 'Industrial Motor Assembly',
        'category': 'Mechanical',
        'status': 'active',
        'inventory': {
            'currentStock': 450,
            'safetyStock': 150,
            'reorderPoint': 250,
            'avgDailyUsage': 35,
            'leadTime': 14,
            'stockoutRisk': 12,
        },
        'bom': [
            {'id': 'MOT-101', 'name': 'AC Motor 5HP', 'quantity': 1, 'stock': 520, 'supplier': 'SUP-003', 'cost': 245.00},
            {'id': 'BEAR-102', 'name': 'Ball Bearing Set', 'quantity': 4, 'stock': 2800, 'supplier': 'SUP-001', 'cost': 18.50},
            {'id': 'SHAFT-103', 'name': 'Steel Shaft', 'quantity': 1, 'stock': 680, 'supplier': 'SUP-004', 'cost': 32.00},
            {'id': 'HOUS-104', 'name': 'Aluminum Housing', 'quantity': 1, 'stock': 420, 'supplier': 'SUP-002', 'cost': 68.00},
        ],
    },
    'PROD-C': {
        'id': 'PROD-C',
        'name': 'Smart Thermostat',
        'category': 'Electronics',
        'status': 'active',
        'inventory': {
            'currentStock': 3200,
            'safetyStock': 800,
            'reorderPoint': 1200,
            'avgDailyUsage': 180,
            'leadTime': 10,
            'stockoutRisk': 8,
        },
        'bom': [
            {'id': 'DISP-201', 'name': 'LCD Display', 'quantity': 1, 'stock': 3800, 'supplier': 'SUP-001', 'cost': 8.90},
            {'id': 'PCB-202', 'name': 'Control Board', 'quantity': 1, 'stock': 3500, 'supplier': 'SUP-001', 'cost': 15.20},
            {'id': 'WIFI-203', 'name': 'WiFi Module', 'quantity': 1, 'stock': 4200, 'supplier': 'SUP-003', 'cost': 6.50},
            {'id': 'CASE-204', 'name': 'Front Panel', 'quantity': 1, 'stock': 2900, 'supplier': 'SUP-002', 'cost': 4.20},
        ],
    },
    'PROD-D': {
        'id': 'PROD-D',
        'name': 'Hydraulic Pump',
        'category': 'Mechanical',
        'status': 'active',
        'inventory': {
            'currentStock': 280,
            'safetyStock': 100,
            'reorderPoint': 150,
            'avgDailyUsage': 22,
            'leadTime': 21,
            'stockoutRisk': 25,
        },
        'bom': [
            {'id': 'PUMP-301', 'name': 'Pump Body (Cast Iron)', 'quantity': 1, 'stock': 320, 'supplier': 'SUP-004', 'cost': 185.00},
            {'id': 'SEAL-302', 'name': 'Hydraulic Seal Kit', 'quantity': 1, 'stock': 580, 'supplier': 'SUP-003', 'cost': 28.50},
            {'id': 'VAL-303', 'name': 'Pressure Valve', 'quantity': 2, 'stock': 840, 'supplier': 'SUP-001', 'cost': 42.00},
            {'id': 'HOSE-304', 'name': 'Hydraulic Hose Assembly', 'quantity': 2, 'stock': 650, 'supplier': 'SUP-002', 'cost': 15.80},
        ],
    },
    'PROD-E': {
        'id': 'PROD-E',
        'name': 'LED Display Panel',
        'category': 'Electronics',
        'status': 'limited',
        'inventory': {
            'currentStock': 95,
            'safetyStock': 50,
            'reorderPoint': 80,
            'avgDailyUsage': 12,
            'leadTime': 45,
            'stockoutRisk': 42,
        },
        'bom': [
            {'id': 'LED-401', 'name': 'LED Matrix Array', 'quantity': 1, 'stock': 120, 'supplier': 'SUP-003', 'cost': 95.00},
            {'id': 'DRV-402', 'name': 'LED Driver IC', 'quantity': 4, 'stock': 580, 'supplier': 'SUP-001', 'cost': 12.30},
            {'id': 'FRAME-403', 'name': 'Aluminum Frame', 'quantity': 1, 'stock': 88, 'supplier': 'SUP-002', 'cost': 42.00},
            {'id': 'PWR-404', 'name': 'Power Supply Unit', 'quantity': 1, 'stock': 150, 'supplier': 'SUP-001', 'cost': 38.50},
        ],
    },
}

MACHINES_BY_PRODUCT = {
    'PROD-A': ['MCH-001', 'MCH-002', 'MCH-005'],
    'PROD-B': ['MCH-003'],
    'PROD-C': ['MCH-001', 'MCH-005'],
    'PROD-D': ['MCH-004'],
    'PROD-E': ['MCH-002', 'MCH-003'],
}

MACHINES = {
    'MCH-001': {
        'id': 'MCH-001', 'name': 'Stamping Press A', 'type': 'Stamping', 'line': 'Line 1',
        'status': 'healthy', 'oee': 87, 'availability': 92, 'performance': 95, 'quality': 100,
        'failureRisk': 8, 'lastMaintenance': '2026-01-15', 'nextMaintenance': '2026-03-15',
        'productionCapacity': 50, 'currentUtilization': 94,
        'alarms': [{'id': 1, 'time': '2026-02-27 14:22', 'severity': 'low', 'message': 'Oil pressure slightly below optimal'}],
        'maintenanceHistory': [
            {'date': '2026-01-15', 'type': 'Preventive', 'technician': 'John Smith', 'duration': '2h', 'notes': 'Replaced hydraulic fluid'},
            {'date': '2025-12-10', 'type': 'Corrective', 'technician': 'Maria Garcia', 'duration': '4h', 'notes': 'Fixed sensor calibration'},
        ],
        'spareParts': [
            {'part': 'Hydraulic Seal', 'stock': 5, 'minStock': 2, 'status': 'OK'},
            {'part': 'Pressure Sensor', 'stock': 1, 'minStock': 2, 'status': 'LOW'},
        ],
    },
    'MCH-002': {
        'id': 'MCH-002', 'name': 'Assembly Robot B', 'type': 'Robotic Assembly', 'line': 'Line 2',
        'status': 'at_risk', 'oee': 64, 'availability': 78, 'performance': 85, 'quality': 96,
        'failureRisk': 47, 'lastMaintenance': '2025-11-20', 'nextMaintenance': '2026-02-28',
        'productionCapacity': 45, 'currentUtilization': 78,
        'alarms': [
            {'id': 2, 'time': '2026-02-28 09:15', 'severity': 'high', 'message': 'Gripper actuator showing increased cycle time'},
            {'id': 3, 'time': '2026-02-27 16:40', 'severity': 'medium', 'message': 'Vision system alignment drift detected'},
        ],
        'maintenanceHistory': [
            {'date': '2025-11-20', 'type': 'Preventive', 'technician': 'David Lee', 'duration': '3h', 'notes': 'Lubrication and calibration'},
        ],
        'spareParts': [
            {'part': 'Gripper Assembly', 'stock': 0, 'minStock': 1, 'status': 'CRITICAL'},
            {'part': 'Vision Camera', 'stock': 2, 'minStock': 1, 'status': 'OK'},
        ],
    },
    'MCH-003': {
        'id': 'MCH-003', 'name': 'Quality Scanner C', 'type': 'Inspection', 'line': 'Line 3',
        'status': 'healthy', 'oee': 91, 'availability': 96, 'performance': 95, 'quality': 100,
        'failureRisk': 12, 'lastMaintenance': '2026-02-01', 'nextMaintenance': '2026-04-01',
        'productionCapacity': 60, 'currentUtilization': 88,
        'alarms': [],
        'maintenanceHistory': [
            {'date': '2026-02-01', 'type': 'Preventive', 'technician': 'Sarah Johnson', 'duration': '1h', 'notes': 'Lens cleaning and calibration check'},
        ],
        'spareParts': [
            {'part': 'Scanner Lens', 'stock': 3, 'minStock': 2, 'status': 'OK'},
            {'part': 'Light Source', 'stock': 4, 'minStock': 2, 'status': 'OK'},
        ],
    },
    'MCH-004': {
        'id': 'MCH-004', 'name': 'Welding Station D', 'type': 'Welding', 'line': 'Maintenance',
        'status': 'critical', 'oee': 45, 'availability': 50, 'performance': 90, 'quality': 100,
        'failureRisk': 78, 'lastMaintenance': '2026-02-20', 'nextMaintenance': '2026-02-23',
        'productionCapacity': 40, 'currentUtilization': 0,
        'alarms': [
            {'id': 4, 'time': '2026-02-20 11:00', 'severity': 'critical', 'message': 'Welding transformer failure - machine down'},
        ],
        'maintenanceHistory': [
            {'date': '2026-02-20', 'type': 'Breakdown', 'technician': 'Robert Chen', 'duration': 'Ongoing', 'notes': 'Waiting for transformer replacement part'},
        ],
        'spareParts': [
            {'part': 'Welding Transformer', 'stock': 0, 'minStock': 1, 'status': 'CRITICAL'},
            {'part': 'Welding Tips', 'stock': 15, 'minStock': 10, 'status': 'OK'},
        ],
    },
    'MCH-005': {
        'id': 'MCH-005', 'name': 'Packaging Unit E', 'type': 'Packaging', 'line': 'Line 5',
        'status': 'healthy', 'oee': 83, 'availability': 88, 'performance': 94, 'quality': 100,
        'failureRisk': 6, 'lastMaintenance': '2026-02-10', 'nextMaintenance': '2026-03-10',
        'productionCapacity': 55, 'currentUtilization': 0,
        'alarms': [],
        'maintenanceHistory': [
            {'date': '2026-02-10', 'type': 'Preventive', 'technician': 'Emily Brown', 'duration': '2h', 'notes': 'Belt tension adjustment and sensor check'},
        ],
        'spareParts': [
            {'part': 'Conveyor Belt', 'stock': 2, 'minStock': 1, 'status': 'OK'},
            {'part': 'Proximity Sensor', 'stock': 8, 'minStock': 5, 'status': 'OK'},
        ],
    },
}

SUPPLIERS = {
    'SUP-001': {
        'id': 'SUP-001', 'name': 'Global Parts Co.', 'location': 'Detroit, USA',
        'score': 92, 'rating': 'A', 'onTimeDelivery': 96, 'quality': 98, 'costIndex': 102,
        'baseCost': 51.20, 'leadTime': 7, 'leadTimeVariability': 1, 'risk': 'Low',
        'moq': 1000, 'paymentTerms': 'Net 30', 'currency': 'USD',
        'certifications': ['ISO-9001', 'IATF-16949', 'ISO-14001'],
        'contracts': [
            {'id': 'CNT-2025-001', 'startDate': '2025-01-01', 'endDate': '2026-12-31', 'volume': 50000, 'status': 'active'},
        ],
        'incidents': [
            {'date': '2025-08-15', 'type': 'Quality', 'severity': 'low', 'resolution': 'Replaced defective batch'},
        ],
    },
    'SUP-002': {
        'id': 'SUP-002', 'name': 'Precision Manufacturing Ltd.', 'location': 'Toronto, Canada',
        'score': 78, 'rating': 'B', 'onTimeDelivery': 82, 'quality': 91, 'costIndex': 96,
        'baseCost': 48.30, 'leadTime': 10, 'leadTimeVariability': 3, 'risk': 'Medium',
        'moq': 500, 'paymentTerms': 'Net 45', 'currency': 'CAD',
        'certifications': ['ISO-9001'],
        'contracts': [
            {'id': 'CNT-2024-008', 'startDate': '2024-06-01', 'endDate': '2026-05-31', 'volume': 25000, 'status': 'active'},
        ],
        'incidents': [
            {'date': '2026-02-25', 'type': 'Delivery', 'severity': 'medium', 'resolution': 'PO-2026-002 delayed 3 days'},
            {'date': '2025-11-10', 'type': 'Quality', 'severity': 'medium', 'resolution': '5% batch rejected'},
        ],
    },
    'SUP-003': {
        'id': 'SUP-003', 'name': 'Eastern Components Inc.', 'location': 'Shenzhen, China',
        'score': 85, 'rating': 'B+', 'onTimeDelivery': 88, 'quality': 94, 'costIndex': 89,
        'baseCost': 49.80, 'leadTime': 12, 'leadTimeVariability': 4, 'risk': 'Low',
        'moq': 2000, 'paymentTerms': 'LC at Sight', 'currency': 'CNY',
        'certifications': ['ISO-9001', 'ISO-14001', 'RoHS'],
        'contracts': [
            {'id': 'CNT-2025-015', 'startDate': '2025-03-01', 'endDate': '2027-02-28', 'volume': 75000, 'status': 'active'},
        ],
        'incidents': [],
    },
    'SUP-004': {
        'id': 'SUP-004', 'name': 'Quality Supplies LLC', 'location': 'Mexico City, Mexico',
        'score': 68, 'rating': 'C+', 'onTimeDelivery': 74, 'quality': 85, 'costIndex': 84,
        'baseCost': 45.00, 'leadTime': 14, 'leadTimeVariability': 6, 'risk': 'High',
        'moq': 500, 'paymentTerms': 'Net 60', 'currency': 'MXN',
        'certifications': ['ISO-9001'],
        'contracts': [
            {'id': 'CNT-2023-042', 'startDate': '2023-09-01', 'endDate': '2026-08-31', 'volume': 15000, 'status': 'review'},
        ],
        'incidents': [
            {'date': '2026-01-20', 'type': 'Delivery', 'severity': 'high', 'resolution': 'Shipment delayed 7 days'},
            {'date': '2025-10-05', 'type': 'Quality', 'severity': 'high', 'resolution': '12% batch rejected'},
            {'date': '2025-07-12', 'type': 'Delivery', 'severity': 'medium', 'resolution': 'Partial shipment only'},
        ],
    },
}

def migrate_products():
    """Migrate products and inventory"""
    conn = get_db_connection()
    cursor = conn.cursor()

    print("Migrating products...")
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
            product_id, inv['currentStock'], inv['safetyStock'], inv['reorderPoint'],
            inv['avgDailyUsage'], inv['leadTime'], inv['stockoutRisk']
        ))

        # Insert BOM items
        for bom_item in data['bom']:
            cursor.execute("""
                INSERT OR REPLACE INTO bom_items
                (id, product_id, component_id, component_name, quantity, stock, supplier_id, cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bom_item['id'], product_id, bom_item['id'], bom_item['name'],
                bom_item['quantity'], bom_item['stock'], bom_item['supplier'], bom_item['cost']
            ))

        print(f"  [OK] {product_id}: {data['name']}")

    conn.commit()
    conn.close()

def migrate_machines():
    """Migrate machines with alarms, maintenance history, and spare parts"""
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\nMigrating machines...")
    for machine_id, data in MACHINES.items():
        # Insert machine
        cursor.execute("""
            INSERT OR REPLACE INTO machines
            (id, name, type, line, status, oee, availability, performance, quality,
             failure_risk, production_capacity, current_utilization,
             last_maintenance, next_maintenance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            machine_id, data['name'], data['type'], data['line'], data['status'],
            data['oee'], data['availability'], data['performance'], data['quality'],
            data['failureRisk'], data['productionCapacity'], data['currentUtilization'],
            data['lastMaintenance'], data['nextMaintenance']
        ))

        # Insert alarms
        for alarm in data.get('alarms', []):
            cursor.execute("""
                INSERT OR IGNORE INTO machine_alarms
                (machine_id, time, severity, message)
                VALUES (?, ?, ?, ?)
            """, (machine_id, alarm['time'], alarm['severity'], alarm['message']))

        # Insert maintenance history
        for maint in data.get('maintenanceHistory', []):
            cursor.execute("""
                INSERT OR IGNORE INTO maintenance_history
                (machine_id, date, type, technician, duration, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (machine_id, maint['date'], maint['type'], maint['technician'],
                  maint['duration'], maint['notes']))

        # Insert spare parts
        for part in data.get('spareParts', []):
            cursor.execute("""
                INSERT OR IGNORE INTO spare_parts
                (machine_id, part_name, stock, min_stock, status)
                VALUES (?, ?, ?, ?, ?)
            """, (machine_id, part['part'], part['stock'], part['minStock'], part['status']))

        print(f"  [OK] {machine_id}: {data['name']}")

    conn.commit()
    conn.close()

def migrate_product_machines():
    """Migrate product-machine mappings"""
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\nMigrating product-machine mappings...")
    for product_id, machine_ids in MACHINES_BY_PRODUCT.items():
        for machine_id in machine_ids:
            cursor.execute("""
                INSERT OR REPLACE INTO product_machines (product_id, machine_id)
                VALUES (?, ?)
            """, (product_id, machine_id))
        print(f"  [OK] {product_id}: {len(machine_ids)} machines")

    conn.commit()
    conn.close()

def migrate_suppliers():
    """Migrate suppliers with certifications, contracts, and incidents"""
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\nMigrating suppliers...")
    for supplier_id, data in SUPPLIERS.items():
        # Insert supplier
        cursor.execute("""
            INSERT OR REPLACE INTO suppliers
            (id, name, location, score, rating, on_time_delivery, quality_score,
             cost_index, base_cost, lead_time, lead_time_variability, risk,
             moq, payment_terms, currency)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            supplier_id, data['name'], data['location'], data['score'], data['rating'],
            data['onTimeDelivery'], data['quality'], data['costIndex'], data['baseCost'],
            data['leadTime'], data['leadTimeVariability'], data['risk'],
            data['moq'], data['paymentTerms'], data['currency']
        ))

        # Insert certifications
        for cert in data.get('certifications', []):
            cursor.execute("""
                INSERT OR IGNORE INTO supplier_certifications (supplier_id, certification)
                VALUES (?, ?)
            """, (supplier_id, cert))

        # Insert contracts
        for contract in data.get('contracts', []):
            cursor.execute("""
                INSERT OR REPLACE INTO supplier_contracts
                (id, supplier_id, start_date, end_date, volume, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (contract['id'], supplier_id, contract['startDate'],
                  contract['endDate'], contract['volume'], contract['status']))

        # Insert incidents
        for incident in data.get('incidents', []):
            cursor.execute("""
                INSERT OR IGNORE INTO supplier_incidents
                (supplier_id, date, type, severity, resolution)
                VALUES (?, ?, ?, ?, ?)
            """, (supplier_id, incident['date'], incident['type'],
                  incident['severity'], incident['resolution']))

        print(f"  [OK] {supplier_id}: {data['name']}")

    conn.commit()
    conn.close()

def migrate_all():
    """Run complete migration"""
    print("=" * 60)
    print("AMIS Database Migration")
    print("=" * 60)

    # Initialize database
    print("\nInitializing database schema...")
    init_database()

    # Migrate data
    migrate_products()
    migrate_machines()
    migrate_product_machines()
    migrate_suppliers()

    print("\n" + "=" * 60)
    print("Migration Complete!")
    print("=" * 60)

    # Show stats
    stats = get_database_stats()
    print("\nDatabase Statistics:")
    print(f"  Products: {stats['products']}")
    print(f"  Machines: {stats['machines']}")
    print(f"  Suppliers: {stats['suppliers']}")
    print(f"  Work Orders: {stats['work_orders']}")
    print(f"  Activity Log: {stats['activity_log']}")
    print(f"  Database Size: {stats['database_size_kb']:.2f} KB")
    print()

if __name__ == "__main__":
    migrate_all()
