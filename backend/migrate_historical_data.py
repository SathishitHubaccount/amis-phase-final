"""
Migration Script: Populate Historical Demand Data
==================================================
This script populates the database with 52 weeks of historical demand data
for all products. This data becomes the INPUT for the AI Demand Forecasting Agent.

Run this ONCE to initialize the historical data.
After running, the data is persistent and can be queried with SQL.
"""
import sqlite3
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

# Database path
DATABASE_PATH = Path(__file__).parent / "amis.db"


def populate_historical_demand_data():
    """
    Generate and store 52 weeks of historical demand data for 3 products.
    Uses the same algorithm as sample_data.py but stores results in database.
    """
    print("\n" + "=" * 70)
    print("MIGRATING HISTORICAL DEMAND DATA TO DATABASE")
    print("=" * 70)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # First, create tables if they don't exist (idempotent)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historical_demand_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            week_start_date DATE NOT NULL,
            week_number INTEGER NOT NULL,
            year INTEGER NOT NULL,
            demand_units INTEGER NOT NULL,
            avg_price REAL,
            promotions_active BOOLEAN DEFAULT 0,
            competitor_price REAL,
            is_anomaly BOOLEAN DEFAULT 0,
            anomaly_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            UNIQUE(product_id, week_start_date)
        )
    """)

    # Products to generate data for
    products = [
        {"id": "PROD-A", "base_demand": 950, "base_price": 89.99},
        {"id": "PROD-B", "base_demand": 720, "base_price": 149.99},
        {"id": "PROD-C", "base_demand": 1150, "base_price": 59.99},
    ]

    records_created = 0

    for product in products:
        product_id = product["id"]
        base_demand = product["base_demand"]
        base_price = product["base_price"]

        print(f"\n[PRODUCT] Generating 52 weeks of data for {product_id}...")

        # Generate 52 weeks of historical data (going backwards from today)
        for i in range(52, 0, -1):
            # Calculate week start date (going backwards)
            week_start_date = datetime.now() - timedelta(weeks=i)
            week_start_date = week_start_date.replace(hour=0, minute=0, second=0, microsecond=0)

            # Calculate week number (1-52) and year
            week_number = week_start_date.isocalendar()[1]
            year = week_start_date.year

            # Calculate demand using same formula as sample_data.py
            # 1. Trend component (gradual growth over time)
            trend = 15  # units increase per week
            weeks_since_start = 52 - i
            trend_value = trend * weeks_since_start

            # 2. Seasonal component (repeats every 52 weeks)
            seasonal_amplitude = 120
            seasonal_phase = (weeks_since_start / 52.0) * 2 * math.pi
            seasonal = seasonal_amplitude * math.sin(seasonal_phase)

            # 3. Random noise
            noise_std = 60
            noise = random.gauss(0, noise_std)

            # 4. Anomalies (spikes in specific weeks)
            is_anomaly = False
            anomaly_reason = None
            anomaly = 0

            # Week 48 (4 weeks ago) - viral social media spike
            if i == 4:
                anomaly = 450
                is_anomaly = True
                anomaly_reason = "Viral social media campaign spike"

            # Week 39 (13 weeks ago) - supply chain disruption
            elif i == 13:
                anomaly = -280
                is_anomaly = True
                anomaly_reason = "Competitor supply chain disruption (demand shifted to us)"

            # Week 26 (26 weeks ago) - promotional campaign
            elif i == 26:
                anomaly = 320
                is_anomaly = True
                anomaly_reason = "Black Friday promotional campaign"

            # Calculate final demand (ensure non-negative)
            demand_units = max(0, int(base_demand + trend_value + seasonal + noise + anomaly))

            # Price variations
            price_volatility = 5.0
            avg_price = base_price + random.uniform(-price_volatility, price_volatility)
            competitor_price = base_price * 1.15 + random.uniform(-8, 8)

            # Promotions (20% of weeks have promotions)
            promotions_active = random.random() < 0.20

            # Insert into database
            cursor.execute("""
                INSERT OR REPLACE INTO historical_demand_data
                (product_id, week_start_date, week_number, year, demand_units,
                 avg_price, promotions_active, competitor_price, is_anomaly, anomaly_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                week_start_date.date(),
                week_number,
                year,
                demand_units,
                round(avg_price, 2),
                1 if promotions_active else 0,
                round(competitor_price, 2),
                1 if is_anomaly else 0,
                anomaly_reason
            ))

            records_created += 1

            # Print progress for anomalies
            if is_anomaly:
                print(f"   [ANOMALY] Week {weeks_since_start + 1}: {anomaly_reason} (demand: {demand_units})")

    conn.commit()

    print(f"\n[SUCCESS] Created {records_created} historical demand records")
    print(f"   (52 weeks x {len(products)} products)")

    # Verify data
    cursor.execute("SELECT COUNT(*) FROM historical_demand_data")
    total = cursor.fetchone()[0]
    print(f"\n[DATABASE] Database now contains {total} historical demand records")

    conn.close()


def populate_market_context_data():
    """
    Generate and store market context data.
    This provides macroeconomic and market conditions for the AI to consider.
    """
    print("\n" + "=" * 70)
    print("MIGRATING MARKET CONTEXT DATA TO DATABASE")
    print("=" * 70)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create table if doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_context_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_recorded DATE NOT NULL UNIQUE,
            industry_growth_rate REAL,
            economic_indicator TEXT,
            competitor_activity TEXT,
            raw_material_price_trend TEXT,
            trade_show_date DATE,
            major_client_contract_renewal_date DATE,
            seasonal_pattern TEXT,
            market_sentiment TEXT,
            supply_chain_status TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert current market context
    today = datetime.now().date()
    trade_show_date = today + timedelta(days=21)  # 3 weeks from now
    contract_renewal = today + timedelta(days=14)  # 2 weeks from now

    cursor.execute("""
        INSERT OR REPLACE INTO market_context_data
        (date_recorded, industry_growth_rate, economic_indicator, competitor_activity,
         raw_material_price_trend, trade_show_date, major_client_contract_renewal_date,
         seasonal_pattern, market_sentiment, supply_chain_status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        today,
        7.2,  # 7.2% industry growth
        "Manufacturing PMI at 52.3 (expansion)",
        "Competitor launched new product targeting enterprise market",
        "Raw material costs up 4% YoY due to supply chain constraints",
        trade_show_date,
        contract_renewal,
        "Q1 typically sees 15% higher demand (industrial buying cycle)",
        "Positive - Economic recovery driving capital investments",
        "Stable with minor delays in Asian shipping routes",
        "Current market conditions as of database initialization"
    ))

    conn.commit()
    print(f"[SUCCESS] Market context data created for {today}")

    conn.close()


def verify_migration():
    """
    Verify that migration was successful by running validation queries.
    """
    print("\n" + "=" * 70)
    print("VERIFYING MIGRATION")
    print("=" * 70)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check 1: Count records per product
    print("\n[STATS] Records per product:")
    cursor.execute("""
        SELECT product_id, COUNT(*) as week_count
        FROM historical_demand_data
        GROUP BY product_id
        ORDER BY product_id
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} weeks")

    # Check 2: Show recent 5 weeks for PROD-A
    print("\n[RECENT] Most recent 5 weeks for PROD-A:")
    cursor.execute("""
        SELECT week_start_date, demand_units, is_anomaly, anomaly_reason
        FROM historical_demand_data
        WHERE product_id = 'PROD-A'
        ORDER BY week_start_date DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        anomaly_flag = "[!] " if row[2] else "    "
        reason = f" ({row[3]})" if row[3] else ""
        print(f"   {anomaly_flag}{row[0]}: {row[1]} units{reason}")

    # Check 3: Calculate average demand
    print("\n[AVERAGE] Average weekly demand by product:")
    cursor.execute("""
        SELECT product_id,
               ROUND(AVG(demand_units), 0) as avg_demand,
               MIN(demand_units) as min_demand,
               MAX(demand_units) as max_demand
        FROM historical_demand_data
        GROUP BY product_id
        ORDER BY product_id
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {int(row[1])} units (range: {row[2]} - {row[3]})")

    # Check 4: Count anomalies
    print("\n[ANOMALIES] Anomalies detected:")
    cursor.execute("""
        SELECT product_id, COUNT(*) as anomaly_count
        FROM historical_demand_data
        WHERE is_anomaly = 1
        GROUP BY product_id
        ORDER BY product_id
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} anomalies")

    # Check 5: Market context
    print("\n[MARKET] Market context:")
    cursor.execute("SELECT * FROM market_context_data ORDER BY date_recorded DESC LIMIT 1")
    row = cursor.fetchone()
    if row:
        print(f"   Date: {row[1]}")
        print(f"   Industry Growth: {row[2]}%")
        print(f"   Economic Indicator: {row[3]}")
        print(f"   Competitor Activity: {row[4]}")

    conn.close()

    print("\n" + "=" * 70)
    print("[SUCCESS] MIGRATION COMPLETE!")
    print("=" * 70)
    print("\nYou can now query historical data with SQL:")
    print("  SELECT * FROM historical_demand_data WHERE product_id = 'PROD-A';")
    print("  SELECT * FROM market_context_data;")
    print("\nNext step: Update tools/forecasting.py to use database queries")


if __name__ == "__main__":
    print("\n[START] Starting database migration...\n")

    # Step 1: Populate historical demand data
    populate_historical_demand_data()

    # Step 2: Populate market context data
    populate_market_context_data()

    # Step 3: Verify migration
    verify_migration()

    print("\n[DONE] All done! Database is now populated with historical data.\n")
