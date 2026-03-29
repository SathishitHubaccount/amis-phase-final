"""Check what's actually in the database"""
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

print("=== DEMAND FORECASTS TABLE ===")
cursor.execute('SELECT * FROM demand_forecasts LIMIT 5')
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"  Week {row['week_number']}: Base={row['base_case']}, Optimistic={row['optimistic']}, Pessimistic={row['pessimistic']}")
else:
    print("  (Empty - No forecasts yet)")

print("\n=== INVENTORY TABLE (PROD-A) ===")
cursor.execute('SELECT * FROM inventory WHERE product_id="PROD-A"')
row = cursor.fetchone()
if row:
    print(f"  Current Stock: {row['current_stock']}")
    print(f"  Safety Stock: {row['safety_stock']}")
    print(f"  Reorder Point: {row['reorder_point']}")
    print(f"  Stockout Risk: {row['stockout_risk']}%")
else:
    print("  (No inventory data)")

print("\n=== PRODUCTION SCHEDULE (PROD-A) ===")
cursor.execute('SELECT * FROM production_schedule WHERE product_id="PROD-A" LIMIT 4')
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"  Week {row['week_number']}: Demand={row['demand']}, Planned={row['planned_production']}, Gap={row['gap']}")
else:
    print("  (No production schedule)")

print("\n=== MACHINES TABLE ===")
cursor.execute('SELECT id, name, oee, failure_risk, status FROM machines LIMIT 5')
rows = cursor.fetchall()
for row in rows:
    print(f"  {row['id']}: {row['name']} - OEE={row['oee']}%, Risk={row['failure_risk']}%, Status={row['status']}")

conn.close()
