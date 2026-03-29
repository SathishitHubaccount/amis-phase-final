# SQL Validation Queries - Quick Reference

This document contains the most important SQL queries to validate the Demand Intelligence module.

---

## 1. View Historical Demand Data

**Purpose:** See the raw historical data that the AI uses as input

```sql
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
```

**What to look for:**
- 12 weeks of historical demand
- Demand values around 1,200-1,800 units
- Check for anomaly flags (is_anomaly = 1)
- Look for promotion weeks (promotions_active = 1)

---

## 2. Calculate Average Weekly Demand

**Purpose:** Verify the "Average Weekly Demand" shown in the UI

```sql
SELECT
    ROUND(AVG(demand_units), 0) as avg_demand,
    MIN(demand_units) as min_demand,
    MAX(demand_units) as max_demand
FROM historical_demand_data
WHERE product_id = 'PROD-A';
```

**Expected Result:**
- Average: ~1,344 units/week
- Min: ~947 units
- Max: ~2,081 units

**Compare to UI:**
- Go to Demand Intelligence page
- Check "Average Weekly Demand" metric
- Should match the `avg_demand` from SQL query

---

## 3. Find Demand Anomalies

**Purpose:** Verify that the AI correctly identifies anomalies

```sql
SELECT
    week_start_date,
    demand_units,
    anomaly_reason
FROM historical_demand_data
WHERE product_id = 'PROD-A'
  AND is_anomaly = 1
ORDER BY week_start_date DESC;
```

**Expected Result:**
```
Date            Demand     Reason
2026-02-04      2081       Viral social media campaign spike
2025-12-03      1194       Competitor supply chain disruption (demand shifted to us)
2025-09-03      1643       Black Friday promotional campaign
```

**Compare to AI Analysis:**
- Run the Demand Forecasting Agent
- Check if AI mentions "spike detected" in its analysis
- AI should reference the viral social media campaign

---

## 4. Calculate Trend Direction

**Purpose:** Verify the "Trend Direction" shown in the UI

```sql
WITH recent_data AS (
    SELECT
        demand_units,
        ROW_NUMBER() OVER (ORDER BY week_start_date DESC) as week_rank
    FROM historical_demand_data
    WHERE product_id = 'PROD-A'
    LIMIT 12
)
SELECT
    AVG(CASE WHEN week_rank <= 4 THEN demand_units END) as recent_4week_avg,
    AVG(demand_units) as all_12week_avg,
    ROUND(
        ((AVG(CASE WHEN week_rank <= 4 THEN demand_units END) - AVG(demand_units))
         / AVG(demand_units)) * 100,
        1
    ) as trend_pct
FROM recent_data;
```

**What to look for:**
- If `recent_4week_avg` > `all_12week_avg`: Upward trend
- If `recent_4week_avg` < `all_12week_avg`: Downward trend
- `trend_pct` should match the percentage shown in UI

---

## 5. Week-over-Week Changes

**Purpose:** Understand demand volatility

```sql
WITH weekly_data AS (
    SELECT
        week_start_date,
        demand_units,
        LAG(demand_units) OVER (ORDER BY week_start_date) as prev_demand
    FROM historical_demand_data
    WHERE product_id = 'PROD-A'
)
SELECT
    week_start_date,
    demand_units,
    prev_demand,
    ROUND(((demand_units - prev_demand) * 100.0 / prev_demand), 2) as wow_change_pct
FROM weekly_data
WHERE prev_demand IS NOT NULL
ORDER BY week_start_date DESC
LIMIT 10;
```

**What to look for:**
- Large spikes (>30%) indicate anomalies
- Consistent positive changes = upward trend
- High variance = volatile demand

---

## 6. View Market Context

**Purpose:** See the external market factors the AI considers

```sql
SELECT
    industry_growth_rate,
    economic_indicator,
    competitor_activity,
    raw_material_price_trend,
    seasonal_pattern,
    market_sentiment,
    supply_chain_status
FROM market_context_data
ORDER BY date_recorded DESC
LIMIT 1;
```

**Expected Result:**
```
Industry Growth:     7.2%
Economic Indicator:  Manufacturing PMI at 52.3 (expansion)
Competitor Activity: Competitor launched new product targeting enterprise market
Seasonal Pattern:    Q1 typically sees 15% higher demand
Market Sentiment:    Positive - Economic recovery driving capital investments
```

---

## 7. Count Data Availability

**Purpose:** Verify that all products have historical data

```sql
SELECT
    product_id,
    COUNT(*) as week_count,
    MIN(week_start_date) as oldest_week,
    MAX(week_start_date) as newest_week
FROM historical_demand_data
GROUP BY product_id
ORDER BY product_id;
```

**Expected Result:**
```
product_id    week_count    oldest_week    newest_week
PROD-A        52            2025-03-04     2026-02-25
PROD-B        52            2025-03-04     2026-02-25
PROD-C        52            2025-03-04     2026-02-25
```

---

## 8. Compare Historical to Forecast

**Purpose:** Validate that AI forecasts are reasonable based on history

```sql
-- Historical average (AI input)
SELECT
    'Historical Avg' as metric,
    ROUND(AVG(demand_units), 0) as value
FROM historical_demand_data
WHERE product_id = 'PROD-A'

UNION ALL

-- AI forecast (AI output)
SELECT
    'AI Forecast' as metric,
    base_case as value
FROM demand_forecasts
WHERE product_id = 'PROD-A'
ORDER BY forecast_date DESC
LIMIT 1;
```

**What to look for:**
- AI forecast should be close to historical average
- If different, check if AI adjusted for trend or anomalies

---

## 9. Validate Promotion Impact

**Purpose:** See if promotions increased demand

```sql
SELECT
    promotions_active,
    ROUND(AVG(demand_units), 0) as avg_demand,
    COUNT(*) as week_count
FROM historical_demand_data
WHERE product_id = 'PROD-A'
GROUP BY promotions_active;
```

**Expected Result:**
```
promotions_active    avg_demand    week_count
0                    ~1,300        ~42 weeks
1                    ~1,500        ~10 weeks
```

**What to look for:**
- Promotion weeks should have higher average demand
- This shows promotions are effective

---

## 10. Database Health Check

**Purpose:** Verify migration completed successfully

```sql
-- Check all tables exist and have data
SELECT 'historical_demand_data' as table_name, COUNT(*) as record_count
FROM historical_demand_data

UNION ALL

SELECT 'market_context_data' as table_name, COUNT(*) as record_count
FROM market_context_data

UNION ALL

SELECT 'demand_forecasts' as table_name, COUNT(*) as record_count
FROM demand_forecasts;
```

**Expected Result:**
```
table_name                record_count
historical_demand_data    156
market_context_data       1
demand_forecasts          (varies - created by pipeline)
```

---

## How to Run These Queries

### Option 1: SQLite Command Line
```bash
cd backend
sqlite3 amis.db
.mode column
.headers on
# Paste query here
```

### Option 2: Python Script
```python
import sqlite3
conn = sqlite3.connect('backend/amis.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM historical_demand_data LIMIT 5")
for row in cursor.fetchall():
    print(row)
conn.close()
```

### Option 3: SQLite Browser
1. Download DB Browser for SQLite (free)
2. Open `backend/amis.db`
3. Go to "Execute SQL" tab
4. Paste queries and run

---

## Validation Workflow for Hackathon Demo

**Step 1: Show Historical Data**
```sql
SELECT * FROM historical_demand_data WHERE product_id = 'PROD-A' LIMIT 10;
```
"This is the data the AI uses as input."

**Step 2: Run AI Pipeline**
- Go to UI → Pipeline → Run Analysis
- AI generates forecast

**Step 3: Show AI Output**
```sql
SELECT * FROM demand_forecasts WHERE product_id = 'PROD-A' ORDER BY created_at DESC LIMIT 1;
```
"This is what the AI predicted."

**Step 4: Validate with Statistics**
```sql
SELECT AVG(demand_units) FROM historical_demand_data WHERE product_id = 'PROD-A';
```
"The AI forecast is based on this historical average."

**Step 5: Explain Reasoning**
"The AI saw an anomaly spike (2,081 units) and a growing trend, so it predicted higher future demand. All data is traceable in the database."

---

## Troubleshooting Queries

### No data returned?
```sql
-- Check if tables exist
SELECT name FROM sqlite_master WHERE type='table';
```

### Wrong values?
```sql
-- Check when data was created
SELECT MAX(created_at) FROM historical_demand_data;
```

### Need to reset data?
```bash
cd backend
python migrate_historical_data.py
```

---

## Summary

These 10 SQL queries let you **fully validate** the Demand Intelligence module:

1. ✅ View historical data (AI input)
2. ✅ Calculate averages (validate UI metrics)
3. ✅ Find anomalies (validate AI detection)
4. ✅ Calculate trends (validate UI trend direction)
5. ✅ Week-over-week changes (understand volatility)
6. ✅ View market context (external factors)
7. ✅ Count data availability (verify all products)
8. ✅ Compare historical to forecast (validate AI reasoning)
9. ✅ Validate promotion impact (business insights)
10. ✅ Database health check (migration success)

**For the hackathon demo, focus on queries 1, 2, 3, and 8** to show:
- Where the data comes from
- How the AI uses it
- Why the forecast is correct
