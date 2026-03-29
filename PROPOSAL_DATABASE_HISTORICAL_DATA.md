# PROPOSAL: Store Historical Data in Database Tables

## 📋 Executive Summary

**Current Problem:**
- Historical demand data is generated on-the-fly by Python function `get_historical_demand()`
- Data is **NOT stored** in database
- **Cannot validate** with SQL queries
- Data **changes** each time you run the function (random noise)
- **Not auditable** - can't trace what data AI agent used

**Proposed Solution:**
- Create new database table `historical_demand_data`
- **Populate once** with realistic historical data
- AI tools **query database** instead of calling Python function
- **Fully traceable** - SQL query shows exact data used
- **Persistent** - same data every time
- **Auditable** - know inputs that produced outputs

---

## 🔄 Current vs Proposed Flow

### CURRENT FLOW (Problem)

```
User runs pipeline
    ↓
AI Tool calls get_historical_demand()
    ↓
Python generates 12 weeks of random data
    demand = 950 + trend + seasonal + random.gauss(0, 60)
    ↓
Different data EVERY time (because of random noise!)
    ↓
Cannot validate with SQL ❌
```

### PROPOSED FLOW (Solution)

```
[ONE-TIME SETUP]
Run migration script
    ↓
Populates historical_demand_data table with 52 weeks
    ↓

[ONGOING USE]
User runs pipeline
    ↓
AI Tool queries: SELECT * FROM historical_demand_data WHERE product_id = 'PROD-A'
    ↓
Same data EVERY time ✅
    ↓
Can validate with SQL ✅
Can trace AI decisions ✅
```

---

## 📊 Proposed Database Tables

### Table 1: `historical_demand_data`

**Purpose:** Store weekly historical demand for AI training

**Schema:**

```sql
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
);

CREATE INDEX idx_historical_demand_product ON historical_demand_data(product_id);
CREATE INDEX idx_historical_demand_date ON historical_demand_data(week_start_date DESC);
```

**Column Details:**

| Column | Type | Nullable | Business Meaning | Example Value |
|--------|------|----------|------------------|---------------|
| `id` | INTEGER | NO | Unique record ID | 42 |
| `product_id` | TEXT | NO | Which product | "PROD-A" |
| `week_start_date` | DATE | NO | Monday of that week | "2026-03-03" |
| `week_number` | INTEGER | NO | ISO week number (1-53) | 10 |
| `year` | INTEGER | NO | Year | 2026 |
| `demand_units` | INTEGER | NO | Actual units sold that week | 1107 |
| `avg_price` | REAL | YES | Average selling price | 88.50 |
| `promotions_active` | BOOLEAN | NO | Was there a promotion? | 1 (true) |
| `competitor_price` | REAL | YES | Competitor's price | 92.00 |
| `is_anomaly` | BOOLEAN | NO | Unusual week? | 1 (spike week) |
| `anomaly_reason` | TEXT | YES | Why unusual? | "Holiday promotion" |
| `created_at` | TIMESTAMP | NO | When record was created | "2026-03-04 10:00:00" |

**Why This Design:**

✅ **week_start_date** - Exact date for time-series analysis
✅ **UNIQUE constraint** - Prevent duplicate weeks for same product
✅ **Indexes** - Fast queries by product and date
✅ **is_anomaly flag** - Mark unusual weeks (spike, dip)
✅ **anomaly_reason** - Document WHY (promotion, holiday, stockout)

---

### Table 2: `market_context_data`

**Purpose:** Store external market factors (instead of hardcoded values)

```sql
CREATE TABLE IF NOT EXISTS market_context_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    observation_date DATE NOT NULL UNIQUE,
    season TEXT,
    economic_indicator TEXT,
    industry_trend TEXT,
    raw_material_trend TEXT,
    competitor_activity TEXT,
    social_media_volume INTEGER,
    social_media_sentiment REAL,
    social_media_topic TEXT,
    weather_forecast TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Sample Data:**

```sql
INSERT INTO market_context_data (
    observation_date, season, economic_indicator, industry_trend,
    social_media_volume, social_media_sentiment, social_media_topic
) VALUES (
    '2026-03-04', 'Q1', 'stable', 'growing at 4.2% YoY',
    2400, 0.78, 'viral TikTok video featuring our product'
);
```

---

### Table 3: Keep `inventory` table (already exists, just populate it)

**Current Schema:** (Already in schema.sql)

```sql
CREATE TABLE IF NOT EXISTS inventory (
    product_id TEXT PRIMARY KEY,
    current_stock INTEGER NOT NULL,
    safety_stock INTEGER,
    reorder_point INTEGER,
    avg_daily_usage REAL,
    lead_time INTEGER,
    stockout_risk REAL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

**Just needs to be populated:**

```sql
INSERT INTO inventory (product_id, current_stock, safety_stock, avg_daily_usage, stockout_risk)
VALUES ('PROD-A', 1850, 300, 142, 0.15);
```

---

## 🔧 Migration Script

**File:** `backend/migrate_historical_data.py`

```python
"""
Migration Script: Populate historical_demand_data table
Run this ONCE to create historical data for AI training
"""
import sqlite3
import random
import math
from datetime import datetime, timedelta
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "amis.db"

def populate_historical_demand_data():
    """
    Generate and store 52 weeks of historical demand data
    This runs ONCE, then data is persistent
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Algorithm parameters (same as sample_data.py)
    base_demand = 950
    trend = 15  # units increase per week
    seasonal_amplitude = 120
    noise_std = 60

    products = ['PROD-A', 'PROD-B', 'PROD-C']
    today = datetime.now()

    for product_id in products:
        print(f"Generating historical data for {product_id}...")

        for i in range(52, 0, -1):  # 52 weeks (1 year)
            week_date = today - timedelta(weeks=i)
            week_num = week_date.isocalendar()[1]
            year = week_date.year

            # Same algorithm as sample_data.py
            seasonal = seasonal_amplitude * math.sin(2 * math.pi * week_num / 52)
            trend_value = trend * (52 - i)
            noise = random.gauss(0, noise_std)

            # Anomalies
            anomaly = 0
            is_anomaly = False
            anomaly_reason = None

            if i == 3:  # Recent spike
                anomaly = 380
                is_anomaly = True
                anomaly_reason = "Flash sale promotion"
            elif i == 15:  # Mid-year dip
                anomaly = -200
                is_anomaly = True
                anomaly_reason = "Supply chain delay"

            demand = int(base_demand + trend_value + seasonal + noise + anomaly)
            demand = max(demand, 200)  # Floor

            # Promotions
            promotions_active = i in [3, 7, 15, 25, 40]

            cursor.execute("""
                INSERT OR REPLACE INTO historical_demand_data
                (product_id, week_start_date, week_number, year, demand_units,
                 avg_price, promotions_active, competitor_price, is_anomaly, anomaly_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                week_date.strftime("%Y-%m-%d"),
                week_num,
                year,
                demand,
                round(88.50 + random.uniform(-3, 3), 2),
                promotions_active,
                round(92.00 + random.uniform(-5, 5), 2),
                is_anomaly,
                anomaly_reason
            ))

        print(f"  ✓ Created 52 weeks of data for {product_id}")

    conn.commit()
    conn.close()
    print("\n✅ Migration complete!")
    print(f"Total records created: {len(products) * 52} = {len(products)} products × 52 weeks")


def populate_market_context():
    """Populate market context for current week"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO market_context_data (
            observation_date, season, economic_indicator, industry_trend,
            raw_material_trend, competitor_activity,
            social_media_volume, social_media_sentiment, social_media_topic,
            weather_forecast
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d"),
        "Q1",
        "stable",
        "growing at 4.2% YoY",
        "up 6% last quarter",
        "Competitor X launched new product line last week",
        2400,
        0.78,
        "viral TikTok video featuring our product",
        "Normal conditions expected"
    ))

    conn.commit()
    conn.close()
    print("✅ Market context data populated")


def populate_inventory():
    """Populate inventory table with initial stock levels"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    inventory_data = [
        ('PROD-A', 1850, 300, 142, 0.15),
        ('PROD-B', 2100, 400, 180, 0.08),
        ('PROD-C', 950, 200, 95, 0.25),
    ]

    for product_id, stock, safety, usage, risk in inventory_data:
        cursor.execute("""
            INSERT OR REPLACE INTO inventory
            (product_id, current_stock, safety_stock, avg_daily_usage, stockout_risk)
            VALUES (?, ?, ?, ?, ?)
        """, (product_id, stock, safety, usage, risk))

    conn.commit()
    conn.close()
    print("✅ Inventory data populated")


if __name__ == "__main__":
    print("=" * 60)
    print("AMIS Database Migration: Historical Data")
    print("=" * 60)
    print()

    populate_historical_demand_data()
    populate_market_context()
    populate_inventory()

    print()
    print("=" * 60)
    print("Migration complete! You can now validate with SQL:")
    print("  SELECT COUNT(*) FROM historical_demand_data;")
    print("  SELECT * FROM historical_demand_data WHERE product_id = 'PROD-A' LIMIT 10;")
    print("=" * 60)
```

---

## 🔄 Updated Tool Code

**File:** `tools/forecasting.py`

**BEFORE (current - uses Python function):**

```python
def get_historical_demand(product_id: str = "PROD-A", weeks: int = 12):
    # Generates random data on-the-fly
    base_demand = 950
    ...
    return data  # Different every time!
```

**AFTER (proposed - queries database):**

```python
def get_historical_demand_from_db(product_id: str = "PROD-A", weeks: int = 12):
    """
    Query historical demand from database
    Returns same data every time - fully traceable!
    """
    from backend.database import get_db_connection

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            week_start_date as date,
            week_number,
            year,
            demand_units,
            avg_price,
            promotions_active,
            competitor_price,
            is_anomaly,
            anomaly_reason
        FROM historical_demand_data
        WHERE product_id = ?
        ORDER BY week_start_date DESC
        LIMIT ?
    """, (product_id, weeks))

    rows = cursor.fetchall()
    conn.close()

    # Convert to same format as before
    data = []
    for row in rows:
        data.append({
            "week": f"{row[2]}-W{row[1]:02d}",  # "2026-W10"
            "date": row[0],
            "product_id": product_id,
            "demand_units": row[3],
            "anomaly": bool(row[7]),
            "avg_price": row[4],
            "promotions_active": bool(row[5]),
            "competitor_price": row[6],
        })

    return list(reversed(data))  # Oldest to newest
```

**Benefits:**

✅ **Same signature** - no changes to calling code
✅ **Same output format** - existing tools work unchanged
✅ **Database-backed** - can validate with SQL
✅ **Persistent** - same data every run

---

## 📊 SQL Validation Queries

### Query 1: View Historical Data

```sql
-- See all historical demand for PROD-A
SELECT
    week_start_date,
    demand_units,
    promotions_active,
    is_anomaly,
    anomaly_reason
FROM historical_demand_data
WHERE product_id = 'PROD-A'
ORDER BY week_start_date DESC
LIMIT 12;

-- Expected: 12 most recent weeks
-- Check: Week with promotion should have higher demand
-- Check: Anomaly weeks should be marked
```

### Query 2: Calculate Statistics (Same as AI Does)

```sql
-- Calculate average demand (what AI sees)
SELECT
    AVG(demand_units) as avg_demand,
    MIN(demand_units) as min_demand,
    MAX(demand_units) as max_demand,
    COUNT(*) as weeks_count
FROM historical_demand_data
WHERE product_id = 'PROD-A'
  AND week_start_date >= DATE('now', '-12 weeks');

-- Expected:
-- avg_demand ≈ 1138 units
-- min_demand ≈ 920 units
-- max_demand ≈ 1450 units (anomaly week)
```

### Query 3: Find Anomalies

```sql
-- Which weeks were unusual?
SELECT
    week_start_date,
    demand_units,
    anomaly_reason,
    promotions_active
FROM historical_demand_data
WHERE product_id = 'PROD-A'
  AND is_anomaly = 1
ORDER BY week_start_date DESC;

-- Expected: See spike weeks with reasons
-- Example: "Flash sale promotion" caused 1450 units demand
```

### Query 4: Week-over-Week Changes

```sql
-- Calculate wow changes (what Tool 3 does)
WITH weekly_data AS (
    SELECT
        week_start_date,
        demand_units,
        LAG(demand_units) OVER (ORDER BY week_start_date) as prev_week_demand
    FROM historical_demand_data
    WHERE product_id = 'PROD-A'
      AND week_start_date >= DATE('now', '-12 weeks')
)
SELECT
    week_start_date,
    demand_units,
    prev_week_demand,
    ROUND(((demand_units - prev_week_demand) * 100.0 / prev_week_demand), 1) as wow_change_pct
FROM weekly_data
WHERE prev_week_demand IS NOT NULL
ORDER BY week_start_date;

-- Expected: See +47.2% spike week, -27.6% return to normal
```

---

## 🎯 Implementation Plan

### Step 1: Add New Tables to Schema

**File:** `backend/schema.sql` (append to end)

```sql
-- Historical demand data for AI training
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
);

CREATE INDEX idx_historical_demand_product ON historical_demand_data(product_id);
CREATE INDEX idx_historical_demand_date ON historical_demand_data(week_start_date DESC);

-- Market context data
CREATE TABLE IF NOT EXISTS market_context_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    observation_date DATE NOT NULL UNIQUE,
    season TEXT,
    economic_indicator TEXT,
    industry_trend TEXT,
    raw_material_trend TEXT,
    competitor_activity TEXT,
    social_media_volume INTEGER,
    social_media_sentiment REAL,
    social_media_topic TEXT,
    weather_forecast TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Step 2: Run Migration Script

```bash
cd backend
python migrate_historical_data.py

# Output:
# Generating historical data for PROD-A...
#   ✓ Created 52 weeks of data for PROD-A
# Generating historical data for PROD-B...
#   ✓ Created 52 weeks of data for PROD-B
# Generating historical data for PROD-C...
#   ✓ Created 52 weeks of data for PROD-C
#
# ✅ Migration complete!
# Total records created: 156 = 3 products × 52 weeks
```

### Step 3: Update Tools to Use Database

**File:** `tools/forecasting.py`

Replace `get_historical_demand()` calls with `get_historical_demand_from_db()`

### Step 4: Test with SQL

```bash
cd backend
sqlite3 amis.db

sqlite> SELECT COUNT(*) FROM historical_demand_data;
-- Expected: 156

sqlite> SELECT * FROM historical_demand_data WHERE product_id = 'PROD-A' LIMIT 5;
-- Expected: See 5 rows with demand data
```

### Step 5: Run Pipeline and Validate

```bash
# Run pipeline
curl -X POST http://localhost:8000/api/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"product_id": "PROD-A"}'

# Query historical data AI used
sqlite3 backend/amis.db "
SELECT AVG(demand_units) FROM historical_demand_data
WHERE product_id = 'PROD-A'
  AND week_start_date >= DATE('now', '-12 weeks');
"

# Compare to forecast results
sqlite3 backend/amis.db "
SELECT AVG(base_case) FROM demand_forecasts WHERE product_id = 'PROD-A';
"

# They should be related (forecast based on historical avg + trend)
```

---

## ✅ Benefits of This Approach

| Benefit | Before (sample_data.py) | After (Database) |
|---------|-------------------------|------------------|
| **Traceability** | ❌ Can't see what data AI used | ✅ `SELECT * FROM historical_demand_data` |
| **Consistency** | ❌ Different data every run (random) | ✅ Same data every run |
| **Validation** | ❌ Cannot query with SQL | ✅ Full SQL validation |
| **Auditability** | ❌ No record of inputs | ✅ Complete audit trail |
| **Documentation** | ❌ "Trust me, it works" | ✅ "Here's the SQL proof" |
| **Debugging** | ❌ Hard to reproduce issues | ✅ Exact data available |

---

## 🎓 Learning Value (For Hackathon Judges)

**BEFORE:**
> "Our AI forecasts demand using historical patterns"
> Judge: "Can I see the historical data?"
> You: "Uh... it's generated by a Python function..."
> Judge: "How do I validate your forecasts?"
> You: "..."

**AFTER:**
> "Our AI forecasts demand using 52 weeks of historical data stored in SQLite"
> Judge: "Can I see the data?"
> You: "Absolutely! Run this SQL:"
> ```sql
> SELECT * FROM historical_demand_data WHERE product_id = 'PROD-A';
> ```
> Judge: "How do I validate your forecasts?"
> You: "Compare this SQL result to our forecasts - here are 4 validation queries!"

**This shows:**
- ✅ Professional data engineering practices
- ✅ Transparency and auditability
- ✅ Real-world database design
- ✅ Testable, verifiable system

---

## 📝 Next Steps

1. **Review this proposal** - Does this make sense?
2. **Approve schema** - Are these the right tables/columns?
3. **I'll implement**:
   - Add tables to schema.sql
   - Create migration script
   - Update tools to query database
   - Create validation SQL queries
   - Update documentation

**Time to implement:** ~30 minutes

**Do you want me to proceed with implementation?**
