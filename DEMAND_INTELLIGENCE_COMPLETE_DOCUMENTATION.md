# DEMAND INTELLIGENCE MODULE - COMPLETE TECHNICAL DOCUMENTATION

**Version:** 1.0
**Date:** March 2026
**Purpose:** Complete end-to-end documentation for learning and validating the Demand Intelligence system

---

## TABLE OF CONTENTS

1. [Module Overview](#1-module-overview)
2. [System Architecture](#2-system-architecture)
3. [Database Schema & Data Sources](#3-database-schema--data-sources)
4. [Pipeline Execution Flow](#4-pipeline-execution-flow)
5. [AI Agent & Tools](#5-ai-agent--tools)
6. [Calculation Logic & Formulas](#6-calculation-logic--formulas)
7. [Data Flow: Backend to Frontend](#7-data-flow-backend-to-frontend)
8. [UI Components & Display](#8-ui-components--display)
9. [Validation & Testing](#9-validation--testing)
10. [Troubleshooting Guide](#10-troubleshooting-guide)

---

## 1. MODULE OVERVIEW

### 1.1 What is Demand Intelligence?

**Demand Intelligence** is the forecasting module in AMIS that predicts future product demand using AI-powered scenario analysis. It helps manufacturing teams answer:

- "How much product should we make next week/month?"
- "Is the recent demand spike a trend or anomaly?"
- "What's the financial impact of different production strategies?"

### 1.2 Key Features

| Feature | Description | Value to User |
|---------|-------------|---------------|
| **AI-Powered Forecasting** | Uses Claude AI to analyze 12 weeks of historical data and generate multi-scenario forecasts (Optimistic, Base, Pessimistic) | Confident decision-making with probability weights |
| **Automatic Pipeline Sync** | When you run the AI Pipeline, forecasts automatically sync to database | No manual data entry needed |
| **Manual Forecast Entry** | Users can add/edit forecasts manually with validation | Control over data, ability to override AI |
| **Trend Analysis** | Calculates trend direction, growth rate, week-over-week changes | Understand if demand is growing, declining, or stable |
| **Visual Charts** | Area chart shows 3 scenarios + actual demand (purple line) | Easy to spot patterns and variances |
| **Actual vs Forecast** | Track actual demand against predictions to measure accuracy | Continuous improvement of forecasting process |

### 1.3 Who Uses This Module?

| Role | What They Do | How They Use Demand Intelligence |
|------|--------------|----------------------------------|
| **Demand Planner (Jessica)** | Forecasts customer demand, manages orders | Primary user - reviews AI forecasts, adds manual forecasts, tracks actuals |
| **Operations Manager (Sarah)** | Makes strategic production decisions | Uses insights to approve production volumes |
| **Production Supervisor (Mike)** | Executes daily production plans | Checks demand outlook to validate production schedules |

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER (Browser)                              │
│                     localhost:5173                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP Request
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│               FRONTEND (React + Vite)                           │
│                                                                  │
│  DemandIntelligence.jsx                                         │
│  ├─ Fetches /api/products (product list)                       │
│  ├─ Fetches /api/demand/forecasts/{product_id} (forecast data) │
│  ├─ POST /api/demand/forecasts (create new forecast)           │
│  └─ Calculates insights (avg, trend) from data                 │
│                                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ API Call (JSON)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│               BACKEND (FastAPI)                                  │
│               localhost:8000                                     │
│                                                                  │
│  main.py                                                         │
│  ├─ GET /api/demand/forecasts/{product_id}?weeks=12            │
│  │   → Calls database.get_demand_forecasts(product_id, 12)     │
│  │   → Returns JSON: {forecasts: [...]}                        │
│  │                                                               │
│  ├─ POST /api/demand/forecasts/{product_id}                    │
│  │   → Calls database.create_demand_forecast(...)              │
│  │   → Returns: {forecast_id: 123}                             │
│  │                                                               │
│  └─ POST /api/pipeline/run                                     │
│      → Runs OrchestratorAgent.run_full_pipeline()              │
│      → Calls DemandForecastingAgent.run()                      │
│      → Syncs results to database via ai_database_bridge        │
│                                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ SQL Query
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│               DATABASE (SQLite)                                  │
│               backend/amis.db                                    │
│                                                                  │
│  Tables:                                                         │
│  ├─ demand_forecasts (AI + manual forecasts)                   │
│  ├─ products (product master data)                             │
│  └─ production_schedule (weekly production plans)              │
│                                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Tool Calls
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│             AI AGENT (DemandForecastingAgent)                    │
│                                                                  │
│  demand_agent.py                                                 │
│  ├─ Uses LangChain + Claude (Anthropic API)                    │
│  ├─ Has access to 3 tools:                                     │
│  │   1. simulate_demand_scenarios()                            │
│  │   2. analyze_demand_trends()                                │
│  │   3. get_demand_data_summary()                              │
│  └─ Generates human-readable analysis + structured JSON        │
│                                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Reads Sample Data
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│             SAMPLE DATA (Simulated ERP Data)                     │
│                                                                  │
│  sample_data.py                                                  │
│  ├─ get_historical_demand() - 12 weeks of demand data          │
│  ├─ get_market_context() - External factors (trends, events)   │
│  ├─ get_current_inventory() - Stock levels                     │
│  └─ get_production_capacity() - Production constraints         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React 18 + Vite | User interface, charts |
| **Charts** | Recharts | Data visualization (area charts) |
| **State Management** | React Query (TanStack Query) | API calls, caching |
| **Backend** | FastAPI (Python 3.11+) | REST API server |
| **AI Framework** | LangChain + Claude 3.5 Sonnet | Agentic AI reasoning |
| **Database** | SQLite 3 | Persistent data storage |
| **Data Tools** | Python (math, statistics) | Forecasting algorithms |

---

## 3. DATABASE SCHEMA & DATA SOURCES

### 3.1 Database Tables Overview

The Demand Intelligence module uses **2 primary tables** and **1 reference table**:

1. **`demand_forecasts`** - Stores all forecast data (AI + manual)
2. **`products`** - Product master data
3. **`production_schedule`** - Links demand to production plans

### 3.2 `demand_forecasts` Table (CORE TABLE)

**Location:** `backend/schema.sql` lines 179-190

```sql
CREATE TABLE IF NOT EXISTS demand_forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    week_number INTEGER,
    forecast_date DATE,
    optimistic INTEGER,
    base_case INTEGER,
    pessimistic INTEGER,
    actual INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

#### Column Details

| Column | Type | Nullable | Description | Business Meaning | Example Value |
|--------|------|----------|-------------|------------------|---------------|
| **id** | INTEGER | NO | Auto-incrementing primary key | Unique ID for each forecast entry | 42 |
| **product_id** | TEXT | NO | Product identifier (FK) | Which product this forecast is for | "PROD-A" |
| **week_number** | INTEGER | YES | Week number in year (1-52) | Which week this forecast covers | 10 (= 10th week of 2026) |
| **forecast_date** | DATE | YES | Start date of the forecast week | When this forecast week begins | "2026-03-09" |
| **optimistic** | INTEGER | YES | Optimistic scenario demand (units) | Upper bound demand (20% probability) | 1,250 |
| **base_case** | INTEGER | YES | Most likely demand (units) | Expected demand (55% probability) | 1,050 |
| **pessimistic** | INTEGER | YES | Conservative scenario demand (units) | Lower bound demand (25% probability) | 850 |
| **actual** | INTEGER | YES | Actual demand that occurred (units) | Real sales after week completes | 1,080 (once known) |
| **created_at** | TIMESTAMP | NO | When this record was created | Audit trail for when forecast was made | "2026-03-04 10:23:45" |

#### Data Integrity Rules

1. **Foreign Key:** `product_id` must exist in `products` table
2. **Validation:** `optimistic >= base_case >= pessimistic` (checked in application layer)
3. **Uniqueness:** Combination of `(product_id, week_number)` should be unique (enforced by application)
4. **NULL Handling:**
   - `actual` starts as NULL
   - User updates `actual` after week ends
   - Used to calculate forecast accuracy

#### Sample Data

```sql
INSERT INTO demand_forecasts
(product_id, week_number, forecast_date, optimistic, base_case, pessimistic, actual)
VALUES
('PROD-A', 10, '2026-03-09', 1250, 1050, 850, NULL),
('PROD-A', 11, '2026-03-16', 1280, 1075, 870, NULL),
('PROD-A', 12, '2026-03-23', 1310, 1100, 890, 1095); -- actual recorded!
```

### 3.3 `products` Table (REFERENCE)

**Location:** `backend/schema.sql` lines 5-11

```sql
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Column Details

| Column | Type | Description | Example Value |
|--------|------|-------------|---------------|
| **id** | TEXT | Product ID (Primary Key) | "PROD-A" |
| **name** | TEXT | Human-readable product name | "Automotive Sensor Unit" |
| **category** | TEXT | Product category/family | "Electronics" |
| **status** | TEXT | Active status | "active" |

#### Sample Data

```sql
INSERT INTO products (id, name, category, status) VALUES
('PROD-A', 'Automotive Sensor Unit', 'Electronics', 'active'),
('PROD-B', 'Industrial Motor Assembly', 'Mechanical', 'active'),
('PROD-C', 'Smart Thermostat', 'Electronics', 'active');
```

### 3.4 Data Relationships

```
products (1) ─────── (Many) demand_forecasts
   │                        │
   │                        │
   │                        ↓
   └────────────── (Many) production_schedule
```

**Relationship Logic:**
- One product (e.g., PROD-A) has many forecast entries (one per week)
- Forecasts link to production schedules (demand drives production)

### 3.5 Database Access Functions

**Location:** `backend/database.py` lines 687-750

#### 3.5.1 `get_demand_forecasts(product_id, weeks)`

**Purpose:** Retrieve forecast data for a product

**Code:**
```python
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
```

**Inputs:**
- `product_id` (str): Product ID like "PROD-A"
- `weeks` (int): How many weeks to return (default: 12)

**Output:**
```json
[
  {
    "id": 1,
    "product_id": "PROD-A",
    "week_number": 10,
    "forecast_date": "2026-03-09",
    "optimistic": 1250,
    "base_case": 1050,
    "pessimistic": 850,
    "actual": null,
    "created_at": "2026-03-04 10:23:45"
  },
  ...
]
```

**SQL Query:**
```sql
SELECT * FROM demand_forecasts
WHERE product_id = 'PROD-A'
ORDER BY week_number
LIMIT 12
```

#### 3.5.2 `create_demand_forecast(product_id, week_number, forecast_data)`

**Purpose:** Insert new forecast into database

**Code:**
```python
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
```

**Inputs:**
- `product_id`: "PROD-A"
- `week_number`: 10
- `forecast_data`: `{"forecast_date": "2026-03-09", "optimistic": 1250, "base_case": 1050, "pessimistic": 850}`

**Output:**
- `forecast_id` (int): The ID of newly created record (e.g., 42)

**Side Effects:**
- Logs activity to `activity_log` table
- Triggers timestamp update (`created_at`)

#### 3.5.3 `update_actual_demand(product_id, week_number, actual)`

**Purpose:** Update actual demand after week completes

**Code:**
```python
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
```

**Inputs:**
- `product_id`: "PROD-A"
- `week_number`: 10
- `actual`: 1095

**Output:**
- `True` if update successful, `False` if no matching record

**SQL Query:**
```sql
UPDATE demand_forecasts
SET actual = 1095
WHERE product_id = 'PROD-A' AND week_number = 10
```

### 3.6 Sample Data Source (AI Training Data)

**Location:** `data/sample_data.py` lines 11-58

The AI agent doesn't directly query the database for historical analysis. Instead, it uses **simulated historical data** that mimics real ERP/MES systems.

#### 3.6.1 `get_historical_demand(product_id, weeks=12)`

**Purpose:** Generate 12 weeks of realistic historical demand data for AI analysis

**Algorithm:**
```python
demand = base_demand + trend_value + seasonal + noise + anomaly
```

**Components:**

| Component | Formula | Description | Example |
|-----------|---------|-------------|---------|
| **Base Demand** | 950 units | Starting baseline | 950 |
| **Trend** | 15 × (weeks - i) | Linear growth trend | 15 × 9 = 135 |
| **Seasonal** | 120 × sin(2π × week_num / 52) | Annual seasonality pattern | 120 × sin(...) ≈ 45 |
| **Noise** | Normal(0, 60) | Random week-to-week variation | -23 (random) |
| **Anomaly** | 380 (week 3 only) | Simulated demand spike | 380 or 0 |

**Final Calculation Example (Week 9):**
```
demand = 950 + 135 + 45 + (-23) + 0 = 1,107 units
```

**Output Format:**
```json
[
  {
    "week": "2026-W01",
    "date": "2026-01-05",
    "product_id": "PROD-A",
    "demand_units": 1107,
    "anomaly": false,
    "avg_price": 88.50,
    "promotions_active": false,
    "competitor_price": 92.00
  },
  ...
]
```

**Why This Matters:**
- AI agent analyzes this historical data to predict future demand
- Simulates real-world patterns: trends, seasonality, noise, promotions
- In production, this would connect to actual ERP/MES database

---

## 4. PIPELINE EXECUTION FLOW

### 4.1 What is the Pipeline?

The **AI Pipeline** is the automated daily process that runs all 5 AI agents in sequence to update the system with fresh insights.

**Think of it like this:**
- **Without Pipeline**: You manually ask each AI agent for analysis (slow, manual)
- **With Pipeline**: Click one button → all 5 agents run → database updates automatically

### 4.2 Pipeline Trigger Points

| Trigger | When | How | Who |
|---------|------|-----|-----|
| **Manual (UI Button)** | Anytime user clicks "Run Pipeline" | User goes to Pipeline page → clicks button | Any user |
| **Scheduled (Future)** | Daily at 6:00 AM | Cron job / scheduled task | System (automated) |
| **API Call** | Programmatic trigger | `POST /api/pipeline/run` | External system |

### 4.3 Step-by-Step Pipeline Flow (Demand Intelligence Focus)

#### STEP 1: User Triggers Pipeline

**Location:** Frontend → `frontend/src/pages/RunPipeline.jsx`

**User Action:**
1. User navigates to http://localhost:5173/pipeline
2. Selects product (e.g., "PROD-A")
3. Clicks "Run Full Pipeline" button

**Frontend Code:**
```javascript
const handleRunPipeline = async () => {
  const response = await fetch('http://localhost:8000/api/pipeline/run', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({product_id: selectedProduct})
  })

  const data = await response.json()
  const runId = data.run_id  // e.g., "a3f5b9c2-..."

  // Poll for status every 2 seconds
  pollPipelineStatus(runId)
}
```

**What Happens:**
- Frontend sends `POST /api/pipeline/run` with `{product_id: "PROD-A"}`
- Backend creates a unique `run_id` (UUID)
- Backend starts pipeline in **background task**
- Frontend receives `run_id` immediately (non-blocking)
- Frontend polls `/api/pipeline/runs/{run_id}` every 2 seconds to check status

---

#### STEP 2: Backend Starts Pipeline Task

**Location:** Backend → `backend/main.py` lines 298-318

**Code:**
```python
@app.post("/api/pipeline/run")
async def run_pipeline(request: PipelineRunRequest, background_tasks: BackgroundTasks):
    """Run full 5-agent pipeline"""
    run_id = str(uuid.uuid4())  # Generate unique ID

    pipeline_runs[run_id] = {
        "id": run_id,
        "product_id": request.product_id,
        "status": "pending",  # Status: pending → running → completed/failed
        "created_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
        "agents_completed": [],
        "result": None,
        "error": None
    }

    # Add background task (doesn't block the API response)
    background_tasks.add_task(run_pipeline_task, run_id, request.product_id)

    return {"run_id": run_id, "status": "pending"}
```

**Key Concept: Background Task**
- Pipeline runs in **separate thread** (doesn't block API)
- User gets immediate response with `run_id`
- Actual agent execution happens asynchronously

---

#### STEP 3: Orchestrator Agent Runs

**Location:** Backend → `backend/main.py` lines 196-236

**Code:**
```python
async def run_pipeline_task(run_id: str, product_id: str):
    """Run full 5-agent pipeline in background"""
    try:
        pipeline_runs[run_id]["status"] = "running"
        pipeline_runs[run_id]["started_at"] = datetime.utcnow().isoformat()

        # Get orchestrator agent instance
        orchestrator = get_agent("orchestrator")

        # Run full pipeline (calls all 5 agents)
        structured_result = await asyncio.to_thread(
            orchestrator.run_full_pipeline,
            product_id=product_id,
            planning_weeks=4
        )

        # Format human-readable result
        text_result = format_pipeline_result(structured_result)

        # ========== AUTOMATICALLY SYNC TO DATABASE ==========
        from ai_database_bridge import get_bridge
        bridge = get_bridge()
        sync_result = bridge.sync_pipeline_results(structured_result)
        # ====================================================

        pipeline_runs[run_id].update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "result": text_result,
            "structured_result": structured_result,
            "database_sync": sync_result,
            "agents_completed": ["demand", "inventory", "machine", "production", "supplier"],
            "error": None
        })
    except Exception as e:
        pipeline_runs[run_id].update({
            "status": "failed",
            "error": str(e)
        })
```

**What Happens:**
1. Orchestrator agent coordinates all 5 agents
2. Demand agent runs first (because other agents depend on demand forecast)
3. Results stored in `structured_result` (JSON format)
4. Results synced to database via `ai_database_bridge`

---

#### STEP 4: Demand Forecasting Agent Executes

**Location:** Agents → `agents/demand_agent.py` lines 32-74

**Entry Point:**
```python
def get_forecast_output(self, product_id: str = "PROD-A") -> dict:
    """
    Generate standardized forecast for cross-agent consumption.
    This runs forecasting tools programmatically (not via LLM chat).
    """
    from tools.forecasting import simulate_demand_scenarios, analyze_demand_trends

    # TOOL 1: Generate 3 scenarios (Optimistic, Base, Pessimistic)
    scenarios_json = simulate_demand_scenarios.invoke({
        "product_id": product_id,
        "horizon_weeks": 4,
    })
    scenarios = json.loads(scenarios_json)

    # TOOL 2: Analyze historical trends
    trends_json = analyze_demand_trends.invoke({
        "product_id": product_id,
    })
    trends = json.loads(trends_json)

    # Package structured output
    return {
        "source_agent": "demand_forecasting",
        "timestamp": datetime.now().isoformat(),
        "product_id": product_id,
        "forecast_horizon_weeks": 4,
        "expected_weekly_demand": scenarios["expected_weighted_demand"] // 4,
        "demand_std_dev": trends["demand_statistics"]["std_deviation"],
        "scenarios": {...},  # 3 scenarios with probabilities
        "trend_direction": trends["trend_analysis"]["direction"],
        "growth_rate_pct_per_week": trends["trend_analysis"]["growth_rate_pct_per_week"],
        "anomaly_detected": scenarios["historical_summary"]["spike_detected"],
        "recommended_strategy": "balanced"
    }
```

**What Happens:**
1. Agent calls `simulate_demand_scenarios()` tool
2. Agent calls `analyze_demand_trends()` tool
3. Agent combines results into structured JSON
4. Returns forecast envelope to orchestrator

---

#### STEP 5: Tools Execute Forecasting Algorithms

**Location:** Tools → `tools/forecasting.py`

##### TOOL 1: `simulate_demand_scenarios(product_id, horizon_weeks=4)`

**Location:** Lines 14-116

**Purpose:** Generate 3 demand scenarios with probability weights

**Algorithm Steps:**

**Step 5.1: Load Historical Data**
```python
historical = get_historical_demand(product_id)  # 12 weeks of data
demands = [w["demand_units"] for w in historical]
# Example: [920, 985, 1450, 1050, 1080, 1100, 1120, 1150, 1180, 1200, 1220, 1240]
```

**Step 5.2: Calculate Trend**
```python
n = len(demands)  # 12
avg_demand = sum(demands) / n  # 1137.9
recent_avg = sum(demands[-4:]) / 4  # (1180 + 1200 + 1220 + 1240) / 4 = 1210
trend_pct = ((recent_avg - avg_demand) / avg_demand) * 100  # 6.3% growth
```

**Step 5.3: Detect Anomalies**
```python
last_week = demands[-1]  # 1240
spike_detected = last_week > avg_demand * 1.3  # 1240 > 1479? False
```

**Step 5.4: Calculate Volatility**
```python
variance = sum((d - avg_demand) ** 2 for d in demands) / n
std_dev = math.sqrt(variance)  # Standard deviation ≈ 127.5
volatility_pct = (std_dev / avg_demand) * 100  # 11.2%
```

**Step 5.5: Generate Optimistic Scenario**
```python
for w in range(4):  # Next 4 weeks
    forecast = recent_avg * (1.15 + 0.03 * w) + random.gauss(0, 30)
    # Week 1: 1210 * 1.15 + noise = 1391
    # Week 2: 1210 * 1.18 + noise = 1427
    # Week 3: 1210 * 1.21 + noise = 1464
    # Week 4: 1210 * 1.24 + noise = 1500
    # Total: 5,782 units (probability: 20%)
```

**Step 5.6: Generate Base Scenario**
```python
for w in range(4):
    forecast = recent_avg * (1.0 + 0.01 * w) + random.gauss(0, 25)
    # Week 1: 1210 * 1.00 = 1210
    # Week 2: 1210 * 1.01 = 1222
    # Week 3: 1210 * 1.02 = 1234
    # Week 4: 1210 * 1.03 = 1246
    # Total: 4,912 units (probability: 55%)
```

**Step 5.7: Generate Pessimistic Scenario**
```python
for w in range(4):
    forecast = recent_avg * (0.82 - 0.02 * w) + random.gauss(0, 20)
    # Week 1: 1210 * 0.82 = 992
    # Week 2: 1210 * 0.80 = 968
    # Week 3: 1210 * 0.78 = 943
    # Week 4: 1210 * 0.76 = 919
    # Total: 3,822 units (probability: 25%)
```

**Step 5.8: Calculate Expected Weighted Demand**
```python
expected = (5782 * 0.20) + (4912 * 0.55) + (3822 * 0.25)
         = 1156 + 2702 + 955
         = 4813 units over 4 weeks
         = 1203 units/week average
```

**Output JSON:**
```json
{
  "product_id": "PROD-A",
  "forecast_horizon_weeks": 4,
  "historical_summary": {
    "weeks_analyzed": 12,
    "average_weekly_demand": 1138,
    "recent_4week_average": 1210,
    "trend": "Upward (+6.3%)",
    "volatility": "11.2%",
    "spike_detected": false
  },
  "scenarios": {
    "optimistic": {
      "probability_weight": 0.20,
      "weekly_forecast": [1391, 1427, 1464, 1500],
      "total_units": 5782,
      "assumptions": ["Viral momentum continues", "Trade show success", "Competitor issues"]
    },
    "base": {
      "probability_weight": 0.55,
      "weekly_forecast": [1210, 1222, 1234, 1246],
      "total_units": 4912,
      "assumptions": ["Steady growth", "Normal seasonality", "No disruptions"]
    },
    "pessimistic": {
      "probability_weight": 0.25,
      "weekly_forecast": [992, 968, 943, 919],
      "total_units": 3822,
      "assumptions": ["Price increases", "Competitor launch", "Economic slowdown"]
    }
  },
  "expected_weighted_demand": 4813,
  "confidence_interval_95pct": {"lower": 907, "upper": 1512}
}
```

##### TOOL 2: `analyze_demand_trends(product_id)`

**Location:** Lines 119-200

**Purpose:** Perform detailed trend analysis (slope, correlation, anomalies)

**Algorithm Steps:**

**Step 1: Linear Regression for Trend**
```python
# Calculate slope using least squares method
x_mean = (n - 1) / 2  # 5.5 (midpoint of 0-11)
y_mean = avg  # 1138
numerator = sum((i - x_mean) * (demands[i] - y_mean) for i in range(n))
denominator = sum((i - x_mean) ** 2 for i in range(n))
slope = numerator / denominator  # ≈ 24.5 units/week

direction = "Upward" if slope > 5 else "Downward" if slope < -5 else "Stable"
growth_rate_pct = (slope / avg) * 100  # 2.15% per week
```

**Step 2: Week-over-Week Changes**
```python
wow_changes = []
for i in range(1, n):
    change_pct = ((demands[i] - demands[i-1]) / demands[i-1]) * 100
    wow_changes.append(round(change_pct, 1))
# Example: [7.1%, 47.2%, -27.6%, 2.9%, 1.9%, 1.8%, 2.7%, 2.6%, 1.7%, 1.7%, 1.6%]
```

**Step 3: Detect Anomalies (>1.5 std dev from mean)**
```python
std_dev = 127.5
threshold = 1.5 * std_dev  # 191.25
anomalies = [
    {
        "week": "2026-W03",
        "demand": 1450,  # 312 units above average!
        "deviation_from_avg": 312,
        "z_score": 2.45,  # (1450 - 1138) / 127.5
        "had_promotion": True  # Explains the spike!
    }
]
```

**Step 4: Price-Demand Correlation**
```python
# Calculate Pearson correlation coefficient
prices = [88.50, 87.20, 89.10, ...]  # From historical data
price_avg = 88.50
cov = sum((demands[i] - avg) * (prices[i] - price_avg) for i in range(n)) / n
price_std = sqrt(sum((p - price_avg) ** 2 for p in prices) / n)
correlation = cov / (std_dev * price_std)  # -0.12 (weak negative)
```

**Output JSON:**
```json
{
  "product_id": "PROD-A",
  "trend_analysis": {
    "direction": "Upward",
    "slope_units_per_week": 24.5,
    "growth_rate_pct_per_week": 2.15
  },
  "demand_statistics": {
    "mean": 1138,
    "std_deviation": 127,
    "min": 920,
    "max": 1450,
    "coefficient_of_variation": 11.2
  },
  "week_over_week_changes_pct": [7.1, 47.2, -27.6, 2.9, 1.9, 1.8, 2.7, 2.6, 1.7, 1.7, 1.6],
  "anomalies_detected": [
    {
      "week": "2026-W03",
      "demand": 1450,
      "deviation_from_avg": 312,
      "z_score": 2.45,
      "had_promotion": true
    }
  ],
  "price_demand_correlation": {
    "correlation_coefficient": -0.12,
    "interpretation": "Weak/no correlation"
  },
  "market_context": {
    "season": "Q1",
    "industry_trend": "growing at 4.2% YoY",
    "social_media_mentions": {
      "volume": "2,400 mentions this week (up 180%)",
      "sentiment": "78% positive",
      "top_topic": "viral TikTok video featuring our product"
    }
  }
}
```

---

#### STEP 6: Database Sync (AI → Database Bridge)

**Location:** Backend → `backend/ai_database_bridge.py`

**Purpose:** Automatically insert AI forecast results into `demand_forecasts` table

**Code (Simplified):**
```python
class AIToDatabaseBridge:
    def sync_pipeline_results(self, pipeline_result: Dict) -> Dict:
        """Sync AI pipeline results to database"""
        changes = []

        # Extract demand forecasts from AI result
        demand_data = pipeline_result.get("demand_forecasting", {})
        scenarios = demand_data.get("scenarios", {})

        # Get weekly forecasts for next 4 weeks
        for week_num in range(1, 5):
            forecast_data = {
                "product_id": demand_data["product_id"],
                "week_number": current_week + week_num,
                "forecast_date": calculate_week_start_date(week_num),
                "optimistic": scenarios["optimistic"]["weekly_forecast"][week_num - 1],
                "base_case": scenarios["base"]["weekly_forecast"][week_num - 1],
                "pessimistic": scenarios["pessimistic"]["weekly_forecast"][week_num - 1],
                "actual": None  # Will be filled in later
            }

            # Insert into database
            forecast_id = create_demand_forecast(
                product_id=forecast_data["product_id"],
                week_number=forecast_data["week_number"],
                forecast_data=forecast_data
            )

            changes.append(f"Created forecast week {week_num}: {forecast_data['base_case']} units")

        return {
            "success": True,
            "changes_made": changes,
            "warnings": [],
            "errors": []
        }
```

**What Happens:**
1. Bridge extracts forecast data from AI result
2. For each of 4 weeks, creates a database record
3. Populates `optimistic`, `base_case`, `pessimistic` columns
4. Leaves `actual` as NULL (user fills in later)
5. Returns sync status to pipeline

**Database Result:**
```sql
-- After sync, database contains:
SELECT * FROM demand_forecasts WHERE product_id = 'PROD-A' ORDER BY week_number DESC LIMIT 4;

-- Results:
week_number | forecast_date | optimistic | base_case | pessimistic | actual
------------|---------------|------------|-----------|-------------|--------
11          | 2026-03-16    | 1427       | 1222      | 968         | NULL
12          | 2026-03-23    | 1464       | 1234      | 943         | NULL
13          | 2026-03-30    | 1500       | 1246      | 919         | NULL
14          | 2026-04-06    | 1537       | 1258      | 895         | NULL
```

---

#### STEP 7: Pipeline Completes, Frontend Updates

**Frontend Polling:**
```javascript
// Every 2 seconds, frontend checks status
const checkStatus = async () => {
  const response = await fetch(`http://localhost:8000/api/pipeline/runs/${runId}`)
  const data = await response.json()

  if (data.status === "completed") {
    // Show success message
    alert("Pipeline completed! Forecasts synced to database.")
    // Refresh Demand Intelligence page
    navigate('/demand-intelligence')
  } else if (data.status === "failed") {
    alert(`Pipeline failed: ${data.error}`)
  }
}
```

**Database Sync Status Display:**
```json
{
  "run_id": "a3f5b9c2-...",
  "status": "completed",
  "database_sync": {
    "success": true,
    "changes_made": [
      "Created forecast week 11: 1222 units",
      "Created forecast week 12: 1234 units",
      "Created forecast week 13: 1246 units",
      "Created forecast week 14: 1258 units"
    ],
    "warnings": [],
    "errors": []
  }
}
```

---

### 4.4 Pipeline Execution Time

| Stage | Duration | Bottleneck |
|-------|----------|-----------|
| User clicks button | <100ms | Network latency |
| Backend creates run_id | <50ms | UUID generation |
| Orchestrator starts | <200ms | Agent initialization |
| **Demand Agent runs** | **15-25 seconds** | **Anthropic API calls** |
| Inventory Agent runs | 12-18 seconds | Tool execution |
| Machine Agent runs | 10-15 seconds | Tool execution |
| Production Agent runs | 15-20 seconds | Tool execution |
| Supplier Agent runs | 12-18 seconds | Tool execution |
| Database sync | 1-2 seconds | SQLite writes |
| **TOTAL** | **65-100 seconds** | **AI reasoning time** |

**Why so long?**
- Each agent makes 2-3 LLM calls (Claude API)
- Each LLM call: 3-8 seconds (network + thinking time)
- Agents run sequentially (not parallel) to pass data between them

---

### 4.5 Pipeline Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    PIPELINE FLOW                             │
└──────────────────────────────────────────────────────────────┘

[User Clicks "Run Pipeline"]
         │
         ↓
[POST /api/pipeline/run] ────→ Create run_id ────→ Return immediately
         │                                                │
         ↓                                                │
[Background Task Starts]                                  │
         │                                                │
         ↓                                                │
┌─────────────────────────────┐                          │
│  ORCHESTRATOR AGENT         │                          │
│  Coordinates 5 agents       │                          │
└─────────────────────────────┘                          │
         │                                                │
         ├─────────────────────────────────┐             │
         ↓                                 ↓             │
┌─────────────────────┐         ┌──────────────────┐    │
│ DEMAND AGENT (1st)  │         │ Other 4 agents   │    │
│ ├─ simulate_demand_ │         │ run after demand │    │
│ │  scenarios()      │         │ completes        │    │
│ ├─ analyze_trends() │         └──────────────────┘    │
│ └─ Output: JSON     │                                  │
└─────────────────────┘                                  │
         │                                                │
         ↓                                                │
┌─────────────────────────────┐                          │
│  AI DATABASE BRIDGE         │                          │
│  ├─ Extract scenarios       │                          │
│  ├─ For each week (4):      │                          │
│  │   INSERT INTO            │                          │
│  │   demand_forecasts       │                          │
│  └─ Return sync status      │                          │
└─────────────────────────────┘                          │
         │                                                │
         ↓                                                │
[Database Updated] ─────────────────────────────────────→│
         │                                                │
         ↓                                                │
[Pipeline Status = "completed"] ←─────────────────────────┘
         │
         ↓
[Frontend Polls: Status = "completed"]
         │
         ↓
[User sees success message]
         │
         ↓
[Navigate to Demand Intelligence page]
         │
         ↓
[Page fetches new forecasts from database]
         │
         ↓
[Chart displays AI-generated forecasts]
```

---

## 5. AI AGENT & TOOLS

### 5.1 Agent Architecture

**Location:** `agents/demand_agent.py`

**Inheritance:**
```python
DemandForecastingAgent(BaseAgent)
    ↓
BaseAgent (uses LangChain)
    ↓
claude-3-5-sonnet (Anthropic API)
```

### 5.2 Agent Identity & Personality

**System Prompt** (Location: `prompts/demand_prompts.py` lines 15-79)

The agent is given a **role, expertise, and reasoning framework**:

```
You are the **Demand Forecasting Agent** in AMIS.

## YOUR ROLE
Senior demand planning expert with 15 years of manufacturing forecasting experience.
You don't just predict numbers — you REASON about demand, EXPLAIN thinking, RECOMMEND strategies.

## YOUR REASONING FRAMEWORK
1. PERCEIVE — Gather context (demand, market, inventory, capacity)
2. ANALYZE — Run tools (forecasts, trends, anomalies)
3. INTERPRET — Connect dots, explain what numbers MEAN
4. REASON — Evaluate trade-offs, pros/cons
5. RECOMMEND — Give specific action with confidence level
6. EXPLAIN — Show your work, acknowledge uncertainty

## CRITICAL RULES
- NEVER just return raw tool output. Always interpret and explain.
- NEVER give single number without uncertainty range.
- ALWAYS consider market context, not just historical patterns.
- ALWAYS flag anomalies and hypothesize causes.
- Think like a human expert who will be QUESTIONED by plant manager.
```

**Why This Matters:**
- LLM doesn't just execute tools mechanically
- It **reasons** like a human expert would
- Explains **why** it recommends something
- Acknowledges uncertainty and risks

### 5.3 Agent Tools (Detailed)

The agent has access to **3 main tools** (plus 3 optional advanced tools):

#### Tool 1: `get_demand_data_summary`

**Purpose:** Get complete picture before analysis

**When Used:** First tool call in any analysis

**What It Returns:**
```json
{
  "product_info": {"id": "PROD-A", "name": "Automotive Sensor Unit", "unit_cost": 52.00, "unit_price": 89.50},
  "historical_demand_last_12_weeks": [{week: "2026-W01", demand_units: 1107}, ...],
  "current_inventory": {"current_stock": 1850, "safety_stock": 300, "days_of_supply": 13},
  "market_context": {"season": "Q1", "industry_trend": "growing 4.2% YoY", ...},
  "production_capacity": {"max_daily_output": 220, "utilization_pct": 76}
}
```

**Code:** `tools/forecasting.py` lines 203-231

#### Tool 2: `simulate_demand_scenarios`

**Purpose:** Generate 3 probabilistic forecasts (Optimistic, Base, Pessimistic)

**When Used:** Main forecasting tool, called for every analysis

**Inputs:**
- `product_id`: "PROD-A"
- `horizon_weeks`: 4 (how many weeks to forecast)

**What It Returns:** (See Section 4.3 Step 5 for detailed algorithm)
```json
{
  "scenarios": {
    "optimistic": {"probability": 0.20, "weekly_forecast": [1391, 1427, 1464, 1500], "total": 5782},
    "base": {"probability": 0.55, "weekly_forecast": [1210, 1222, 1234, 1246], "total": 4912},
    "pessimistic": {"probability": 0.25, "weekly_forecast": [992, 968, 943, 919], "total": 3822}
  },
  "expected_weighted_demand": 4813,
  "confidence_interval_95pct": {"lower": 907, "upper": 1512}
}
```

**Code:** `tools/forecasting.py` lines 14-116

#### Tool 3: `analyze_demand_trends`

**Purpose:** Deep trend analysis (slope, volatility, anomalies, correlations)

**When Used:** To understand **why** demand is changing

**What It Returns:** (See Section 4.3 Step 5 for detailed algorithm)
```json
{
  "trend_analysis": {"direction": "Upward", "slope_units_per_week": 24.5, "growth_rate_pct": 2.15},
  "demand_statistics": {"mean": 1138, "std_deviation": 127, "coefficient_of_variation": 11.2},
  "anomalies_detected": [{week: "2026-W03", demand: 1450, z_score: 2.45, had_promotion: true}],
  "price_demand_correlation": {"correlation_coefficient": -0.12, "interpretation": "Weak"}
}
```

**Code:** `tools/forecasting.py` lines 119-200

### 5.4 How Agent Interprets Tool Results (Intelligence Layer)

**Example Agent Response:**

**User Prompt:**
> "Give me a demand forecast for PROD-A for the next 4 weeks"

**What Agent Does:**

**Step 1: Agent calls tools**
```python
# Behind the scenes (LangChain handles this):
data_summary = get_demand_data_summary.invoke({"product_id": "PROD-A"})
scenarios = simulate_demand_scenarios.invoke({"product_id": "PROD-A", "horizon_weeks": 4})
trends = analyze_demand_trends.invoke({"product_id": "PROD-A"})
```

**Step 2: Agent reasons about results**
```
Claude (thinking):
- Historical average: 1138 units/week
- Recent 4-week average: 1210 units/week (up 6.3%)
- Detected anomaly in week 3 (1450 units) - had promotion
- Trend: Upward at 2.15% per week
- Base case forecast: 1228 units/week average
- But social media mentions up 180% (viral TikTok video!)
- This could be temporary spike OR sustainable growth
```

**Step 3: Agent generates human-like response**

```markdown
## Situation Assessment
PROD-A (Automotive Sensor Unit) is experiencing upward demand momentum. Recent 4-week
average (1,210 units/week) is 6.3% above the 12-week average (1,138 units/week).

## Key Findings
I've generated three demand scenarios for the next 4 weeks:

1. **Base Case (55% probability)**: 4,912 total units (1,228/week average)
   - Assumes viral spike normalizes, steady 1% weekly growth continues
   - Most likely outcome based on historical patterns

2. **Optimistic (20% probability)**: 5,782 total units (1,445/week average)
   - Assumes viral momentum sustains, trade show generates new contracts
   - Competitor supply issues persist

3. **Pessimistic (25% probability)**: 3,822 total units (956/week average)
   - Assumes raw material price increases dampen demand
   - Competitor's new product captures market share

**Expected Weighted Demand**: 4,813 total units over 4 weeks (1,203/week)
**95% Confidence Interval**: 907 - 1,512 units/week

## Interpretation (This Is Where I Add Intelligence)

The recent spike to 1,450 units in week 3 was accompanied by a promotion AND
a viral TikTok video (2,400 social media mentions, up 180%). This is a
**compounding effect** - hard to separate organic growth from promotion-driven spike.

However, the trend analysis shows a consistent 2.15% weekly growth BEFORE the spike,
suggesting underlying demand strength beyond the viral moment.

**What concerns me**:
- Current inventory (1,850 units) = only 13 days of supply at expected demand
- If optimistic scenario plays out, we'll hit stockout in 9 days
- Social media sentiment (78% positive) could sustain, OR could fade in 2 weeks

## Recommendation

**Produce to the Base Case + 10% buffer**:
- Target: 5,400 units over 4 weeks (1,350/week)
- This covers Base Case (4,912) + 10% safety margin (488 units)
- Keeps us below Optimistic scenario to avoid overproduction risk

**Why this strategy**:
- Protects against stockout if viral momentum continues (Optimistic scenario)
- Avoids massive overproduction if demand normalizes (Base scenario)
- 10% buffer costs less than stockout penalties ($45/unit)

**Confidence Level**: 70%

**What could change my mind**:
- If social media mentions drop below 1,000 next week → reduce to Base Case only
- If major client contract renews early (due in 2 weeks) → increase to Optimistic
- If competitor's new product launches → shift to Pessimistic planning

## Cross-Agent Alerts

**→ Inventory Agent**: Current 13 days of supply is TIGHT. Need to accelerate
   incoming orders (Supplier A: 500 units ETA 4 days, Supplier B: 300 units ETA 7 days).
   Recommend advancing Supplier B delivery by 3 days if possible.

**→ Production Agent**: Plan for 1,350 units/week production. Current capacity
   (220/day) supports this with 7-day weeks (1,540/week). No overtime needed if
   we run full 7 days. If maintaining 5-day weeks, need 12 hours overtime/week.

**→ Supplier Agent**: If we commit to Optimistic scenario (1,445/week), raw
   material requirements increase by 18%. Confirm supplier capacity BEFORE
   committing to large customer orders.
```

**This is the intelligence layer** - the agent:
- Connects multiple data points (promotion + viral video + trend)
- Identifies risks (tight inventory, social media volatility)
- Recommends specific action (Base + 10% buffer)
- States confidence level (70%)
- Explains what could change the decision
- Alerts other agents proactively

---

## 6. CALCULATION LOGIC & FORMULAS

### 6.1 Frontend Calculations (Real-Time Insights)

**Location:** `frontend/src/pages/DemandIntelligence.jsx` lines 42-71

The frontend calculates real-time insights from database data (NOT from AI):

#### 6.1.1 Average Weekly Demand (Base Case)

**Formula:**
```javascript
const avgBase = forecastData.reduce((sum, f) => sum + (f.base_case || 0), 0) / forecastData.length
```

**Example Calculation:**
```
Forecast Data from Database:
Week 10: base_case = 1050
Week 11: base_case = 1075
Week 12: base_case = 1100
Week 13: base_case = 1125

avgBase = (1050 + 1075 + 1100 + 1125) / 4 = 4350 / 4 = 1087.5 ≈ 1088 units
```

**Displayed As:** "1,088 units" (with comma formatting)

---

#### 6.1.2 Trend Direction & Percent

**Formula:**
```javascript
// Simple linear regression slope (change from first to last week divided by number of weeks)
const trend = forecastData.length > 1
  ? ((forecastData[forecastData.length - 1]?.base_case || 0) - (forecastData[0]?.base_case || 0)) / forecastData.length
  : 0

const trendDirection = trend > 0 ? 'Upward' : trend < 0 ? 'Downward' : 'Stable'
const trendPercent = avgBase > 0 ? ((trend / avgBase) * 100).toFixed(1) : 0
```

**Example Calculation:**
```
First week (week 10): base_case = 1050
Last week (week 13): base_case = 1125
Number of weeks: 4

trend = (1125 - 1050) / 4 = 75 / 4 = 18.75 units/week growth

trendDirection = 'Upward' (since 18.75 > 0)

trendPercent = (18.75 / 1088) * 100 = 1.72% ≈ 1.7%
```

**Displayed As:** "Upward" with badge "+1.7% per week"

---

#### 6.1.3 Forecasts Entered vs Actuals Recorded

**Formula:**
```javascript
const forecastsEntered = forecastData.length
const actualsRecorded = forecastData.filter(f => f.actual !== null && f.actual !== undefined).length
```

**Example Calculation:**
```
Forecast Data:
Week 10: base_case = 1050, actual = NULL
Week 11: base_case = 1075, actual = NULL
Week 12: base_case = 1100, actual = 1095
Week 13: base_case = 1125, actual = 1130

forecastsEntered = 4 weeks
actualsRecorded = 2 (weeks 12 and 13 have actuals)
```

**Displayed As:** "4 weeks" with subtitle "2 with actuals recorded"

---

### 6.2 AI Tool Calculations (Detailed Algorithms)

#### 6.2.1 Standard Deviation (Volatility Measure)

**Formula:**
```python
variance = sum((d - avg_demand) ** 2 for d in demands) / n
std_dev = math.sqrt(variance)
```

**Example Calculation:**
```
Historical Demand: [920, 985, 1450, 1050, 1080, 1100, 1120, 1150, 1180, 1200, 1220, 1240]
Average (avg_demand): 1137.9

Step 1: Calculate squared differences
(920 - 1137.9)² = 47477.61
(985 - 1137.9)² = 23379.61
(1450 - 1137.9)² = 97424.41
(1050 - 1137.9)² = 7726.41
(1080 - 1137.9)² = 3351.61
(1100 - 1137.9)² = 1437.61
(1120 - 1137.9)² = 320.41
(1150 - 1137.9)² = 146.41
(1180 - 1137.9)² = 1772.41
(1200 - 1137.9)² = 3852.41
(1220 - 1137.9)² = 6740.41
(1240 - 1137.9)² = 10422.41

Step 2: Sum squared differences
Sum = 204051.33

Step 3: Divide by n (variance)
variance = 204051.33 / 12 = 17004.28

Step 4: Square root (standard deviation)
std_dev = √17004.28 = 130.4 units

Coefficient of Variation (CV) = (130.4 / 1137.9) × 100 = 11.5%
```

**Interpretation:**
- **Low CV (<10%)**: Stable, predictable demand
- **Medium CV (10-20%)**: Moderate variability (this product)
- **High CV (>20%)**: Volatile, hard to predict

---

#### 6.2.2 Linear Regression (Trend Slope)

**Formula (Least Squares Method):**
```python
x_mean = (n - 1) / 2
y_mean = avg_demand
numerator = sum((i - x_mean) * (demands[i] - y_mean) for i in range(n))
denominator = sum((i - x_mean) ** 2 for i in range(n))
slope = numerator / denominator
```

**Example Calculation:**
```
n = 12 weeks
x_mean = (12 - 1) / 2 = 5.5
y_mean = 1137.9

Calculate numerator (covariance × n):
i=0: (0 - 5.5) × (920 - 1137.9) = (-5.5) × (-217.9) = 1198.45
i=1: (1 - 5.5) × (985 - 1137.9) = (-4.5) × (-152.9) = 688.05
i=2: (2 - 5.5) × (1450 - 1137.9) = (-3.5) × (312.1) = -1092.35
i=3: (3 - 5.5) × (1050 - 1137.9) = (-2.5) × (-87.9) = 219.75
i=4: (4 - 5.5) × (1080 - 1137.9) = (-1.5) × (-57.9) = 86.85
i=5: (5 - 5.5) × (1100 - 1137.9) = (-0.5) × (-37.9) = 18.95
i=6: (6 - 5.5) × (1120 - 1137.9) = (0.5) × (-17.9) = -8.95
i=7: (7 - 5.5) × (1150 - 1137.9) = (1.5) × (12.1) = 18.15
i=8: (8 - 5.5) × (1180 - 1137.9) = (2.5) × (42.1) = 105.25
i=9: (9 - 5.5) × (1200 - 1137.9) = (3.5) × (62.1) = 217.35
i=10: (10 - 5.5) × (1220 - 1137.9) = (4.5) × (82.1) = 369.45
i=11: (11 - 5.5) × (1240 - 1137.9) = (5.5) × (102.1) = 561.55

Sum (numerator) = 3382.5

Calculate denominator (variance of x × n):
sum((i - 5.5)² for i in range(12)) = 143

slope = 3382.5 / 143 = 23.65 units/week

Growth Rate % = (23.65 / 1137.9) × 100 = 2.08% per week
```

**Interpretation:**
- **Positive slope**: Demand is growing
- **Negative slope**: Demand is declining
- **Slope near 0**: Stable demand
- **Growth rate >5%/week**: Rapid growth (investigate why!)

---

#### 6.2.3 Z-Score (Anomaly Detection)

**Formula:**
```python
z_score = (demand - avg_demand) / std_dev
anomaly_threshold = 1.5  # Standard: >1.5 std dev = anomaly
```

**Example Calculation:**
```
Week 3 Demand: 1450 units
Average Demand: 1137.9 units
Standard Deviation: 130.4 units

z_score = (1450 - 1137.9) / 130.4 = 312.1 / 130.4 = 2.39

Interpretation:
- z_score > 1.5: Anomaly detected! ✓
- z_score > 2.0: Strong anomaly (this is 2.39, very unusual)
```

**Statistical Meaning:**
- **z = 1.5**: 93% of normal data falls below this → 7% outlier
- **z = 2.0**: 97.7% of normal data falls below this → 2.3% outlier
- **z = 2.39**: 99.2% of normal data falls below this → 0.8% outlier (very rare!)

**Business Action:**
- Agent investigates: Week 3 had promotion → explains the spike
- If NO promotion: Could indicate data error OR real demand surge

---

#### 6.2.4 Expected Weighted Demand

**Formula:**
```python
expected_demand = sum(scenario["total_units"] × scenario["probability"] for scenario in scenarios)
```

**Example Calculation:**
```
Scenarios (4-week totals):
- Optimistic: 5,782 units × 0.20 probability = 1,156.4
- Base:       4,912 units × 0.55 probability = 2,701.6
- Pessimistic: 3,822 units × 0.25 probability = 955.5

Expected Weighted Demand = 1,156.4 + 2,701.6 + 955.5 = 4,813.5 units
Weekly Average = 4,813.5 / 4 = 1,203.4 ≈ 1,203 units/week
```

**Why Weighted?**
- Simple average: (5,782 + 4,912 + 3,822) / 3 = 4,839 (WRONG!)
- Weighted average accounts for probability (Base is most likely at 55%)
- More accurate for decision-making

---

#### 6.2.5 Confidence Interval (95%)

**Formula (Simplified):**
```python
lower_bound = recent_avg × 0.75
upper_bound = recent_avg × 1.25
```

**Example Calculation:**
```
Recent 4-week Average: 1,210 units/week

Lower Bound (95% CI) = 1,210 × 0.75 = 907 units/week
Upper Bound (95% CI) = 1,210 × 1.25 = 1,512 units/week
```

**Interpretation:**
- 95% probability that actual demand will fall between 907 and 1,512 units/week
- If actual demand is 1,600: Outside confidence interval → investigate why!
- Used for risk planning: "What if demand hits upper bound? Do we have capacity?"

**Note:** This is a simplified calculation. Production-grade systems use Student's t-distribution for more accurate confidence intervals with small sample sizes.

---

### 6.3 Validation Formulas

#### How to Manually Verify "Average Weekly Demand"

**Step 1: Query Database**
```sql
SELECT base_case FROM demand_forecasts WHERE product_id = 'PROD-A' ORDER BY week_number LIMIT 12;
```

**Step 2: Calculate Average**
```
Results: [1050, 1075, 1100, 1125, 1150, 1175, 1200, 1225, 1250, 1275, 1300, 1325]

Manual Calculation:
Sum = 1050 + 1075 + 1100 + ... + 1325 = 14,250
Average = 14,250 / 12 = 1,187.5 ≈ 1,188 units
```

**Step 3: Compare to UI**
- UI should show: "1,188 units" (or "1.2K units" if abbreviated)
- If different: Check if UI is filtering by product_id correctly

---

#### How to Manually Verify "Trend Direction"

**Step 1: Query First and Last Week**
```sql
SELECT base_case FROM demand_forecasts WHERE product_id = 'PROD-A' ORDER BY week_number ASC LIMIT 1;
-- Result: 1050

SELECT base_case FROM demand_forecasts WHERE product_id = 'PROD-A' ORDER BY week_number DESC LIMIT 1;
-- Result: 1325
```

**Step 2: Calculate Trend**
```
trend = (last - first) / count
trend = (1325 - 1050) / 12 = 275 / 12 = 22.9 units/week

trendPercent = (22.9 / 1188) × 100 = 1.93% ≈ 1.9%
```

**Step 3: Compare to UI**
- UI should show: "Upward" with "+1.9% per week"
- Direction Logic: 22.9 > 0 → Upward ✓

---

## 7. DATA FLOW: BACKEND TO FRONTEND

### 7.1 API Endpoints (Complete Reference)

#### 7.1.1 GET `/api/demand/forecasts/{product_id}`

**Purpose:** Fetch forecast data for charts and insights

**Request:**
```http
GET http://localhost:8000/api/demand/forecasts/PROD-A?weeks=12
```

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `weeks` | integer | No | 12 | How many weeks of forecasts to return |

**Response (Success - 200):**
```json
{
  "forecasts": [
    {
      "id": 1,
      "product_id": "PROD-A",
      "week_number": 10,
      "forecast_date": "2026-03-09",
      "optimistic": 1250,
      "base_case": 1050,
      "pessimistic": 850,
      "actual": null,
      "created_at": "2026-03-04T10:23:45"
    },
    ...
  ]
}
```

**Response (Empty - 200):**
```json
{
  "forecasts": []
}
```

**Error Responses:**
- `500 Internal Server Error`: Database connection failed

**Backend Code:**
```python
@app.get("/api/demand/forecasts/{product_id}")
async def get_forecasts(product_id: str, weeks: int = 12):
    """Get demand forecasts for a product"""
    try:
        forecasts = get_demand_forecasts(product_id, weeks)
        return {"forecasts": forecasts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

#### 7.1.2 POST `/api/demand/forecasts/{product_id}`

**Purpose:** Create new manual forecast entry

**Request:**
```http
POST http://localhost:8000/api/demand/forecasts/PROD-A
Content-Type: application/json

{
  "week_number": 15,
  "forecast_date": "2026-04-13",
  "optimistic": 1350,
  "base_case": 1150,
  "pessimistic": 950,
  "actual": null
}
```

**Request Body Schema:**
```json
{
  "week_number": "integer (1-53, required)",
  "forecast_date": "string (YYYY-MM-DD format, required)",
  "optimistic": "integer (units, required)",
  "base_case": "integer (units, required)",
  "pessimistic": "integer (units, required)",
  "actual": "integer (units, optional, default: null)"
}
```

**Validation Rules:**
- `optimistic >= base_case >= pessimistic` (enforced in frontend)
- `week_number` must be 1-53
- `forecast_date` must be valid date
- All unit values must be >= 0

**Response (Success - 201):**
```json
{
  "forecast_id": 42,
  "message": "Forecast created successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input data
- `409 Conflict`: Forecast for this week already exists
- `500 Internal Server Error`: Database write failed

**Backend Code:**
```python
@app.post("/api/demand/forecasts/{product_id}")
async def create_forecast(product_id: str, forecast_data: ForecastCreate):
    """Create new demand forecast"""
    try:
        forecast_id = create_demand_forecast(
            product_id=product_id,
            week_number=forecast_data.week_number,
            forecast_data=forecast_data.dict()
        )
        return {"forecast_id": forecast_id, "message": "Forecast created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

#### 7.1.3 PATCH `/api/demand/forecasts/{product_id}/{week_number}`

**Purpose:** Update actual demand after week completes

**Request:**
```http
PATCH http://localhost:8000/api/demand/forecasts/PROD-A/10
Content-Type: application/json

{
  "actual": 1095
}
```

**Response (Success - 200):**
```json
{
  "message": "Actual demand updated successfully",
  "product_id": "PROD-A",
  "week_number": 10,
  "actual": 1095
}
```

**Error Responses:**
- `404 Not Found`: No forecast found for this week
- `400 Bad Request`: Invalid actual value
- `500 Internal Server Error`: Database update failed

---

### 7.2 Frontend API Client

**Location:** `frontend/src/lib/api.js`

**Usage in Component:**
```javascript
import { apiClient } from '../lib/api'

// Fetch forecasts
const { data } = await apiClient.getDemandForecasts('PROD-A', 12)

// Create forecast
await apiClient.createDemandForecast('PROD-A', 15, {
  forecast_date: '2026-04-13',
  optimistic: 1350,
  base_case: 1150,
  pessimistic: 950
})

// Update actual
await apiClient.updateActualDemand('PROD-A', 10, 1095)
```

---

### 7.3 React Query Integration

**Location:** `frontend/src/pages/DemandIntelligence.jsx` lines 19-37

**Caching Strategy:**
```javascript
const { data: forecastsData, isLoading, refetch } = useQuery({
  queryKey: ['demand-forecasts', selectedProduct],  // Cache key
  queryFn: async () => {
    const response = await apiClient.getDemandForecasts(selectedProduct, 12)
    return response.data.forecasts
  },
  staleTime: 60000,  // Data considered fresh for 1 minute
  cacheTime: 300000  // Cache persists for 5 minutes
})
```

**Benefits:**
- **Automatic Caching**: Second page load is instant (no API call)
- **Refetch on Focus**: When user returns to tab, data refreshes
- **Loading States**: `isLoading` automatically managed
- **Optimistic Updates**: `refetch()` manually triggers refresh

---

### 7.4 Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│              USER OPENS DEMAND INTELLIGENCE PAGE                │
│              http://localhost:5173/demand-intelligence          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  REACT COMPONENT MOUNTS                                         │
│  DemandIntelligence.jsx                                         │
│                                                                  │
│  useQuery triggers:                                             │
│    queryKey: ['demand-forecasts', 'PROD-A']                    │
│    queryFn: apiClient.getDemandForecasts('PROD-A', 12)         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP GET Request
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  API ENDPOINT                                                    │
│  GET /api/demand/forecasts/PROD-A?weeks=12                      │
│                                                                  │
│  Backend (FastAPI) receives request                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Database Query
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  DATABASE QUERY EXECUTES                                         │
│                                                                  │
│  SELECT * FROM demand_forecasts                                 │
│  WHERE product_id = 'PROD-A'                                    │
│  ORDER BY week_number                                            │
│  LIMIT 12                                                        │
│                                                                  │
│  Returns 12 rows                                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ JSON Response
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND RECEIVES DATA                                          │
│                                                                  │
│  forecastData = [                                               │
│    {id: 1, week_number: 10, base_case: 1050, ...},             │
│    {id: 2, week_number: 11, base_case: 1075, ...},             │
│    ...                                                           │
│  ]                                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND CALCULATES INSIGHTS                                    │
│                                                                  │
│  avgBase = forecastData.reduce(sum) / length                   │
│  trend = (last.base_case - first.base_case) / length           │
│  actualsRecorded = forecastData.filter(f => f.actual != null)  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  UI RENDERS                                                      │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Average Weekly Demand:  1,088 units                     │   │
│  │ Trend Direction:        Upward (+1.7% per week)         │   │
│  │ Forecasts Entered:      12 weeks (2 with actuals)       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ [AREA CHART]                                            │   │
│  │   - Green area: Optimistic scenario                     │   │
│  │   - Blue area: Base case scenario                       │   │
│  │   - Red area: Pessimistic scenario                      │   │
│  │   - Purple line: Actual demand (where recorded)         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. UI COMPONENTS & DISPLAY

### 8.1 Page Structure

**Location:** `frontend/src/pages/DemandIntelligence.jsx`

**Component Hierarchy:**
```
DemandIntelligence
  ├─ Page Header
  │   ├─ Title ("Demand Intelligence")
  │   ├─ Product Selector (dropdown)
  │   ├─ "Import from AI" button
  │   └─ "Add Forecast" button
  │
  ├─ Metric Cards Row (3 cards)
  │   ├─ MetricCard: Average Weekly Demand
  │   ├─ MetricCard: Forecasts Entered
  │   └─ MetricCard: Trend Direction
  │
  ├─ Forecast Chart Card
  │   ├─ CardHeader: Title + Description
  │   └─ CardContent: Recharts AreaChart
  │       ├─ XAxis: Week dates
  │       ├─ YAxis: Units
  │       ├─ Area: Pessimistic (red)
  │       ├─ Area: Base Case (blue)
  │       ├─ Area: Optimistic (green)
  │       └─ Line: Actual (purple, bold)
  │
  ├─ Forecast Analysis Card
  │   ├─ Summary box (blue): Forecast counts, averages
  │   ├─ Trend box (green/yellow): Trend direction, recommendations
  │   ├─ Action box (amber): Prompt to record actuals
  │   └─ Accuracy box (purple): Forecast tracking status
  │
  └─ ForecastInputModal (when visible)
      ├─ Product ID (read-only)
      ├─ Week Number (input)
      ├─ Forecast Date (date picker)
      ├─ Optimistic Scenario (input)
      ├─ Base Case (input)
      ├─ Pessimistic Scenario (input)
      ├─ Actual Demand (input, optional)
      └─ Submit button
```

### 8.2 Metric Cards (Detailed)

#### Card 1: Average Weekly Demand

**Visual:**
```
┌────────────────────────────────────────────┐
│  📈                                        │
│                                            │
│  Average Weekly Demand                     │
│                                            │
│  1,088 units              +1.7%           │
│                                            │
│  Base case forecast average                │
└────────────────────────────────────────────┘
```

**Data Source:**
```javascript
const avgBase = insights.avgBase.toLocaleString()  // 1088 → "1,088"
const trend = insights.trend > 0 ? `+${insights.trendPercent}%` : `${insights.trendPercent}%`
```

**Color Coding:**
- Trend positive (+1.7%): Green text
- Trend negative (-1.7%): Red text
- Trend neutral (0%): Gray text

---

#### Card 2: Forecasts Entered

**Visual:**
```
┌────────────────────────────────────────────┐
│  📊                                        │
│                                            │
│  Forecasts Entered                         │
│                                            │
│  12 weeks                                  │
│                                            │
│  2 with actuals recorded                   │
└────────────────────────────────────────────┘
```

**Data Source:**
```javascript
const forecastsEntered = forecastData.length  // 12
const actualsRecorded = forecastData.filter(f => f.actual !== null).length  // 2
```

**Business Meaning:**
- **12 weeks**: Total forecast horizon (how far ahead we've planned)
- **2 actuals**: How many weeks have completed and actual demand recorded
- **Ratio 2/12**: 16.7% of forecasts validated with actuals (low - need more tracking!)

---

#### Card 3: Trend Direction

**Visual (Upward Trend):**
```
┌────────────────────────────────────────────┐
│  📈                        [Growing]       │
│                                            │
│  Trend Direction                           │
│                                            │
│  Upward                                    │
│                                            │
│  +1.7% per week                            │
└────────────────────────────────────────────┘
```

**Visual (Downward Trend):**
```
┌────────────────────────────────────────────┐
│  📉                      [Declining]       │
│                                            │
│  Trend Direction                           │
│                                            │
│  Downward                                  │
│                                            │
│  -2.3% per week                            │
└────────────────────────────────────────────┘
```

**Badge Logic:**
```javascript
badge = insights.trend > 0 ? "Growing" : insights.trend < 0 ? "Declining" : null
```

---

### 8.3 Area Chart (Recharts Configuration)

**Chart Type:** Stacked Area Chart with overlay line

**Location:** Lines 216-280

**Configuration:**

| Element | Property | Value | Visual Effect |
|---------|----------|-------|---------------|
| **Pessimistic Area** | `stroke` | `#ef4444` (red) | Red border line |
| | `fill` | `#fee2e2` (light red) | Light red fill |
| | `stackId` | `1` | Stacks independently |
| | `name` | "Conservative Scenario (25% prob)" | Tooltip label |
| **Base Case Area** | `stroke` | `#0ea5e9` (blue) | Blue border line |
| | `fill` | `#dbeafe` (light blue) | Light blue fill |
| | `stackId` | `2` | Stacks independently |
| | `name` | "Base Case Forecast (55% prob)" | Tooltip label |
| **Optimistic Area** | `stroke` | `#10b981` (green) | Green border line |
| | `fill` | `#d1fae5` (light green) | Light green fill |
| | `stackId` | `3` | Stacks independently |
| | `name` | "Optimistic Scenario (20% prob)" | Tooltip label |
| **Actual Line** | `stroke` | `#8b5cf6` (purple) | Purple line |
| | `strokeWidth` | `3` | Bold line (3px) |
| | `dot` | `{r: 6}` | Large dots (6px radius) |
| | `name` | "Actual" | Tooltip label |

**Why 3 Separate Stacks?**
- Each area renders independently (not stacked on top of each other)
- User sees 3 scenario bands + actual overlay
- Easy to compare actual vs each scenario visually

**X-Axis Formatting:**
```javascript
tickFormatter={(date) => {
  const d = new Date(date)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}}
// "2026-03-09" → "Mar 9"
```

**Y-Axis Label:** "Units" (vertical, left side)

**Tooltip Customization:**
```javascript
labelFormatter={(date) => {
  const d = new Date(date)
  return `Week of ${d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
}}
// "2026-03-09" → "Week of Mar 9, 2026"

formatter={(value, name) => {
  return [value.toLocaleString() + ' units', name]
}}
// 1050 → "1,050 units"
```

**Empty State:**
```javascript
{forecastData.length === 0 ? (
  <div className="text-center py-12">
    <p className="text-gray-500">No forecast data for {selectedProduct}</p>
    <button onClick={() => setShowForecastModal(true)}>
      Add First Forecast
    </button>
  </div>
) : (
  <AreaChart data={forecastData}>...</AreaChart>
)}
```

---

### 8.4 Forecast Analysis Boxes

#### Box 1: Forecast Summary (Blue)

**Visual:**
```
┌─────────────────────────────────────────────────────────┐
│ 📊 Forecast Summary                                     │
│                                                         │
│ 12 weeks of forecast data entered                      │
│ 2 weeks with actual demand recorded                    │
│ Average base case: 1,088 units/week                    │
│ Range: 950 (conservative) to 1,250 (optimistic)        │
└─────────────────────────────────────────────────────────┘
```

**When Shown:** Always (if insights exist)

**Data Source:**
```javascript
insights.forecastsEntered  // 12
insights.actualsRecorded  // 2
insights.avgBase  // 1088
insights.avgPessimistic  // 950
insights.avgOptimistic  // 1250
```

---

#### Box 2: Trend Alert (Green/Yellow)

**Visual (Upward Trend - Green):**
```
┌─────────────────────────────────────────────────────────┐
│ 📈 Upward Trend Detected                                │
│                                                         │
│ Demand forecast shows an upward trend (+1.7% per week). │
│ Consider increasing production capacity or supplier     │
│ orders to meet growing demand.                          │
└─────────────────────────────────────────────────────────┘
```

**Visual (Downward Trend - Yellow):**
```
┌─────────────────────────────────────────────────────────┐
│ 📉 Downward Trend Detected                              │
│                                                         │
│ Demand forecast shows a downward trend (-2.3% per week).│
│ Review production schedules and inventory levels to     │
│ avoid overstock.                                         │
└─────────────────────────────────────────────────────────┘
```

**When Shown:** Only if `insights.trend !== 0` (non-zero trend)

**Color Logic:**
```javascript
const bgColor = insights.trend > 0 ? 'bg-green-50' : 'bg-yellow-50'
const borderColor = insights.trend > 0 ? 'border-green-200' : 'border-yellow-200'
const textColor = insights.trend > 0 ? 'text-green-900' : 'text-yellow-900'
```

---

#### Box 3: Action Needed (Amber)

**Visual:**
```
┌─────────────────────────────────────────────────────────┐
│ ⚠️ Action Needed: Track Actual Demand                   │
│                                                         │
│ No actual demand data recorded yet. Once weeks pass,    │
│ update forecasts with actual sales to measure forecast  │
│ accuracy and improve future predictions.                │
└─────────────────────────────────────────────────────────┘
```

**When Shown:** Only if `insights.actualsRecorded === 0`

**Purpose:** Prompt user to start tracking actuals for forecast accuracy

---

#### Box 4: Accuracy Tracking (Purple)

**Visual:**
```
┌─────────────────────────────────────────────────────────┐
│ ✅ Forecast Accuracy Tracking Active                    │
│                                                         │
│ 2 weeks have actual demand recorded. Continue tracking  │
│ to calculate forecast accuracy (MAPE) and improve       │
│ planning precision.                                      │
└─────────────────────────────────────────────────────────┘
```

**When Shown:** Only if `insights.actualsRecorded > 0`

**Future Enhancement:** Calculate MAPE (Mean Absolute Percentage Error)
```
MAPE = (1/n) × Σ |actual - forecast| / actual × 100%
```

---

## 9. VALIDATION & TESTING

### 9.1 Database Validation Queries

#### 9.1.1 Check if Forecasts Exist

**Query:**
```sql
SELECT COUNT(*) as forecast_count
FROM demand_forecasts
WHERE product_id = 'PROD-A';
```

**Expected Result:**
```
forecast_count
--------------
12
```

**If Result = 0:**
- Pipeline has NOT been run yet
- OR database sync failed
- **Fix:** Run pipeline manually from UI

---

#### 9.1.2 Verify Forecast Data Quality

**Query:**
```sql
SELECT
    week_number,
    optimistic,
    base_case,
    pessimistic,
    actual,
    CASE
        WHEN optimistic >= base_case AND base_case >= pessimistic THEN 'VALID'
        ELSE 'INVALID'
    END as data_quality
FROM demand_forecasts
WHERE product_id = 'PROD-A'
ORDER BY week_number;
```

**Expected Result:**
```
week_number | optimistic | base_case | pessimistic | actual | data_quality
------------|------------|-----------|-------------|--------|-------------
10          | 1250       | 1050      | 850         | NULL   | VALID
11          | 1280       | 1075      | 870         | NULL   | VALID
12          | 1310       | 1100      | 890         | 1095   | VALID
```

**If Data Quality = 'INVALID':**
- Manual data entry error (user entered optimistic < base_case)
- **Fix:** Update record with correct values

---

#### 9.1.3 Calculate Average Manually (Cross-Check UI)

**Query:**
```sql
SELECT
    AVG(base_case) as avg_base_case,
    MIN(base_case) as min_base,
    MAX(base_case) as max_base,
    COUNT(*) as week_count
FROM demand_forecasts
WHERE product_id = 'PROD-A';
```

**Expected Result:**
```
avg_base_case | min_base | max_base | week_count
--------------|----------|----------|------------
1087.5        | 1050     | 1325     | 12
```

**Compare to UI:**
- UI "Average Weekly Demand" should show: **1,088 units** (rounded)
- UI "Trend Direction" range should be min_base to max_base

---

### 9.2 API Endpoint Testing (Postman/cURL)

#### 9.2.1 Test GET Forecasts Endpoint

**cURL Command:**
```bash
curl -X GET "http://localhost:8000/api/demand/forecasts/PROD-A?weeks=12" \
  -H "accept: application/json"
```

**Expected Response (200 OK):**
```json
{
  "forecasts": [
    {
      "id": 1,
      "product_id": "PROD-A",
      "week_number": 10,
      "forecast_date": "2026-03-09",
      "optimistic": 1250,
      "base_case": 1050,
      "pessimistic": 850,
      "actual": null,
      "created_at": "2026-03-04T10:23:45"
    }
  ]
}
```

**If Response is Empty `{"forecasts": []}`:**
- No data in database for PROD-A
- Run pipeline to generate forecasts

---

#### 9.2.2 Test CREATE Forecast Endpoint

**cURL Command:**
```bash
curl -X POST "http://localhost:8000/api/demand/forecasts/PROD-A" \
  -H "Content-Type: application/json" \
  -d '{
    "week_number": 25,
    "forecast_date": "2026-06-15",
    "optimistic": 1400,
    "base_case": 1200,
    "pessimistic": 1000,
    "actual": null
  }'
```

**Expected Response (201 Created):**
```json
{
  "forecast_id": 43,
  "message": "Forecast created successfully"
}
```

**Verify in Database:**
```sql
SELECT * FROM demand_forecasts WHERE id = 43;
```

---

### 9.3 Frontend Calculation Validation

#### 9.3.1 Test Trend Calculation

**Scenario:** User has 4 weeks of forecasts
```
Week 10: base_case = 1000
Week 11: base_case = 1050
Week 12: base_case = 1100
Week 13: base_case = 1150
```

**Expected Calculations:**

**Average:**
```
avgBase = (1000 + 1050 + 1100 + 1150) / 4 = 4300 / 4 = 1075 units
```

**Trend:**
```
trend = (1150 - 1000) / 4 = 150 / 4 = 37.5 units/week
trendDirection = "Upward" (since 37.5 > 0)
trendPercent = (37.5 / 1075) × 100 = 3.49% ≈ 3.5%
```

**UI Should Show:**
- Average Weekly Demand: **1,075 units**
- Trend Direction: **Upward**
- Trend Badge: **+3.5% per week**

**How to Verify:**
1. Open browser DevTools → Console
2. Type: `console.log(insights)`
3. Check: `insights.avgBase === 1075` and `insights.trendPercent === "3.5"`

---

#### 9.3.2 Test Empty State Handling

**Scenario:** Product has NO forecasts

**Expected UI Behavior:**
1. Metric cards show: "—" or "No data"
2. Chart shows: Empty state with "Add First Forecast" button
3. Analysis boxes: Hidden (no insights object)

**How to Test:**
1. Select a product with no forecasts (e.g., PROD-X)
2. Verify UI gracefully handles empty data

---

### 9.4 AI Agent Output Validation

#### 9.4.1 Verify Tool Output Format

**Test Tool Independently:**
```python
# In Python shell:
from tools.forecasting import simulate_demand_scenarios

result = simulate_demand_scenarios.invoke({
    "product_id": "PROD-A",
    "horizon_weeks": 4
})

import json
data = json.loads(result)

# Verify structure:
assert "scenarios" in data
assert "optimistic" in data["scenarios"]
assert "base" in data["scenarios"]
assert "pessimistic" in data["scenarios"]
assert data["scenarios"]["optimistic"]["probability_weight"] == 0.20
assert data["scenarios"]["base"]["probability_weight"] == 0.55
assert data["scenarios"]["pessimistic"]["probability_weight"] == 0.25

print("✅ Tool output valid!")
```

---

#### 9.4.2 Verify Expected Weighted Demand Calculation

**Manual Calculation:**
```python
scenarios = data["scenarios"]

optimistic_total = scenarios["optimistic"]["total_units"]
base_total = scenarios["base"]["total_units"]
pessimistic_total = scenarios["pessimistic"]["total_units"]

expected = (optimistic_total * 0.20) + (base_total * 0.55) + (pessimistic_total * 0.25)

print(f"Optimistic:   {optimistic_total} × 0.20 = {optimistic_total * 0.20}")
print(f"Base:         {base_total} × 0.55 = {base_total * 0.55}")
print(f"Pessimistic:  {pessimistic_total} × 0.25 = {pessimistic_total * 0.25}")
print(f"Expected:     {expected}")

assert abs(expected - data["expected_weighted_demand"]) < 1  # Allow 1 unit rounding error
print("✅ Expected weighted demand correct!")
```

---

### 9.5 End-to-End Test Scenario

**Scenario:** Complete workflow from pipeline run to UI display

**Steps:**

1. **Clear Database** (Start Fresh)
```sql
DELETE FROM demand_forecasts WHERE product_id = 'PROD-A';
```

2. **Run Pipeline** (UI or API)
```bash
curl -X POST "http://localhost:8000/api/pipeline/run" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "PROD-A"}'

# Capture run_id from response
```

3. **Poll Pipeline Status**
```bash
curl -X GET "http://localhost:8000/api/pipeline/runs/{run_id}"

# Wait until status = "completed"
```

4. **Verify Database Sync**
```sql
SELECT COUNT(*) FROM demand_forecasts WHERE product_id = 'PROD-A';
-- Should return 4 (4 weeks of forecasts)
```

5. **Open UI**
- Navigate to: http://localhost:5173/demand-intelligence
- Select: PROD-A

6. **Verify UI Display**
- ✅ Average Weekly Demand shows a number (not "—")
- ✅ Chart displays 3 colored areas (red, blue, green)
- ✅ Trend Direction shows "Upward" or "Downward"
- ✅ Forecast Summary box shows "4 weeks of forecast data entered"

7. **Add Manual Forecast**
- Click "Add Forecast" button
- Fill in week 15, optimistic: 1350, base: 1150, pessimistic: 950
- Submit

8. **Verify Database Update**
```sql
SELECT * FROM demand_forecasts WHERE product_id = 'PROD-A' AND week_number = 15;
-- Should return the new record
```

9. **Verify UI Refresh**
- Chart should now show 5 weeks (not 4)
- Average recalculated to include week 15

**✅ Test Passes If:** All steps complete without errors, UI displays correct data

---

## 10. TROUBLESHOOTING GUIDE

### 10.1 Common Issues & Solutions

#### Issue 1: "No forecast data" in UI

**Symptoms:**
- UI shows empty chart
- Message: "No forecast data for PROD-A"

**Possible Causes:**

| Cause | How to Check | Solution |
|-------|--------------|----------|
| **Pipeline not run** | Query: `SELECT COUNT(*) FROM demand_forecasts WHERE product_id = 'PROD-A'` → Returns 0 | Run pipeline from UI or API |
| **Database sync failed** | Check pipeline run status: `/api/pipeline/runs/{run_id}` → Look for errors in `database_sync` | Re-run pipeline, check backend logs for errors |
| **Wrong product_id** | UI selected PROD-X instead of PROD-A | Select correct product from dropdown |
| **API endpoint error** | Browser DevTools → Network tab → 500 error | Check backend logs, verify database connection |

**Quick Fix:**
```bash
# 1. Start backend if not running
cd backend && python main.py

# 2. Run pipeline via API
curl -X POST http://localhost:8000/api/pipeline/run -H "Content-Type: application/json" -d '{"product_id": "PROD-A"}'

# 3. Wait 60 seconds, refresh UI
```

---

#### Issue 2: Trend shows "0%" or "Stable" when it shouldn't

**Symptoms:**
- All forecasts have same base_case value (e.g., all 1050)
- Trend percent shows "0%"

**Possible Causes:**

| Cause | How to Check | Solution |
|-------|--------------|----------|
| **AI generated flat forecast** | Query: `SELECT DISTINCT base_case FROM demand_forecasts WHERE product_id = 'PROD-A'` → Returns only 1 value | This is actually valid - AI detected no trend in historical data |
| **Database duplication bug** | Same forecast copied 12 times | Delete duplicates, re-run pipeline |
| **Sample data has no trend** | Check `sample_data.py` → `trend = 0` | Modify `trend` variable to simulate growth |

**Diagnosis Query:**
```sql
SELECT
    week_number,
    base_case,
    LAG(base_case) OVER (ORDER BY week_number) as prev_week,
    base_case - LAG(base_case) OVER (ORDER BY week_number) as week_change
FROM demand_forecasts
WHERE product_id = 'PROD-A'
ORDER BY week_number;
```

**Expected:** `week_change` should vary (not all 0 or all same value)

---

#### Issue 3: Chart displays but data looks wrong

**Symptoms:**
- Optimistic < Base < Pessimistic (inverted!)
- Negative values
- Extreme values (e.g., 999,999 units)

**Possible Causes:**

| Cause | How to Check | Solution |
|-------|--------------|----------|
| **Manual entry error** | User swapped optimistic/pessimistic | Edit forecast, fix values |
| **AI tool bug** | Tool returned NaN or negative | Check backend logs, verify tool code |
| **Database corruption** | `SELECT * FROM demand_forecasts WHERE base_case < 0` | Delete bad records, re-run pipeline |

**Validation Query:**
```sql
SELECT *
FROM demand_forecasts
WHERE
    optimistic < base_case  -- Optimistic should be >= Base
    OR base_case < pessimistic  -- Base should be >= Pessimistic
    OR optimistic < 0  -- No negative values
    OR base_case < 0
    OR pessimistic < 0;
```

**If Returns Rows:** Data quality issue - delete and regenerate

---

#### Issue 4: "Import from AI" button does nothing

**Symptoms:**
- Click "Import from AI" → Alert says forecasts are auto-synced
- User expects manual import

**Explanation:**
- **By Design**: Forecasts auto-sync when pipeline runs
- "Import from AI" button is now informational only

**Solution:**
- Change button label to "ℹ️ How Forecasts Sync"
- OR remove button entirely (forecasts always auto-sync)

**Code Change:**
```javascript
// Option 1: Change button to info icon
<button onClick={() => alert('Forecasts auto-sync when you run the AI Pipeline!')}>
  <Info className="h-4 w-4" />
  How Forecasts Sync
</button>

// Option 2: Remove button entirely (cleaner UX)
// Just delete the "Import from AI" button
```

---

#### Issue 5: Backend crashes when running pipeline

**Symptoms:**
- Pipeline status stays "running" forever
- Backend logs show error: `anthropic.APIConnectionError`

**Possible Causes:**

| Cause | How to Check | Solution |
|-------|--------------|----------|
| **No Anthropic API key** | Check `.env` file → `ANTHROPIC_API_KEY=` is empty | Add valid API key to `.env` |
| **API key invalid** | Backend logs: `401 Unauthorized` | Generate new key at console.anthropic.com |
| **Network firewall** | Test: `ping api.anthropic.com` → Timeout | Check firewall/proxy settings |
| **Rate limit exceeded** | Backend logs: `429 Too Many Requests` | Wait 1 minute, retry |

**Quick Fix:**
```bash
# 1. Check if .env file exists
cd backend
cat .env

# Should contain:
# ANTHROPIC_API_KEY=sk-ant-api03-...

# 2. If missing, create it:
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# 3. Restart backend
python main.py
```

---

#### Issue 6: Actuals not updating in UI

**Symptoms:**
- User updates `actual` field in database
- UI still shows `actual` as NULL or old value

**Possible Causes:**

| Cause | How to Check | Solution |
|-------|--------------|----------|
| **React Query cache** | Old data cached in browser for 5 minutes | Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac) |
| **API not returning actuals** | Check API response in DevTools → Network tab | Verify backend query includes `actual` column |
| **Database update failed** | Query: `SELECT actual FROM demand_forecasts WHERE week_number = 10` | Re-run UPDATE query |

**Force Cache Clear:**
```javascript
// In browser console:
queryClient.invalidateQueries(['demand-forecasts', 'PROD-A'])
```

---

### 10.2 Debugging Checklist

When something isn't working:

- [ ] **Step 1:** Backend running? (Check http://localhost:8000/api/health)
- [ ] **Step 2:** Frontend running? (Check http://localhost:5173)
- [ ] **Step 3:** Database has data? (`SELECT COUNT(*) FROM demand_forecasts`)
- [ ] **Step 4:** API returns data? (Check Network tab in DevTools)
- [ ] **Step 5:** Calculations correct? (Check `console.log(insights)` in browser)
- [ ] **Step 6:** Chart receives data? (Check `console.log(forecastData)` before chart)
- [ ] **Step 7:** Anthropic API key valid? (Check `.env` file)
- [ ] **Step 8:** Any errors in backend logs? (Look for red ERROR messages)
- [ ] **Step 9:** Any errors in browser console? (Check DevTools → Console)
- [ ] **Step 10:** Clear cache and retry (Ctrl+Shift+R)

---

### 10.3 Logging & Monitoring

#### Backend Logs to Watch

**Normal Pipeline Run:**
```
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO: POST /api/pipeline/run - 200 OK
INFO: Background task started: run_id=a3f5b9c2-...
INFO: Demand Agent started for PROD-A
INFO: Tool called: simulate_demand_scenarios
INFO: Tool called: analyze_demand_trends
INFO: Demand Agent completed (18.4s)
INFO: Database sync: 4 forecasts created
INFO: Pipeline completed successfully (85.2s)
```

**Error Indicators (Bad):**
```
ERROR: anthropic.APIConnectionError: Connection refused
ERROR: sqlite3.OperationalError: no such table: demand_forecasts
ERROR: KeyError: 'scenarios' - missing key in AI response
ERROR: ValidationError: pessimistic value cannot be greater than base_case
```

#### Frontend DevTools Logs

**Normal Load:**
```
[React Query] Fetching: ['demand-forecasts', 'PROD-A']
[API] GET /api/demand/forecasts/PROD-A?weeks=12
[API] Response: 200 OK, 12 forecasts returned
[Insights] avgBase: 1088, trend: 18.75, trendPercent: 1.7
[Chart] Rendering 12 data points
```

**Error Indicators (Bad):**
```
[API] GET /api/demand/forecasts/PROD-A - 500 Internal Server Error
[Chart] Error: Cannot read property 'base_case' of undefined
[React Query] Query failed: Network error
```

---

## APPENDIX A: Quick Reference Tables

### A.1 Database Columns Reference

| Table | Column | Type | Meaning | Example |
|-------|--------|------|---------|---------|
| `demand_forecasts` | `id` | INTEGER | Unique forecast ID | 42 |
| | `product_id` | TEXT | Product identifier | "PROD-A" |
| | `week_number` | INTEGER | Week of year (1-53) | 10 |
| | `forecast_date` | DATE | Week start date | "2026-03-09" |
| | `optimistic` | INTEGER | Best-case demand (units) | 1250 |
| | `base_case` | INTEGER | Expected demand (units) | 1050 |
| | `pessimistic` | INTEGER | Worst-case demand (units) | 850 |
| | `actual` | INTEGER | Real demand (units, filled later) | 1095 |
| | `created_at` | TIMESTAMP | When forecast was created | "2026-03-04 10:23:45" |

### A.2 API Endpoints Reference

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/api/demand/forecasts/{product_id}` | Fetch forecasts | No |
| POST | `/api/demand/forecasts/{product_id}` | Create forecast | No |
| PATCH | `/api/demand/forecasts/{product_id}/{week}` | Update actual | No |
| POST | `/api/pipeline/run` | Run AI pipeline | No |
| GET | `/api/pipeline/runs/{run_id}` | Get pipeline status | No |

### A.3 Key Formulas Reference

| Metric | Formula | Example |
|--------|---------|---------|
| **Average Demand** | `sum(base_case) / count` | `(1050+1075+1100+1125) / 4 = 1088` |
| **Trend Slope** | `(last - first) / count` | `(1125 - 1050) / 4 = 18.75 units/week` |
| **Trend %** | `(slope / average) × 100` | `(18.75 / 1088) × 100 = 1.7%` |
| **Std Deviation** | `sqrt(sum((x - avg)²) / n)` | `sqrt(204051 / 12) = 130.4` |
| **Z-Score** | `(value - average) / std_dev` | `(1450 - 1138) / 130.4 = 2.39` |
| **Expected Weighted** | `Σ(scenario × probability)` | `5782×0.2 + 4912×0.55 + 3822×0.25 = 4813` |

---

## APPENDIX B: Sample Data for Testing

### B.1 SQL Insert Statements

**Create 12 weeks of sample forecasts:**
```sql
INSERT INTO demand_forecasts (product_id, week_number, forecast_date, optimistic, base_case, pessimistic, actual) VALUES
('PROD-A', 10, '2026-03-09', 1250, 1050, 850, NULL),
('PROD-A', 11, '2026-03-16', 1280, 1075, 870, NULL),
('PROD-A', 12, '2026-03-23', 1310, 1100, 890, 1095),
('PROD-A', 13, '2026-03-30', 1340, 1125, 910, 1130),
('PROD-A', 14, '2026-04-06', 1370, 1150, 930, NULL),
('PROD-A', 15, '2026-04-13', 1400, 1175, 950, NULL),
('PROD-A', 16, '2026-04-20', 1430, 1200, 970, NULL),
('PROD-A', 17, '2026-04-27', 1460, 1225, 990, NULL),
('PROD-A', 18, '2026-05-04', 1490, 1250, 1010, NULL),
('PROD-A', 19, '2026-05-11', 1520, 1275, 1030, NULL),
('PROD-A', 20, '2026-05-18', 1550, 1300, 1050, NULL),
('PROD-A', 21, '2026-05-25', 1580, 1325, 1070, NULL);
```

**Expected UI Results:**
- Average Weekly Demand: **1,188 units**
- Trend Direction: **Upward**
- Trend Percent: **+1.9% per week**
- Forecasts Entered: **12 weeks**
- Actuals Recorded: **2** (weeks 12 and 13)

---

## GLOSSARY

| Term | Definition |
|------|------------|
| **Agentic AI** | AI that autonomously decides which tools to use, interprets results, and reasons like a human expert (not just executing predefined scripts) |
| **Area Chart** | Chart type that fills the area under a line, useful for showing volume/magnitude over time |
| **Base Case Forecast** | Most likely demand scenario, typically assigned 50-60% probability weight |
| **Coefficient of Variation (CV)** | Standard deviation divided by mean, expressed as percentage - measures relative variability |
| **Confidence Interval** | Range of values (e.g., 95% CI) where actual value is likely to fall |
| **FastAPI** | Modern Python web framework for building APIs with automatic validation and documentation |
| **LangChain** | Framework for building LLM-powered applications with tool calling and agent orchestration |
| **Linear Regression** | Statistical method to find the best-fit line through data points (used for trend analysis) |
| **Optimistic Scenario** | Best-case demand forecast, typically assigned 15-25% probability weight |
| **Pessimistic Scenario** | Worst-case demand forecast, typically assigned 20-30% probability weight |
| **Pipeline** | Automated workflow that runs all 5 AI agents in sequence |
| **Recharts** | React charting library built on D3.js, used for data visualization |
| **SQLite** | Lightweight file-based SQL database, ideal for embedded applications |
| **Standard Deviation** | Measure of data spread - how much values deviate from the average |
| **TanStack Query (React Query)** | Library for managing server state in React with automatic caching and refetching |
| **Tool** | Python function that an AI agent can call to perform specific tasks (forecasting, analysis, etc.) |
| **Trend** | Long-term direction of change in data (upward, downward, or stable) |
| **UUID** | Universally Unique Identifier - random ID used for tracking pipeline runs |
| **Z-Score** | Number of standard deviations a value is from the mean (used for anomaly detection) |

---

## CONCLUSION

This documentation provides **complete end-to-end coverage** of the Demand Intelligence module. You now understand:

✅ **How the system works**: From user click → AI agent → database → UI display
✅ **Where data comes from**: Database tables, sample data generators, AI tools
✅ **How calculations work**: Every formula explained with examples
✅ **How to validate results**: SQL queries, API tests, manual calculations
✅ **How to troubleshoot**: Common issues, debugging steps, log interpretation

**Next Steps:**
1. **Run the system**: Start backend + frontend, run pipeline, observe data flow
2. **Trace one forecast**: Pick a single forecast week, trace it from AI → DB → UI
3. **Modify and test**: Change a value in DB, verify UI updates correctly
4. **Experiment**: Try different products, add manual forecasts, update actuals

**For Questions:**
- Review Section 4 (Pipeline Flow) for "how it works"
- Review Section 6 (Calculations) for "why this number"
- Review Section 9 (Validation) for "how to verify"
- Review Section 10 (Troubleshooting) for "it's broken, help!"

---

**Document Version:** 1.0
**Last Updated:** March 4, 2026
**Maintained By:** AMIS Development Team
**For:** Manufacturing Team Training & System Validation
