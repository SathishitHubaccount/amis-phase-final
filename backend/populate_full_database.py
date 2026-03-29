"""
Complete Database Population Script
Populates all tables including production planning and history data
"""

from database import *
from datetime import datetime, timedelta
import random

def generate_production_lines():
    """Generate production lines data"""
    print("\nPopulating production lines...")

    conn = get_db_connection()
    cursor = conn.cursor()

    lines = [
        {
            'id': 'Line-1',
            'name': 'Line 1',
            'current_product_id': 'PROD-A',
            'capacity_per_hour': 50,
            'status': 'running',
            'utilization': 94.0,
            'bottleneck_machine_id': 'MCH-001'
        },
        {
            'id': 'Line-2',
            'name': 'Line 2',
            'current_product_id': 'PROD-A',
            'capacity_per_hour': 45,
            'status': 'running',
            'utilization': 78.0,
            'bottleneck_machine_id': 'MCH-002'
        },
        {
            'id': 'Line-3',
            'name': 'Line 3',
            'current_product_id': 'PROD-B',
            'capacity_per_hour': 60,
            'status': 'running',
            'utilization': 88.0,
            'bottleneck_machine_id': None
        },
        {
            'id': 'Line-4',
            'name': 'Line 4',
            'current_product_id': 'PROD-C',
            'capacity_per_hour': 40,
            'status': 'running',
            'utilization': 65.0,
            'bottleneck_machine_id': None
        },
        {
            'id': 'Line-5',
            'name': 'Line 5',
            'current_product_id': 'PROD-A',
            'capacity_per_hour': 55,
            'status': 'maintenance',
            'utilization': 0.0,
            'bottleneck_machine_id': 'MCH-004'
        }
    ]

    for line in lines:
        cursor.execute("""
            INSERT OR REPLACE INTO production_lines
            (id, name, current_product_id, capacity_per_hour, status, utilization, bottleneck_machine_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            line['id'], line['name'], line['current_product_id'],
            line['capacity_per_hour'], line['status'], line['utilization'],
            line['bottleneck_machine_id']
        ))
        print(f"  [OK] {line['name']}: {line['status']} - {line['utilization']}% utilization")

    conn.commit()
    conn.close()

def generate_production_schedule():
    """Generate 4-week production schedule for each product"""
    print("\nPopulating production schedule...")

    conn = get_db_connection()
    cursor = conn.cursor()

    products = get_all_products()
    today = datetime.now()

    # Schedule data for each product
    schedules = {
        'PROD-A': [
            {'demand': 1850, 'planned': 1650, 'capacity': 1890, 'overtime': 0},
            {'demand': 2100, 'planned': 1890, 'capacity': 1890, 'overtime': 14},
            {'demand': 1950, 'planned': 1850, 'capacity': 1890, 'overtime': 0},
            {'demand': 2200, 'planned': 1890, 'capacity': 1890, 'overtime': 20}
        ],
        'PROD-B': [
            {'demand': 3200, 'planned': 3100, 'capacity': 3600, 'overtime': 0},
            {'demand': 3400, 'planned': 3400, 'capacity': 3600, 'overtime': 0},
            {'demand': 3300, 'planned': 3300, 'capacity': 3600, 'overtime': 0},
            {'demand': 3500, 'planned': 3500, 'capacity': 3600, 'overtime': 0}
        ],
        'PROD-C': [
            {'demand': 1100, 'planned': 1050, 'capacity': 1200, 'overtime': 0},
            {'demand': 1150, 'planned': 1150, 'capacity': 1200, 'overtime': 0},
            {'demand': 1200, 'planned': 1200, 'capacity': 1200, 'overtime': 0},
            {'demand': 1250, 'planned': 1200, 'capacity': 1200, 'overtime': 8}
        ],
        'PROD-D': [
            {'demand': 800, 'planned': 750, 'capacity': 900, 'overtime': 0},
            {'demand': 850, 'planned': 850, 'capacity': 900, 'overtime': 0},
            {'demand': 820, 'planned': 820, 'capacity': 900, 'overtime': 0},
            {'demand': 900, 'planned': 900, 'capacity': 900, 'overtime': 0}
        ],
        'PROD-E': [
            {'demand': 600, 'planned': 550, 'capacity': 650, 'overtime': 0},
            {'demand': 620, 'planned': 620, 'capacity': 650, 'overtime': 0},
            {'demand': 640, 'planned': 640, 'capacity': 650, 'overtime': 0},
            {'demand': 680, 'planned': 650, 'capacity': 650, 'overtime': 5}
        ]
    }

    for product in products:
        product_id = product['id']
        if product_id not in schedules:
            continue

        schedule_data = schedules[product_id]

        for week_num, week_data in enumerate(schedule_data, 1):
            week_start = today + timedelta(days=(week_num - 1) * 7)
            gap = week_data['demand'] - week_data['planned']

            cursor.execute("""
                INSERT INTO production_schedule
                (product_id, week_number, week_start_date, demand, planned_production,
                 capacity, gap, overtime_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id, week_num, week_start.strftime('%Y-%m-%d'),
                week_data['demand'], week_data['planned'], week_data['capacity'],
                gap, week_data['overtime']
            ))

        print(f"  [OK] {product_id}: 4-week schedule created")

    conn.commit()
    conn.close()

def generate_inventory_history():
    """Generate 30 days of inventory history for trend charts"""
    print("\nPopulating inventory history...")

    conn = get_db_connection()
    cursor = conn.cursor()

    products = get_all_products()

    for product in products:
        product_id = product['id']
        inventory = get_inventory(product_id)

        if not inventory:
            continue

        current_stock = inventory['current_stock']
        avg_usage = inventory.get('avg_daily_usage', 100)

        # Generate 30 days of history with some variation
        for days_ago in range(30, 0, -1):
            date = datetime.now() - timedelta(days=days_ago)

            # Simulate stock changes (declining trend with some fluctuation)
            variation = random.randint(-50, 100)
            historical_stock = current_stock + (days_ago * avg_usage // 3) + variation
            historical_stock = max(historical_stock, 500)  # Minimum stock

            # Calculate historical stockout risk
            days_supply = historical_stock / avg_usage if avg_usage > 0 else 0
            if days_supply > 20:
                risk = random.uniform(5, 10)
            elif days_supply > 10:
                risk = random.uniform(10, 20)
            else:
                risk = random.uniform(20, 40)

            cursor.execute("""
                INSERT INTO inventory_history
                (product_id, date, stock_level, stockout_risk, days_supply)
                VALUES (?, ?, ?, ?, ?)
            """, (
                product_id,
                date.strftime('%Y-%m-%d'),
                historical_stock,
                risk,
                days_supply
            ))

        print(f"  [OK] {product_id}: 30-day history created")

    conn.commit()
    conn.close()

def generate_machine_oee_history():
    """Generate 30 days of machine OEE history for trend charts"""
    print("\nPopulating machine OEE history...")

    conn = get_db_connection()
    cursor = conn.cursor()

    machines = get_all_machines()

    for machine in machines:
        machine_id = machine['id']
        current_oee = machine.get('oee', 85)

        # Generate 30 days of history with trends
        for days_ago in range(30, 0, -1):
            date = datetime.now() - timedelta(days=days_ago)

            # Simulate OEE trend (slight improvement or degradation)
            trend = random.uniform(-2, 3)
            historical_oee = current_oee + (trend * days_ago / 30)
            historical_oee = max(min(historical_oee, 100), 50)  # Clamp between 50-100

            # Generate component metrics
            availability = historical_oee + random.uniform(0, 10)
            availability = min(availability, 100)

            performance = historical_oee + random.uniform(-5, 5)
            performance = max(min(performance, 100), 50)

            quality = random.uniform(95, 100)

            cursor.execute("""
                INSERT INTO machine_oee_history
                (machine_id, date, oee, availability, performance, quality)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                machine_id,
                date.strftime('%Y-%m-%d'),
                round(historical_oee, 1),
                round(availability, 1),
                round(performance, 1),
                round(quality, 1)
            ))

        print(f"  [OK] {machine_id}: 30-day OEE history created")

    conn.commit()
    conn.close()

def main():
    """Main population function"""
    print("="*60)
    print("AMIS COMPLETE DATABASE POPULATION")
    print("="*60)

    # Ensure database is initialized
    init_database()

    # Generate production planning data
    generate_production_lines()
    generate_production_schedule()

    # Generate historical data for charts
    generate_inventory_history()
    generate_machine_oee_history()

    # Print stats
    stats = get_database_stats()
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("="*60)
    print("\n[SUCCESS] Database fully populated!")
    print("\nYou can now:")
    print("  1. View production planning with real data")
    print("  2. See 30-day inventory trends")
    print("  3. See 30-day machine OEE trends")
    print("  4. Use all features with complete data")

if __name__ == "__main__":
    main()
