# AMIS — Real-World Implementation Blueprint
## Autonomous Manufacturing Intelligence System — Production SaaS Build Guide

**Version:** 1.0
**Date:** February 2026
**Audience:** Developers, architects, and engineering leads building AMIS into a production SaaS product.

> This is a technical specification and build guide — not marketing material.
> Every section references what exists in the current codebase and what must be built next.

---

## Table of Contents

1. [Honest Starting Point — What You Have vs. What's Needed](#1-honest-starting-point)
2. [What Changes in the Current Codebase](#2-what-changes-in-the-current-codebase)
3. [Real-World Data Architecture](#3-real-world-data-architecture)
4. [Agent System Improvements for Production](#4-agent-system-improvements-for-production)
5. [Trigger & Automation System](#5-trigger--automation-system)
6. [User Roles — Who Uses What](#6-user-roles)
7. [UI Design — Page by Page](#7-ui-design--page-by-page)
8. [Human-in-the-Loop: Approval Workflow](#8-human-in-the-loop-approval-workflow)
9. [Technical Architecture](#9-technical-architecture)
10. [API Design](#10-api-design)
11. [Phased Build Plan](#11-phased-build-plan)
12. [What Makes This Different](#12-what-makes-this-different)
13. [Production File Structure](#13-production-file-structure)
14. [Key Decisions Reference](#14-key-decisions-reference)

---

## 1. Honest Starting Point

Your current codebase is a **working AI brain with no body**. The agents reason correctly, the data flows are right, and the orchestrator synthesizes properly. What is missing is everything that makes it usable by a real person at a real factory.

```
WHAT YOU HAVE                         WHAT REAL WORLD NEEDS
──────────────────────────────────────────────────────────────────
✅ 6 working agents                   ❌ Real data (not sample_data.py)
✅ ReAct reasoning loop               ❌ Web interface / dashboard
✅ Cross-agent handoffs (envelopes)   ❌ Database (results disappear now)
✅ Orchestrator synthesis             ❌ Scheduled automation
✅ Data flow tracing                  ❌ Auth + multi-tenancy
✅ Scenario validation system         ❌ ERP / IoT connectors
✅ 19 demo scenarios                  ❌ Email / Slack notifications
✅ CLI interface                      ❌ Human approval workflows
                                      ❌ Proper error handling
                                      ❌ FastAPI layer
                                      ❌ Cost control (API rate limiting)
```

The AI intelligence is done. The gap is **infrastructure** — and it is very buildable.

---

## 2. What Changes in the Current Codebase

### 2.1 What Stays (Do Not Touch)

| File / Component | Why It Stays |
|-----------------|-------------|
| `agents/base_agent.py` — ReAct loop | Architecturally correct. Add async + structured logging only. |
| `agents/*.py` — All 6 agents | Agent logic is solid. Swap out tool data sources only. |
| `tools/tracer.py` | Data flow audit stays as-is. This is a production-quality feature. |
| `tools/validator.py` | Scenario validation stays. Becomes the integration test suite. |
| `tools/scenario.py` | Controlled injection testing stays. |
| `prompts/*.py` | All prompts stay. Extend to DB-backed versioning later. |
| `tools/orchestrator.py` — `_compute_report()` | Deterministic scoring logic. Add unit tests; do not rewrite. |
| Agent bridge methods (`get_forecast_output`, etc.) | These programmatic bridges are what make cascading possible. |

### 2.2 What Gets Replaced

| Current | Replace With | Why |
|---------|-------------|-----|
| `data/sample_data.py` — hardcoded dicts | Async PostgreSQL queries per tenant | Real manufacturers need real data |
| `config.py` — hardcoded API key | `.env` file + `python-dotenv` with startup validation | Security — the current key must be rotated immediately |
| `demo.py` / `main.py` — CLI only | FastAPI endpoints + Celery tasks | Production requires HTTP + background execution |
| `print()` statements everywhere | `structlog` structured logging | Queryable, storable, filterable logs |

### 2.3 What Gets Added

| New Layer | Purpose |
|-----------|---------|
| FastAPI application | HTTP interface to all agents |
| PostgreSQL + TimescaleDB | Persistent storage, per-tenant isolation, time-series sensors |
| Redis | Cache + message queue + Celery broker |
| Celery workers | Background async agent execution |
| APScheduler / Celery Beat | Cron-based scheduled runs |
| JWT + RBAC auth | Multi-user, multi-role, multi-tenant |
| CSV upload pipeline | Day 1 data ingestion without ERP integration |
| ERP connectors | SAP, Oracle, Odoo real-data sync |
| Human approval queue | Decisions need sign-off before execution |
| Notification service | Email (SendGrid), Slack, Microsoft Teams |
| React + Next.js frontend | The actual UI manufacturers interact with |
| Audit log | Every decision logged with who, when, and why |

### 2.4 What Gets Improved

**Error handling in tool execution**
```python
# CURRENT — crashes agent if tool fails
result = tool.invoke(tool_args)

# PRODUCTION — structured error returned to LLM, agent continues
async def _execute_tool(self, tool, tool_args, tool_id):
    try:
        result = await asyncio.wait_for(tool.ainvoke(tool_args), timeout=30.0)
        return str(result)
    except asyncio.TimeoutError:
        return json.dumps({"error": "tool_timeout", "tool": tool.name,
                           "recommendation": "Proceed with partial data."})
    except Exception as e:
        log.exception("agent.tool_error", tool=tool.name)
        return json.dumps({"error": str(type(e).__name__), "tool": tool.name,
                           "recommendation": "Flag unavailable, continue with other data."})
```

**Async LLM calls** — Replace `self.llm_with_tools.invoke(messages)` with `await self.llm_with_tools.ainvoke(messages)` throughout BaseAgent. One synchronous call blocks a web thread for 15–45 seconds.

**Conversation memory** — `self.message_history` becomes ephemeral workers; history loaded from and saved to PostgreSQL per session.

---

## 3. Real-World Data Architecture

### 3.1 What Systems Manufacturers Actually Have

| System | Common Products | What AMIS Needs From It |
|--------|----------------|------------------------|
| **ERP** | SAP S/4HANA, Oracle, Odoo, NetSuite, Epicor | Inventory, POs, sales orders, BOM, supplier master |
| **MES** | Ignition, Siemens Opcenter, AVEVA | Production actuals, work orders, shift logs, scrap |
| **SCADA / IoT** | OSIsoft PI, AWS IoT Hub, GE Proficy | Real-time sensors: vibration, temperature, pressure |
| **CMMS** | Fiix, UpKeep, IBM Maximo | Maintenance history, work orders, spare parts |
| **WMS** | Manhattan Associates, SAP EWM | Warehouse locations, actual stock counts |
| **Spreadsheets** | Excel, Google Sheets | Everything not in any other system (always present) |
| **Supplier portals** | Ariba, Coupa, email | Delivery confirmations, lead time updates |

**Critical reality:** No manufacturer has all data in one place. Data quality ranges from excellent to terrible. Your architecture must handle this from day one.

### 3.2 The Data Ingestion Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                 DATA SOURCES (Customer Side)                      │
│  SAP/Oracle  │  MES/SCADA  │  CMMS  │  IoT Sensors  │  CSV      │
└───────┬──────┴──────┬───────┴───┬────┴───────┬────────┴────┬─────┘
        │             │           │            │              │
    REST API      OPC-UA/MQTT  REST API      MQTT        File Upload
        │             │           │            │              │
┌───────▼─────────────▼───────────▼────────────▼──────────────▼─────┐
│                     INGESTION / ETL LAYER                          │
│  1. Extract  → pull raw data from each source                      │
│  2. Validate → check nulls, wrong units, outliers, duplicates      │
│  3. Normalize → standard schema (product_id, week, units, cost)    │
│  4. Score    → attach data_quality_score (0.0–1.0) per record     │
│  5. Load     → write to tenant-isolated PostgreSQL schema          │
└──────────────────────────────────┬─────────────────────────────────┘
                                   │
┌──────────────────────────────────▼─────────────────────────────────┐
│               UNIFIED DATA STORE (per tenant)                       │
│                                                                      │
│  PostgreSQL (transactional):        TimescaleDB (time-series):      │
│  ├── demand_history                 ├── sensor_readings             │
│  ├── inventory_positions            ├── production_counters         │
│  ├── machine_fleet                  └── oee_snapshots              │
│  ├── supplier_master                                                 │
│  ├── purchase_orders                Redis (ephemeral):             │
│  ├── bom_components                 ├── latest sensor values       │
│  ├── maintenance_events             ├── agent result cache         │
│  └── agent_run_results              └── event pub/sub stream       │
└──────────────────────────────────┬─────────────────────────────────┘
                                   │
                        ┌──────────▼──────────┐
                        │    AMIS AGENTS       │
                        │  (read from DB,      │
                        │   not sample_data)   │
                        └──────────────────────┘
```

### 3.3 The Day 1 Problem — CSV Upload First

The biggest SaaS killer: manufacturers cannot give you ERP API access in week one. Integration projects take 6–12 weeks. If AMIS requires full integration before showing value, you lose every sale.

**Solution: CSV upload is the Day 1 path.**

The manufacturer uploads 5 CSV files:
1. **Historical demand / sales orders** — 12+ months, weekly or daily
2. **Current inventory levels** — product ID, stock, location
3. **Machine list** — machine ID, name, line, status, last maintenance
4. **Supplier list** — supplier ID, name, lead times, on-time delivery history
5. **Bill of materials** — product → component mapping with quantities

These 5 CSVs give AMIS enough to run all 5 agents and produce a real first report within 30 minutes. The manufacturer sees value before the sales call ends.

**Progression:**
```
Week 1    CSV upload (always works, zero IT involvement)
Month 1   Odoo / NetSuite API connector (smaller companies)
Month 3   SAP connector (larger companies, needs IT)
Month 6   MES + IoT streaming (advanced customers)
```

### 3.4 Data Quality Issues in the Real World

| Problem | Example | AMIS Handling |
|---------|---------|---------------|
| Missing values | Sensor offline 3 days: null readings | Impute with rolling average; flag as estimated; reduce confidence |
| Wrong units | ERP stores kg; BOM specifies lbs | Unit conversion library; tenant-level preference config |
| Duplicate records | Same PO in ERP and email confirmation | Dedup by PO number + supplier + date |
| Inconsistent IDs | "VALVE-A", "Valve A", "VA", "SKU-001" = same thing | Entity resolution during onboarding |
| Future-dated records | Order dated 2045 (data entry error) | Flag and quarantine; alert IT admin |
| Negative stock | ERP shows -50 units (timing lag) | Treat as 0; log the anomaly |
| Stale data | ERP last synced 18 hours ago | Show data freshness timestamp on every widget |
| Schema drift | ERP vendor updates API field names | Versioned connector schemas; alert on mismatch |

**Confidence scoring:** Every record carries a `data_quality_score` (0.0–1.0). Agent prompts instruct: *"If a tool returns low-confidence data, explicitly acknowledge the uncertainty in your response."*

### 3.5 Multi-Tenant Data Isolation

```sql
-- Row-level security on ALL tenant tables
ALTER TABLE inventory_positions ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON inventory_positions
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

Isolation enforced at 4 levels:
1. PostgreSQL row-level security (cannot be bypassed by application bugs)
2. Application middleware (sets `tenant_id` from JWT on every request)
3. Redis key namespacing (`tenant:{tenant_id}:sensor:{machine_id}`)
4. S3 prefix isolation (`s3://amis-data/{tenant_id}/...`)

---

## 4. Agent System Improvements for Production

### 4.1 Replace sample_data.py with DB-Backed Tools

```python
# BEFORE — reads from hardcoded Python dict
@tool
def get_inventory_status(product_id: str = "PROD-A") -> str:
    from data.sample_data import get_current_inventory
    return json.dumps(get_current_inventory(product_id))

# AFTER — reads from PostgreSQL, tenant-isolated, async
@tool
async def get_inventory_status(product_id: str, tenant_id: str) -> str:
    try:
        async with get_db_pool(tenant_id) as conn:
            row = await conn.fetchrow(
                """SELECT ip.*, ip.current_stock / NULLIF(ip.avg_daily_consumption, 0)
                          AS days_of_supply
                   FROM inventory_positions ip
                   WHERE ip.product_id = $1 AND ip.tenant_id = $2
                   ORDER BY ip.last_updated_at DESC LIMIT 1""",
                product_id, tenant_id
            )
            if not row:
                return json.dumps({"error": f"No inventory data for {product_id}"})
            return json.dumps(dict(row))
    except asyncpg.PostgresError as e:
        log.error("tool.db_error", product_id=product_id, error=str(e))
        return json.dumps({"error": "Database query failed"})
```

### 4.2 Async Execution — Agents Can't Block HTTP Requests

```python
# API endpoint returns immediately
@app.post("/api/v1/agents/{agent_type}/run")
async def trigger_agent_run(agent_type: str, request: AgentRunRequest,
                             user: User = Depends(get_current_user)):
    run = AgentRun(tenant_id=user.tenant_id, agent_type=agent_type,
                   status="pending", input_params=request.params)
    await db.save(run)
    run_agent_task.delay(str(run.id), str(user.tenant_id), agent_type, request.params)
    return {"run_id": str(run.id), "status": "pending"}

# Client polls for result
@app.get("/api/v1/agents/runs/{run_id}")
async def get_run_status(run_id: str):
    run = await db.get_agent_run(run_id)
    return {"status": run.status, "result": run.output, "confidence": run.confidence_score}
```

### 4.3 Result Caching — Control Claude API Costs

```python
async def get_cached_result(agent_type, tenant_id, params) -> dict | None:
    data_hash = await compute_data_snapshot_hash(tenant_id, agent_type, params)
    cache_key = f"agent_result:{tenant_id}:{agent_type}:{data_hash}"
    cached = await redis.get(cache_key)
    if cached:
        log.info("agent.cache_hit", agent_type=agent_type)
        return json.loads(cached)
    return None

# After successful run:
await redis.setex(cache_key, ttl_seconds[agent_type], json.dumps(result))
# TTL: demand=14400s (4h), inventory=3600s (1h), machine_health=300s (5min)
```

### 4.4 Confidence Scoring — When to Auto-Execute vs. Escalate

```python
# Every agent result includes confidence
CONFIDENCE_THRESHOLDS = {
    "auto_execute":     0.85,  # Execute without human review
    "notify_execute":   0.65,  # Notify human; auto-execute if no response in N hours
    "require_approval": 0.50,  # Queue for explicit human approval
    "escalate":         0.50,  # Below this → escalate to senior decision-maker
}
```

### 4.5 Feedback Loop — Learning from Overrides

When a human overrides a recommendation, it is stored:

```python
# agent_recommendation_feedback table
{
    "run_id": "...",
    "agent_type": "supplier",
    "recommendation": {"action": "place_po", "quantity": 500},
    "human_decision": "override",
    "override_quantity": 300,
    "override_reason": "Warehouse space constraint not in system",
    "outcome_30_days": None,   # filled in later by outcome tracker
}
```

An outcome tracker runs 30 days after each override and compares what actually happened to what the model predicted. This builds per-tenant recommendation accuracy reports over time.

---

## 5. Trigger & Automation System

### 5.1 The Monday Morning Scheduled Cascade

```
TIME (UTC)   AGENT              WAITS FOR           OUTPUT
──────────────────────────────────────────────────────────────────────
Monday 06:00  Demand Agent       Nothing             Forecast envelope
Monday 06:15  Inventory Agent    Demand complete     Reorder queue, risk
Monday 07:00  Machine Health     Nothing (parallel)  Capacity ceiling
Monday 08:00  Production Agent   Machine + Demand    MPS, material req.
Monday 09:00  Supplier Agent     Production done     PO package, risk
Monday 09:30  Orchestrator       All 5 complete      Weekly brief, alerts
Monday 09:45  Notifications      Report ready        Email, Slack, Teams

DAILY (Tue–Sun):
08:00  Inventory checkpoint   → check if any product crossed below ROP
08:00  Supplier PO status     → check for overdue POs, flag delays
Every 4h  Machine health pulse → check sensor readings vs. thresholds
16:00  Production attainment  → compare actual output to daily plan
```

### 5.2 Event-Based Triggers — Full Map

| Event | Source | Fires First | Cascades To |
|-------|--------|------------|-------------|
| Machine sensor crosses threshold | IoT / SCADA | Machine Health | → Production re-plan |
| Machine unplanned failure | MES / team | Machine Health (CRITICAL) | → Production emergency + Supplier |
| Inventory drops below ROP | ERP sync | Inventory Agent | → Supplier emergency PO |
| Demand anomaly > 15% | Demand Agent | Alert + Inventory check | → Production capacity check |
| Supplier confirms delivery delay | Webhook | Supplier Agent | → Inventory buffer + Production re-plan |
| Rush customer order arrives | ERP sales webhook | Full pipeline re-run | → All agents → Human queue |
| Human approves action | Approval UI | Execute action | → Notify all parties + audit log |
| Human rejects recommendation | Approval UI | Log + feedback | → Re-run if still urgent |
| Safety stock < minimum | Daily inventory check | Inventory Agent | → Supplier expedite PO → URGENT queue |
| Contract expiry < 60 days | Background monitor | Alert to procurement | → Escalate if < 30 days |
| Production attainment < 90% (2 days) | Daily check | Alert planners | → Machine Health check |

### 5.3 The Cascade Condition Logic

```python
# workers/cascade_evaluator.py — called after EVERY agent run

async def evaluate_demand_cascade(result: dict, tenant_id: str) -> list[str]:
    triggers = []
    if result.get("anomaly_detected"):
        if abs(result.get("anomaly_magnitude_pct", 0)) >= 10:
            triggers.append("inventory")
    last_target = await get_last_production_target(tenant_id)
    new_demand = result.get("expected_weekly_demand", 0)
    if last_target and new_demand > last_target * 1.10:
        triggers.append("production")
    return triggers

async def evaluate_machine_health_cascade(result: dict, tenant_id: str) -> list[str]:
    triggers = []
    if result.get("newly_critical_machines"):
        triggers.append("production")
    prev_ceiling = await get_last_capacity_ceiling(tenant_id)
    new_ceiling = result.get("recommended_production_ceiling_units_per_week", 0)
    if prev_ceiling and new_ceiling < prev_ceiling * 0.90:
        triggers.append("production")
    return triggers

async def evaluate_inventory_cascade(result: dict, tenant_id: str) -> list[str]:
    triggers = []
    if result.get("stockout_probability_pct", 0) >= 40:
        triggers.append("supplier")
        await create_priority_alert(tenant_id, "CRITICAL",
            f"Stockout probability {result['stockout_probability_pct']}%")
    if result.get("reorder_needed_now"):
        if not await has_pending_po(tenant_id, result.get("product_id")):
            triggers.append("supplier")
    return triggers

async def evaluate_production_cascade(result: dict, tenant_id: str) -> list[str]:
    triggers = []
    if result.get("procurement_alerts"):
        triggers.append("supplier")
    prev_req = await get_last_material_requirements(tenant_id)
    new_req = result.get("material_requirements", {})
    if requirements_differ_significantly(prev_req, new_req, threshold_pct=15):
        triggers.append("supplier")
    return triggers
```

### 5.4 Implementation: 3 Phases

**Phase 1 — APScheduler (Weeks 1–6, simplest)**
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(run_monday_cascade,      'cron', day_of_week='mon', hour=6)
scheduler.add_job(run_daily_inventory,     'cron', hour=8)
scheduler.add_job(run_machine_monitor,     'interval', hours=4)
scheduler.start()
```
Limitation: no retries, no distributed execution, single process only.

**Phase 2 — Conditional Cascade (Weeks 7–14)**
Add `run_cascade_evaluation()` after every agent run. Add `agent_run_log` table for observability.

**Phase 3 — Redis + Celery (Month 4+, production-grade)**
Distributed workers, priority queues, automatic retries, Flower monitoring dashboard.

```python
celery_app.conf.task_queues = [
    Queue("critical"),  # Emergency re-plans: immediate
    Queue("high"),      # Event-triggered: within 5 min
    Queue("normal"),    # Scheduled weekly/daily: standard
    Queue("low"),       # Background analytics: best effort
]
```

---

## 6. User Roles

### Role 1: Plant Director / Operations Manager

**Their 3 questions every morning:**
1. Is there anything that will cause us to miss customer commitments this week?
2. What are we spending money on unnecessarily, and where are we under-spending?
3. What decisions need my sign-off today?

**Pages:** Command Center, Weekly Brief, Human Decision Queue (escalations only), Demand summary
**Actions:** Approve high-value POs (above their threshold), authorize overtime, dismiss alerts with reason, download weekly PDF

---

### Role 2: Supply Chain / Demand Planner

**Their 3 questions:**
1. Is the 4-week forecast still valid, or has something changed?
2. Are we at risk of stockout on any product?
3. Are my forecast assumptions still correct (competitor, promotion, seasonality)?

**Pages:** Command Center, Demand Intelligence (primary), Inventory Control, Supplier Management (PO status), AI Chat
**Actions:** Override forecast assumptions, approve inventory orders (within PO authority), configure safety stock policy, create what-if scenarios, export forecast CSV

---

### Role 3: Production Planner

**Their 3 questions:**
1. What is today's production target given current machine availability?
2. Which lines are constrained and why?
3. Do we have the materials to run today's schedule?

**Pages:** Command Center, Production Planning (primary), Machine Health (read), Inventory (component view), AI Chat
**Actions:** Approve schedule adjustments, request overtime authorization, adjust line assignments, flag production shortfall with reason

---

### Role 4: Maintenance Manager

**Their 3 questions:**
1. Which machines are showing failure signs and how much time do I have?
2. What PM work is scheduled this week and does it conflict with production?
3. What did we spend on unplanned vs. planned maintenance last month?

**Pages:** Command Center, Machine Health (primary), Production Planning (read), AI Chat
**Actions:** Create/update/close work orders (sync to CMMS), schedule maintenance windows (auto-checks production conflicts), acknowledge machine alerts, export maintenance reports

---

### Role 5: Procurement Officer

**Their 3 questions:**
1. Which POs are late and what is the production impact?
2. Are there any components I need to order today?
3. How are my suppliers performing against their SLAs?

**Pages:** Command Center, Supplier Management (primary), Inventory Control (reorder queue), Human Decision Queue (PO approvals), AI Chat
**Actions:** Approve/reject AI-recommended POs, manually create POs, update supplier delivery confirmations, initiate contract renegotiation

---

### Role 6: Plant Floor Supervisor

**Their 3 questions:**
1. Any machine alerts right now?
2. What is the shift production target per line?
3. Any incoming materials I need to stage?

**Pages:** Simplified mobile-first dashboard — alerts + shift target + machine status only
**Actions:** Acknowledge machine alerts, log production downtime events, mark maintenance work started/complete

---

### Role 7: IT Administrator

**Their questions:** Are all integrations running? Any failed agent runs? Any security events?

**Pages:** System Configuration (primary), Audit Log, User Management, Data Quality Monitor, API credentials
**Actions:** Configure ERP/MES/IoT connectors, manage users and roles, configure thresholds, view and export audit logs

---

## 7. UI Design — Page by Page

### Page 1: Command Center Dashboard

**Users:** All roles (content filtered by role)
**Purpose:** Single-screen answer to "Is everything OK?" with one-click to anything that is not.

```
┌─────────────────────────────────────────────────────────────────────┐
│  AMIS                  Acme Manufacturing — Plant 01  Mon 24 Feb    │
│  ───────────────────────────────────────────────────────────────── │
│  SYSTEM HEALTH: 68/100  ⚠ AT RISK                                  │
│  ████████████░░░░░░░░                                               │
│  ───────────────────────────────────────────────────────────────── │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │ DEMAND   │ │INVENTORY │ │ MACHINES │ │PRODUCTION│              │
│  │ ↗ +1.8% │ │ 12.8 days│ │  OEE 78% │ │  94% att │              │
│  │ 1,050/wk │ │ ⚠ 2 ROP  │ │ ⚠ MCH-002│ │  Gap: -70│              │
│  │  WATCH   │ │ AT RISK  │ │ AT RISK  │ │  WATCH   │              │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │
│  ───────────────────────────────────────────────────────────────── │
│  ACTION QUEUE — 3 items need your attention                         │
│  ┌─────┬──────────────────────────────────┬────────┬───────────┐  │
│  │ 🔴  │ MCH-002 failure risk 47% (7-day) │ URGENT │ [Review]  │  │
│  │ 🟡  │ PROD-C below reorder point       │  HIGH  │ [Approve] │  │
│  │ 🟡  │ SUP-B contract expiring Jun 30   │ MEDIUM │  [View]   │  │
│  └─────┴──────────────────────────────────┴────────┴───────────┘  │
│  ───────────────────────────────────────────────────────────────── │
│  FINANCIAL SNAPSHOT THIS WEEK                                       │
│  Revenue at risk: $47,250  │  Holding cost: $4,255                 │
│  Potential savings: $8,400 │  Pending PO approvals: $71,550        │
│  ───────────────────────────────────────────────────────────────── │
│  Last run: Mon 06:00 ✓   Next run: Tue 06:00   [Run Now]           │
└─────────────────────────────────────────────────────────────────────┘
```

**Key principles:**
- System health score (0–100) visible immediately — the single number executives care about
- Action queue shows only items needing a **decision**, not just information
- Every risk quantified in **dollars** — manufacturers think in money, not percentages
- Data freshness timestamp — users need to trust the data is current

---

### Page 2: Demand Intelligence

**Users:** Demand Planner, Plant Director (summary view)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Demand Intelligence                     Product: PROD-A  [Change]  │
│  ───────────────────────────────────────────────────────────────── │
│  FORECAST — NEXT 4 WEEKS                                            │
│  1200 ┤                    ╭───────────────── Optimistic (20%)     │
│  1100 ┤            ╭───────╯                                        │
│  1050 ┤────────────╮           Base (55%)                          │
│   950 ┤      ╭─────╯                                               │
│   880 ┤──────╯                 Pessimistic (25%)                   │
│        W07   W08    W09    W10    W11                               │
│  95% Confidence: 880 – 1,210 units / week                          │
│  ───────────────────────────────────────────────────────────────── │
│  ANOMALY DETECTED — Week 05 (Feb 05)              [See Details]    │
│  🔴 +53% spike: 1,652 units vs 1,079 expected                      │
│  Root cause: Promotional pricing + viral social media              │
│  Assessment: Temporary spike. Base demand trend unaffected.        │
│  ───────────────────────────────────────────────────────────────── │
│  WHAT-IF SIMULATOR                             [Run Simulation]    │
│  Demand shift:      [────●────────] +0%                            │
│  Lose enterprise X: [ ] Impact: -$275/wk                          │
│  Trade show boost:  [ ] +15% optimistic scenario                  │
│  ───────────────────────────────────────────────────────────────── │
│  AI REASONING (excerpt)                            [Show Full]     │
│  "Base case 1,050 units/week reflects viral spike normalization    │
│  while preserving the underlying 1.8%/week growth trend. New       │
│  competitor product factors in a -8% demand headwind..."           │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Page 3: Inventory Control

**Users:** Demand Planner (primary), Procurement Officer (reorder queue)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Inventory Control                                                   │
│  STOCK HEATMAP — All Products                [Filter: At Risk Only] │
│  PROD-A  ████████████░░  12.8 days  🟡 WATCH  → Reorder soon       │
│  PROD-B  ████████████████ 31.0 days  🟢 HEALTHY                    │
│  PROD-C  ███░░░░░░░░░░░░   3.1 days  🔴 CRITICAL → ORDER NOW       │
│  ───────────────────────────────────────────────────────────────── │
│  STOCKOUT RISK — PROD-A  (Monte Carlo: 1,000 simulations)           │
│  Day 9:   0.5%  ░░░░░░░░░░░░░░░░░░░░░                              │
│  Day 11:  7.2%  ██░░░░░░░░░░░░░░░░░░                               │
│  Day 14: 41.5%  ██████████░░░░░░░░░  ← ORDER REQUIRED              │
│  Cost if stockout: $45/unit × 1,087 units = $48,915                │
│  ───────────────────────────────────────────────────────────────── │
│  REORDER QUEUE (requires approval)                                  │
│  PROD-C   800 u   SUP-A   $41,600   Feb 26   URGENT   [APPROVE ✓]  │
│  PROD-A   500 u   SUP-A   $26,000   Mar 03   Normal   [APPROVE ✓]  │
│  ───────────────────────────────────────────────────────────────── │
│  SAFETY STOCK OPTIMIZER                                             │
│  Current: 300 units   →  Optimal: 596 units                        │
│  Extra holding cost:  +$680 / year                                  │
│  Stockout cost saving: -$27,099 / year                              │
│  Net annual savings:   $26,419   [Apply Recommendation]            │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Page 4: Machine Health

**Users:** Maintenance Manager (primary), Production Planner (read)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Machine Health                          Plant: PLANT-01            │
│  FLEET MAP                                                           │
│  MCH-001    MCH-002    MCH-003    MCH-004    MCH-005                │
│  Line 1     Line 2     Line 3     Line 4     Line 5                 │
│  [████ 91]  [▓▓░░ 58]  [███░ 74]  [■■■■ DN]  [████ 96]            │
│  NORMAL     WARNING    CAUTION    DOWN       NORMAL                 │
│  ───────────────────────────────────────────────────────────────── │
│  DETAIL: MCH-002 — CNC Machining Center                            │
│  Health: 58/100  │  Alert: WARNING  │  Age: 6.4 years              │
│                                                                      │
│  Vibration:   4.2 mm/s²  [Baseline: 1.8]  [Limit: 3.0]  ⚠ HIGH   │
│  Temperature:  81°C      [Baseline: 72°C]  [Limit: 85°C]  WATCH   │
│  Spindle RPM: 2,850      [Baseline: 3,000]  Degrading trend        │
│                                                                      │
│  7-DAY VIBRATION TREND:                                             │
│  4.2┤                                                ●              │
│  3.5┤                        ●           ●                          │
│  3.0┤─ ─ ─ ─ (threshold)─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─                  │
│  2.0┤●    ●    ●                                                    │
│      Mon  Tue  Wed  Thu  Fri  Sat  Sun                              │
│                                                                      │
│  AI: Rising at 0.31 mm/s²/day. Threshold breach in 4–5 days.       │
│  7-day failure probability: 47%  │  14-day: 68%                    │
│  Cost if fails unplanned: $47,200  │  Planned PM: $3,800           │
│                                                                      │
│  [Schedule Maintenance]  [Create Work Order]  [View History]       │
│  ───────────────────────────────────────────────────────────────── │
│  MAINTENANCE CALENDAR — Next 14 Days                                │
│  Feb 24  MCH-002  Recommended PM (URGENT) — Line 2 offline 8h      │
│  Mar 01  MCH-003  Scheduled PM — Overnight, no production impact   │
│  ───────────────────────────────────────────────────────────────── │
│  CAPACITY CEILING: 910 units/week  │  Demand target: 1,050/week    │
│  GAP: -140 units/week  → Overtime required for this week           │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Page 5: Production Planning

**Users:** Production Planner (primary)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Production Planning                          Week of Feb 24, 2026  │
│  MASTER PRODUCTION SCHEDULE — GANTT                                 │
│        Mon    Tue    Wed    Thu    Fri    Cap/day  Effective        │
│  Line1 [████] [████] [████] [████] [████]   55u     51u           │
│  Line2 [▓▓▓▓] [▓▓PM] [████] [████] [████]   60u     45u (75%)     │
│  Line3 [███░] [███░] [███░] [███░] [███░]   50u     44u (88%)     │
│  Line4 [DOWN] [DOWN] [████] [████] [████]   45u      0u (Mon-Tue)  │
│  Line5 [████] [████] [████] [████] [████]   58u     56u           │
│  OT   [░░░█] [████] [░░░░] [░░░░] [░░░░]          +70u            │
│  TOTAL: 1,091 planned  │  TARGET: 1,050  │  SURPLUS: +41 (buffer)  │
│  ───────────────────────────────────────────────────────────────── │
│  CAPACITY vs DEMAND                                                 │
│  1200│ demand ─────────────────────────── 1,050                   │
│   980│ capacity ─────────────────── 910/980/1120/1120              │
│   700│ overtime ──────── +140 / +70 / 0 / 0                       │
│       W07     W08     W09     W10                                  │
│  ───────────────────────────────────────────────────────────────── │
│  OVERTIME REQUIRED — W07 & W08                                      │
│  Additional units: 70/wk  │  Cost: $6,050/week                    │
│  [Authorize Overtime ✓]  [Reject — Adjust Target ✗]               │
│  ───────────────────────────────────────────────────────────────── │
│  MATERIAL REQUIREMENTS (BOM explosion, 4 weeks)                    │
│  SH-100  Steel Housing   4,200 req  ✓ OK (PO-018 due today)       │
│  VSA-200 Valve Seal     12,600 req  ✓ OK                           │
│  AM-300  Control Module  4,200 req  ⚠ SINGLE SOURCE RISK          │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Page 6: Supplier Management

**Users:** Procurement Officer (primary)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Supplier Management                                                 │
│  SUPPLIER SCORECARDS                                                 │
│  Supplier  Score  OTD%   Quality  Lead Time  Contract   Risk       │
│  SUP-A     87     92.5%  98.8%    4.2 days   Dec 2026  🟢 LOW      │
│  SUP-B     74     85.0%  97.9%    6.8 days   Jun 2026  🟡 MEDIUM   │
│  SUP-C     61     78.3%  96.1%    9.1 days   Mar 2026  🔴 HIGH     │
│  ───────────────────────────────────────────────────────────────── │
│  OPEN POs — AWAITING APPROVAL                     Total: $71,550   │
│  SUP-A  900 units Steel Housing  $46,800  Arr. Feb 27  [APPROVE]   │
│  SUP-B  500 units Steel Housing  $24,750  Arr. Mar 02  [APPROVE]   │
│  ───────────────────────────────────────────────────────────────── │
│  SUPPLY CHAIN RISK MAP                                              │
│  🔴 SINGLE SOURCE: Control Module (AM-300) — only SUP-C            │
│     Risk: If SUP-C fails, production stops in 8 days               │
│     Action: Qualify SUP-A as backup  [Start Qualification]        │
│                                                                      │
│  🟡 CONTRACT EXPIRY: SUP-B expires Jun 30 (127 days)               │
│     Action: Begin renegotiation  [Create Reminder]                 │
│  ───────────────────────────────────────────────────────────────── │
│  DELIVERY TRACKER                                                   │
│  PO-2026-041  SUP-A  500 units  Due Feb 23  ✓ On track             │
│  PO-2026-039  SUP-B  300 units  Due Feb 26  ⚠ 3 days late         │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Page 7: Weekly Intelligence Brief

**Users:** Plant Director, department heads — delivered every Monday at 09:45

```
┌─────────────────────────────────────────────────────────────────────┐
│  MANUFACTURING INTELLIGENCE BRIEF — Week 08, 2026                   │
│  Acme Manufacturing — Plant 01          Generated Mon 06 Feb        │
│  ───────────────────────────────────────────────────────────────── │
│  HEADLINE: Production at risk this week — MCH-002 failure could     │
│            cost $47K and disrupt 2-week output.                     │
│  ───────────────────────────────────────────────────────────────── │
│  SYSTEM HEALTH: 68/100  ⚠ AT RISK  (▼ from 81 last week)           │
│                                                                      │
│  Demand       🟡 WATCH    82/100  Trend +1.8%, trade show in 3 wks │
│  Inventory    🔴 AT RISK  61/100  2 SKUs below reorder point        │
│  Machines     🔴 AT RISK  55/100  MCH-002 degrading rapidly         │
│  Production   🟡 WATCH    74/100  Gap 140 u/wk, OT needed          │
│  Supply Chain 🟢 HEALTHY  82/100  SUP-B contract expiry in 127 d   │
│  ───────────────────────────────────────────────────────────────── │
│  3 CROSS-DOMAIN INSIGHTS THIS WEEK                                  │
│                                                                      │
│  1. MCH-002 degradation + growing demand = $94K combined risk       │
│     Capacity ceiling (910/wk) is BELOW base demand (1,050/wk).     │
│     If MCH-002 fails, gap widens to 280 u/wk.                      │
│                                                                      │
│  2. Demand anomaly (W05) created false safety stock signal          │
│     Spike was promotional — not structural. Hold the extra order.   │
│                                                                      │
│  3. SUP-C single-source risk growing with demand                    │
│     Control Module only from SUP-C. At +1.8%/wk demand growth,     │
│     SUP-C capacity insufficient in ~8 weeks.                        │
│  ───────────────────────────────────────────────────────────────── │
│  YOUR 3 PRIORITY ACTIONS THIS WEEK                                  │
│  [1] IMMEDIATE   Authorize MCH-002 maintenance (saves $43,400)      │
│  [2] THIS WEEK   Approve emergency POs for Steel Housing            │
│  [3] THIS MONTH  Begin SUP-A qualification for Control Module       │
│  ───────────────────────────────────────────────────────────────── │
│  [Download PDF]  [Share via Email]  [View Full Dashboard]           │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Page 8: Human Decision Queue

**Users:** All roles with approval authority

```
┌─────────────────────────────────────────────────────────────────────┐
│  Decision Queue                   3 items require your attention    │
│  ───────────────────────────────────────────────────────────────── │
│  ITEM 1 — URGENT                                 Expires in: 4 hrs  │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  RECOMMENDATION: Emergency Purchase Order                     │ │
│  │  Agent: Supplier Agent  │  Triggered: Inventory cascade       │ │
│  │                                                               │ │
│  │  AI REASONING:                                                │ │
│  │  PROD-C will reach zero in ~4 days at 68 units/day current   │ │
│  │  demand. No open POs exist. SUP-A lead time is 4 days — an  │ │
│  │  order placed today arrives exactly as stock hits zero.       │ │
│  │                                                               │ │
│  │  RECOMMENDED ACTION:                                          │ │
│  │  Place emergency PO with SUP-A: 800 units of PROD-C          │ │
│  │  Cost: $41,600  │  Expected delivery: Feb 28                 │ │
│  │  Confidence: 0.81  │  Data quality: 0.92                     │ │
│  │                                                               │ │
│  │  RISK IF DELAYED:                                             │ │
│  │  Every 24h delay adds ~18% stockout probability.             │ │
│  │  A 2-day stockout costs approximately $9,200 in lost margin. │ │
│  │                                                               │ │
│  │  [✓ APPROVE — PLACE PO NOW]  [✓ APPROVE, qty: ___]         │ │
│  │  [✗ REJECT — reason: _______________________________]        │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ITEM 2 — HIGH     Overtime Authorization Mon–Wed  +$12,100         │
│  ITEM 3 — MEDIUM   Dual-source qualification for AM-300             │
│  ───────────────────────────────────────────────────────────────── │
│  All decisions are logged with your name, timestamp, and reason.    │
│  Approved actions execute automatically within 5 minutes.           │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Page 9: AI Chat

**Users:** All roles

```
┌─────────────────────────────────────────────────────────────────────┐
│  AI Assistant                          Powered by AMIS Agents       │
│  Context: PROD-A  │  PLANT-01  │  Feb 2026                         │
│  ───────────────────────────────────────────────────────────────── │
│  💬 You: Why is production attainment lower this week?              │
│                                                                      │
│  🤖 AMIS: Two factors are contributing:                             │
│                                                                      │
│  1. Line 4 has been down since Feb 18 (MCH-004 bearing failure).   │
│     Removes 45 units/day. Expected return: today.                  │
│                                                                      │
│  2. Line 2 (MCH-002) running at 75% efficiency — vibration at      │
│     140% of baseline. Costs ~15 units/day.                         │
│                                                                      │
│  Combined impact: -60 units/day from normal capacity 220 u/day.    │
│  This explains the 94% attainment you are seeing.                  │
│                                                                      │
│  Recommendation: Schedule MCH-002 PM within 2 days. Once Line 4   │
│  returns today, attainment should recover to 98%+ this week.       │
│                                                                      │
│  [Schedule MCH-002 PM]  [View Machine Health Dashboard]            │
│  ───────────────────────────────────────────────────────────────── │
│  Suggested: "What happens if SUP-A is delayed 2 weeks?"            │
│             "Should we run overtime next week?"                     │
│             "Compare this week to last week"                        │
│  ───────────────────────────────────────────────────────────────── │
│  [ Ask anything about demand, inventory, machines, production... ]  │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Page 10: Onboarding Wizard (Day 1)

**Users:** IT Admin + one domain expert on first setup

```
STEP 1 (5 min)   Company & Plant Setup
                 Company name, timezone, industry, units (metric/imperial)

STEP 2 (15 min)  Upload Your Data
                 ┌──────────────────────────────────────────────────┐
                 │  📁 Drag & drop CSV/Excel files here            │
                 │                                                   │
                 │  ✓ demand_history.csv        (uploaded, valid)  │
                 │  ✓ inventory_snapshot.csv    (uploaded, valid)  │
                 │  ✓ machine_list.csv          (uploaded, valid)  │
                 │  ⏳ supplier_list.csv        (uploading...)     │
                 │  ○ bom_components.csv        (optional)         │
                 └──────────────────────────────────────────────────┘
                 Auto-detects column names, shows mapping for confirmation

STEP 3 (5 min)   Review What AMIS Found
                 "We found 52 weeks of demand, 12 products, 6 machines,
                  3 suppliers, and 48 BOM components."

STEP 4 (10 min)  First AI Run
                 Progress bar: Demand Agent... Inventory... Machine Health...
                 "Your first analysis is ready."

STEP 5 (5 min)   Your First Dashboard
                 Walks through top 3 findings.
                 Prompt: "Set up automated weekly analysis?"

STEP 6 (5 min)   Invite Your Team
                 Add users, assign roles, send invitations

STEP 7 (deferred) Connect Your ERP
                 "When ready to automate data sync, connect here."
```

---

## 8. Human-in-the-Loop Approval Workflow

### 8.1 Auto-Execute vs. Require Approval

| Decision Type | Default Policy | Configurable? |
|---------------|---------------|--------------|
| Send alert notification | Always auto-execute | No |
| Flag item in dashboard | Always auto-execute | No |
| Small reorder (< $X, confidence > 0.85) | Auto-execute | Yes |
| Standard reorder (< $Y, confidence > 0.70) | Notify + auto-execute in 4h if no response | Yes |
| Large reorder (> $Y) | Require explicit approval | Yes |
| Overtime (< Z hours) | Notify + auto-execute in 2h | Yes |
| Overtime (> Z hours) | Require plant director approval | Yes |
| Contract manufacturing activation | Require dual approval | Yes |
| Supplier dual-source qualification | Require procurement + legal | Yes |
| Emergency re-plan | Notify all affected roles; require acknowledgment | Yes |

Dollar and hour thresholds (X, Y, Z) are configured per tenant in System Configuration.

### 8.2 The Approval Flow

```
AI generates recommendation
        │
        ├── confidence > 0.85 AND value < auto_threshold
        │         → Auto-execute immediately + log
        │
        ├── confidence 0.65–0.85 OR value < notify_threshold
        │         → Create approval item + notify
        │         → Wait N hours
        │               ├── Human approves → Execute + log
        │               ├── Human rejects → Log + feedback
        │               └── No response   → Auto-execute + log
        │
        └── confidence < 0.65 OR value > require_threshold
                  → Create URGENT approval item + notify + escalate
                  → WAIT for explicit human response (no auto-timeout)
                        ├── Human approves → Execute + log
                        └── Human rejects → Log + feedback + re-alert if still risky
```

### 8.3 Escalation Matrix

```
Procurement Officer   → approves POs up to $10,000
  └── PO > $10,000 or no response in 4h → escalate to Plant Director

Plant Director        → approves all remaining items
  └── No response in 8h AND CRITICAL → SMS + email to leadership

Maintenance Manager   → approves maintenance scheduling < 4h downtime
  └── > 4h downtime or > $5,000 cost → escalate to Plant Director
```

### 8.4 Audit Log — Every Decision Recorded

```sql
CREATE TABLE audit_log (
    id              UUID PRIMARY KEY,
    tenant_id       UUID NOT NULL,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- immutable, server-side
    actor_user_id   UUID,
    actor_role      TEXT,
    action_type     TEXT,   -- 'approve_po', 'reject_recommendation', 'configure_threshold'
    entity_type     TEXT,
    entity_id       TEXT,
    before_state    JSONB,
    after_state     JSONB,
    ip_address      INET,
    notes           TEXT
);
-- Append-only: no UPDATE or DELETE on this table
```

---

## 9. Technical Architecture

### 9.1 Full System Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                  MANUFACTURER'S ENVIRONMENT                         │
│  SAP/Oracle  │  MES/SCADA  │  IoT Sensors  │  CMMS  │  CSV       │
└───────┬──────┴──────┬───────┴───────┬────────┴───┬────┴────┬───────┘
        │             │               │             │          │
    REST API      OPC-UA/MQTT       MQTT         REST API  File Upload
        │             │               │             │          │
┌───────▼─────────────▼───────────────▼─────────────▼──────────▼──────┐
│                       API GATEWAY (nginx / ALB)                      │
│                  Rate limiting, SSL termination, routing              │
└─────────────────────────────┬────────────────────────────────────────┘
                              │
              ┌───────────────┼──────────────────┐
              ▼               ▼                  ▼
     ┌──────────────┐ ┌──────────────┐  ┌──────────────┐
     │  FastAPI     │ │  FastAPI     │  │  FastAPI     │  (3+ instances)
     │  Auth routes │ │  Agent API   │  │  Dashboard   │
     │  Webhooks    │ │  Config API  │  │  Chat API    │
     └──────┬───────┘ └──────┬───────┘  └──────┬───────┘
            └────────────────┼──────────────────┘
                             │
            ┌────────────────▼────────────────────┐
            │               Redis                  │
            │  Celery broker │ Result cache        │
            │  Session store │ Rate limit counters │
            │  Pub/Sub (event cascade triggers)    │
            │  Latest sensor values (real-time)    │
            └───────┬─────────────────────────────┘
                    │
        ┌───────────▼──────────────────────────────────┐
        │         Celery Workers (Agent Execution)       │
        │                                               │
        │  Critical Queue  High Queue   Normal Queue    │
        │  (emergency)     (events)     (scheduled)     │
        │                                               │
        │  Demand  │ Inventory  │ Machine Health        │
        │  Production  │ Supplier  │ Orchestrator        │
        │                                               │
        │  All agents → Claude API (Anthropic) via HTTPS│
        └───────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                │
│  PostgreSQL + TimescaleDB        S3 / Blob Store                  │
│  ├── demand_history              ├── CSV uploads                  │
│  ├── inventory_positions         ├── PDF reports                  │
│  ├── machine_fleet               ├── Data exports                 │
│  ├── agent_run_results           └── Backups                      │
│  ├── approval_items                                               │
│  └── audit_log                   Redis (above)                    │
│  TimescaleDB hypertables:                                         │
│  └── sensor_readings (per-minute per sensor)                      │
└───────────────────────────────────────────────────────────────────┘

          ┌────────────────────────────────────┐
          │             FRONTEND                │
          │  Streamlit (MVP — weeks 1–6)        │
          │  React + Next.js (production)        │
          │  Hosted on Vercel / CloudFront       │
          └────────────────────────────────────┘
```

### 9.2 Core Database Schema

```sql
-- Tenants
CREATE TABLE tenants (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    slug        TEXT UNIQUE NOT NULL,
    plan        TEXT NOT NULL DEFAULT 'starter',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID REFERENCES tenants(id),
    email           TEXT NOT NULL,
    hashed_password TEXT,
    role            TEXT NOT NULL,  -- plant_director, demand_planner, etc.
    is_active       BOOLEAN DEFAULT TRUE,
    last_login      TIMESTAMPTZ
);

-- Agent Run Tracking
CREATE TABLE agent_runs (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id         UUID REFERENCES tenants(id),
    agent_type        TEXT NOT NULL,
    triggered_by      UUID REFERENCES users(id),  -- null if scheduled
    trigger_reason    TEXT,  -- 'scheduled:weekly', 'cascade:demand', 'manual'
    cascade_depth     INT DEFAULT 0,
    input_params      JSONB,
    status            TEXT DEFAULT 'pending',  -- pending, running, completed, failed
    started_at        TIMESTAMPTZ,
    completed_at      TIMESTAMPTZ,
    output            JSONB,   -- full agent result
    llm_trace         JSONB,   -- self.trace from BaseAgent
    token_usage       INT,
    confidence_score  FLOAT,
    data_quality_score FLOAT,
    error_message     TEXT,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

-- Human Approval Queue
CREATE TABLE approval_items (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id               UUID REFERENCES tenants(id),
    agent_run_id            UUID REFERENCES agent_runs(id),
    recommendation_type     TEXT,  -- 'purchase_order', 'overtime', 'maintenance'
    recommendation_payload  JSONB,
    ai_reasoning            TEXT,
    confidence_score        FLOAT,
    estimated_value         FLOAT,
    urgency                 TEXT,  -- CRITICAL, HIGH, MEDIUM, LOW
    status                  TEXT DEFAULT 'pending',
    assigned_to_role        TEXT,
    expires_at              TIMESTAMPTZ,
    decision_by_user_id     UUID REFERENCES users(id),
    decision_at             TIMESTAMPTZ,
    decision_reason         TEXT,
    executed_at             TIMESTAMPTZ,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

-- Sensor Time-Series (TimescaleDB hypertable)
CREATE TABLE sensor_readings (
    time        TIMESTAMPTZ NOT NULL,
    tenant_id   UUID NOT NULL,
    machine_id  TEXT NOT NULL,
    sensor_name TEXT NOT NULL,
    value       FLOAT NOT NULL,
    unit        TEXT,
    quality     INT DEFAULT 192
);
SELECT create_hypertable('sensor_readings', 'time');
CREATE INDEX ON sensor_readings (tenant_id, machine_id, sensor_name, time DESC);
```

### 9.3 Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| API framework | FastAPI | Async-native Python; shares runtime with agents |
| Primary database | PostgreSQL + TimescaleDB | One DB for relational + time-series; native SQL joins |
| Cache / queue | Redis | Celery broker + result cache + pub/sub in one service |
| Task queue | Celery + Celery Beat | Retries, distributed workers, priority queues |
| MVP frontend | Streamlit | Python-native; no JS required for MVP; ship in days |
| Production frontend | React + Next.js | SSR, type safety, component ecosystem |
| Auth | JWT + RBAC + PostgreSQL RLS | 4-layer tenant isolation |
| Day 1 data | CSV upload | Removes 6-month integration barrier to first value |
| Notifications | SendGrid + Slack + Teams | Covers email, dev tools, enterprise platforms |
| Deployment | Docker Compose (dev) → Kubernetes (prod) | Cloud-agnostic standard |

### 9.4 Security Requirements

- All API communication: TLS 1.3 minimum
- JWT: 1-hour expiry; refresh tokens 24-hour in httpOnly cookies
- JWT revocation via Redis blacklist (logout, role changes)
- PostgreSQL row-level security on all tenant tables
- API key encryption at rest (AES-256 for ERP connector credentials)
- Rate limiting per user (API) and per tenant (Claude API spend)
- Secrets management: AWS Secrets Manager / Azure Key Vault — never in `.env` for production
- Audit log: append-only (no UPDATE/DELETE)
- GDPR compliance: data residency config, user deletion workflows

---

## 10. API Design

### Authentication

```
POST   /api/v1/auth/login              {email, password} → {access_token, refresh_token}
POST   /api/v1/auth/refresh            {refresh_token} → {access_token}
POST   /api/v1/auth/logout             Revokes refresh token
POST   /api/v1/auth/forgot-password    Sends reset email
POST   /api/v1/auth/reset-password     {token, new_password}
GET    /api/v1/auth/me                 Returns current user + role
```

### Agent Runs

```
POST   /api/v1/agents/{agent_type}/run
       Body: {params: {product_id, plant_id, planning_weeks}}
       Returns: {run_id, status: "pending"}

GET    /api/v1/agents/runs/{run_id}
       Returns: {status, output, confidence_score, error}

GET    /api/v1/agents/runs?agent_type=demand&limit=20
       Lists historical runs for the tenant

POST   /api/v1/agents/pipeline/run
       Triggers full 5-agent cascade
       Returns: {pipeline_run_id, agent_run_ids: [...]}

GET    /api/v1/agents/pipeline/{pipeline_run_id}
       Returns: {status, agent_statuses, report}
```

### Dashboard Data

```
GET    /api/v1/dashboard/command-center
GET    /api/v1/dashboard/demand?product_id=PROD-A
GET    /api/v1/dashboard/inventory?product_id=PROD-A
GET    /api/v1/dashboard/machines?plant_id=PLANT-01
GET    /api/v1/dashboard/machines/{machine_id}/sensors
GET    /api/v1/dashboard/production?product_id=PROD-A&weeks=4
GET    /api/v1/dashboard/suppliers
GET    /api/v1/dashboard/weekly-brief
```

### Approvals

```
GET    /api/v1/approvals?status=pending&assigned_to=me
GET    /api/v1/approvals/{approval_id}
POST   /api/v1/approvals/{approval_id}/approve    {override_value, notes}
POST   /api/v1/approvals/{approval_id}/reject     {reason}
```

### Webhooks (for ERP / IoT integrations)

```
POST   /api/v1/webhooks/erp/inventory-update
POST   /api/v1/webhooks/erp/sales-order-new        → triggers pipeline re-run
POST   /api/v1/webhooks/erp/purchase-order-update
POST   /api/v1/webhooks/iot/sensor-reading          → threshold check → cascade
POST   /api/v1/webhooks/supplier/delivery-update    → cascade to production
POST   /api/v1/webhooks/mes/production-event
```

### Chat

```
POST   /api/v1/chat/message    {session_id, message, context: {product_id}}
GET    /api/v1/chat/sessions/{session_id}/history
```

### Configuration

```
GET/PUT  /api/v1/config/integrations/{connector_id}
POST     /api/v1/config/integrations/{connector_id}/test
GET/PUT  /api/v1/config/schedules
GET/PUT  /api/v1/config/thresholds
GET/PUT  /api/v1/config/approvals-authority
GET/PUT  /api/v1/config/notifications
```

---

## 11. Phased Build Plan

### Phase 1 — Working MVP (Weeks 1–6)

**Goal:** Manufacturer uploads CSV, sees dashboard, gets alerts.

| Week | Deliverables |
|------|-------------|
| **1** | `.env` config (fix API key now). FastAPI skeleton. PostgreSQL schema (5 core tables). Redis + Docker Compose. Replace `sample_data.py` bodies with async DB queries. |
| **2** | CSV upload API. ETL pipeline (validate → normalize → load). Column mapping UI in Streamlit. End of week: upload CSV and see data in DB. |
| **3** | All 5 agent tools read from PostgreSQL. `POST /api/v1/agents/pipeline/run` works end-to-end. Store results in `agent_runs` table. |
| **4** | Streamlit dashboard: Command Center, Demand, Inventory, Machine Health, Production, Supplier pages reading from latest `agent_run` results. |
| **5** | JWT auth + login. Multi-tenant `tenant_id` on all tables + row-level security. Test with 2 tenants to verify isolation. |
| **6** | Onboarding wizard. APScheduler weekly pipeline. Email notification (SendGrid) on CRITICAL alerts. Demo to first pilot customer. |

**Exit criteria:** Manufacturer uploads CSV, sees real dashboard, gets email if something is critical.

---

### Phase 2 — Core Product (Weeks 7–14)

**Goal:** All dashboards complete, ERP connector, human approvals, reactive triggers, Slack alerts.

| Week | Deliverables |
|------|-------------|
| **7** | Human Decision Queue: `approval_items` table, workflow logic, approval queue page, connect PO recommendations to queue. |
| **8** | Celery workers: move agent runs to async Celery tasks. API returns `run_id` immediately. Flower monitoring dashboard. |
| **9** | Cascade evaluator: `run_cascade_evaluation()`. End of week: inventory threshold breach automatically triggers Supplier Agent. |
| **10** | Odoo ERP connector (easiest API). Connector framework: abstract base, credential storage, sync scheduler, field mapping. |
| **11** | SAP connector (basic read-only: inventory, POs, sales orders). SAP webhook receiver. |
| **12** | Notification system: Slack webhook, Teams webhook, HTML email templates, notification preferences per user. |
| **13–14** | React + Next.js frontend: all 6 dashboard pages + Human Decision Queue. Streamlit retired. |

**Exit criteria:** ERP syncs data → agents run automatically → alerts fire → humans approve from clean UI → audit trail records everything.

---

### Phase 3 — Enterprise Ready (Weeks 15–22)

**Goal:** Real-time IoT, multi-plant, SSO, audit compliance, PDF weekly brief.

| Week | Deliverables |
|------|-------------|
| **15–16** | TimescaleDB sensor tables. MQTT broker. IoT webhook. Real-time sensor threshold monitoring. Machine Health reads TimescaleDB. |
| **17** | Multi-plant: `plant_id` on tables, plant selector in UI, cross-plant Orchestrator summary. |
| **18** | SSO: SAML 2.0 (Azure AD, Okta). JIT user provisioning. Role mapping from SSO groups. |
| **19** | Audit log: append-only table, all writes instrumented, export to CSV/PDF. SOC 2 documentation. |
| **20** | Weekly Intelligence Brief: PDF generation (WeasyPrint), formatted HTML email, Monday 09:45 delivery. |
| **21** | Advanced analytics: forecast vs. actual accuracy, recommendation acceptance rate, cost savings attribution. |
| **22** | AI Chat: full Orchestrator Agent behind chat endpoint, conversation history in DB, context-aware with dashboard links. |

**Exit criteria:** Enterprise customer connects SSO, sees multi-plant data, receives weekly PDF, passes basic security audit.

---

### Phase 4 — Scale & Differentiation (Ongoing)

| Initiative | Description |
|-----------|-------------|
| **Mobile app** | React Native for Plant Floor Supervisor: push alerts, shift target, machine QR scan |
| **ML predictive models** | Gradient-boosted models trained on per-tenant sensor + failure history. LLM explains ML output. |
| **Industry templates** | Pre-built configs: Automotive Parts, Food & Beverage (shelf life, temp), Pharma (batch tracking, FDA 21 CFR Part 11) |
| **Integration marketplace** | 20+ ERP/MES/CMMS connectors. Community-contributed. Revenue share. |
| **Supplier portal** | Lightweight portal: suppliers self-report delivery status, receive PO confirmations |
| **What-if engine** | Full pipeline runs with modified inputs. Comparative report. Export to Excel. |

---

## 12. What Makes This Different

### What Existing Tools Do Well (and Should Not Be Replaced)

| Tool | What It Does Well |
|------|------------------|
| SAP / Oracle ERP | Master data, financial records, compliance, transaction history — irreplaceable |
| PowerBI / Tableau | Self-service BI, custom reporting, "what happened?" questions with known dimensions |
| MES | Real-time production tracking, work order execution, source of truth for shop floor |
| CMMS | Maintenance work order management, PM scheduling, spare parts inventory |
| Excel | Flexibility — manufacturers always use Excel for one-off analysis |

AMIS reads from these systems. It does not replace them.

### What Existing Tools Do Poorly

**Cross-domain reasoning.** SAP knows inventory. The MES knows machine status. They are separate systems. No existing tool looks at them together and says: *"Your inventory is low AND your top machine is about to fail AND your best supplier just reported a 3-day delay — together, these mean you will miss your customer commitment next Tuesday."* Manufacturers figure this out manually, in a Monday morning meeting, from printed reports, 48 hours after the data was available.

**Natural language.** PowerBI dashboards require someone who knows how to build them. A Plant Director cannot ask "why are we missing plan this week?" and receive a specific, contextualized answer in plain English.

**Proactive alerting with context.** ERP systems alert on thresholds — but the alert says "inventory low," not "inventory is low, your safety stock model is wrong for current demand variability, your best supplier has 15% late delivery rate this quarter, so order 2 weeks early."

**Synthesis across all domains simultaneously.** A human planner looks at 12 weeks of history, today's inventory, next week's maintenance schedule, and the supplier contract expiry — all at once — to make a judgment call. This is a human cognitive task done in spreadsheets today. AMIS does it automatically, every morning, across all five domains.

### The Value Proposition in One Sentence

> **AMIS is the first system that tells manufacturers WHY something is happening and WHAT to do about it — not just what the numbers are.**

### Business Case (Illustrative for a $50M Revenue Manufacturer)

| Improvement | How AMIS Delivers It | Annual Value |
|-------------|---------------------|-------------|
| Reduce unplanned downtime 30% | Predictive maintenance before failure | $120K–$400K |
| Reduce stockouts 50% | Demand-driven inventory policy | $80K–$250K |
| Reduce safety stock 15% | Precise calculation using real demand variability | $50K–$150K |
| Reduce premium freight 40% | Earlier reorder triggers, fewer emergencies | $30K–$100K |

**Total annual value: $280K–$900K.** A SaaS price of $3K–$8K/month is an easy ROI conversation.

---

## 13. Production File Structure

```
amis/
├── api/
│   ├── main.py                      # FastAPI app factory + startup
│   ├── middleware/
│   │   ├── auth.py                  # JWT validation, tenant context injection
│   │   └── rate_limit.py            # Per-user and per-tenant rate limits
│   └── routes/
│       ├── auth.py
│       ├── agents.py                # Trigger + status endpoints
│       ├── dashboard.py             # All dashboard data endpoints
│       ├── approvals.py             # Human decision queue
│       ├── config.py                # Tenant configuration
│       ├── webhooks.py              # ERP / IoT event receivers
│       └── chat.py                  # AI Chat endpoint
│
├── agents/
│   ├── base_agent.py               # KEEP — add async, structured logging
│   ├── demand_agent.py             # KEEP — swap tool data sources only
│   ├── inventory_agent.py
│   ├── machine_health_agent.py
│   ├── production_agent.py
│   ├── supplier_agent.py
│   └── orchestrator_agent.py
│
├── data/
│   ├── connectors/
│   │   ├── base_connector.py       # Abstract connector interface
│   │   ├── postgres_connector.py   # Reads from normalized DB (replaces sample_data)
│   │   ├── sap_connector.py
│   │   ├── odoo_connector.py
│   │   ├── mqtt_connector.py       # IoT sensor ingestion
│   │   └── csv_connector.py        # CSV upload processing
│   └── etl/
│       ├── pipeline.py             # ETL orchestration
│       ├── normalizer.py           # Unit + schema normalization
│       ├── quality_scorer.py       # Data quality scoring (0.0–1.0)
│       └── loaders.py              # PostgreSQL load operations
│
├── db/
│   ├── session.py                  # AsyncSession factory, tenant context
│   ├── models/                     # SQLAlchemy ORM models
│   └── migrations/                 # Alembic migrations
│
├── tools/
│   ├── forecasting.py              # KEEP signatures; replace sample_data bodies
│   ├── inventory.py
│   ├── machine_health.py
│   ├── production.py
│   ├── supplier.py
│   ├── orchestrator.py             # KEEP _compute_report(); add unit tests
│   ├── tracer.py                   # KEEP as-is
│   └── validator.py                # KEEP as-is; expand to integration tests
│
├── prompts/                        # KEEP structure; add DB-backed versioning later
│
├── workers/
│   ├── celery_app.py               # Celery configuration + priority queues
│   ├── agent_tasks.py              # Agent run Celery tasks
│   ├── cascade_evaluator.py        # Post-run cascade condition logic
│   ├── scheduler.py                # Celery Beat scheduled tasks
│   └── notification_tasks.py       # Email / Slack / Teams send tasks
│
├── notifications/
│   ├── email.py                    # SendGrid integration + HTML templates
│   ├── slack.py                    # Slack webhook sender
│   └── teams.py                    # Microsoft Teams webhook sender
│
├── frontend/                       # Streamlit (MVP) → React + Next.js (Phase 2)
│
├── tests/
│   ├── unit/                       # Tool function tests, scorer tests
│   ├── integration/                # Full agent run tests with DB
│   └── scenarios/                  # Expand from current ScenarioValidator
│
├── .env.example                    # Template — never commit real .env
├── config.py                       # REPLACE hardcoded key with strict env loading
├── docker-compose.yml              # Local dev: FastAPI + PostgreSQL + Redis + Celery
├── Dockerfile
└── requirements.txt
```

---

## 14. Key Decisions Reference

| Decision | Choice | Rationale |
|----------|--------|-----------|
| API framework | FastAPI | Async-native, shares Python runtime with agents |
| Primary database | PostgreSQL + TimescaleDB | One DB for relational + time-series; native SQL joins |
| Cache / queue | Redis | Celery broker + result cache + pub/sub in one service |
| Task queue | Celery + Celery Beat | Retries, distributed, priority queues |
| MVP frontend | Streamlit | Python-native; no JS; ships in days |
| Production frontend | React + Next.js | SSR, TypeScript, component ecosystem |
| Auth | JWT + RBAC + PostgreSQL RLS | Four-layer tenant isolation |
| Day 1 data path | CSV upload | Removes 6-month integration barrier to first value |
| Agent pattern | ReAct loop (keep from current) | Proven, extensible, auditable via `self.trace` |
| LLM calls | Async (`ainvoke`) | Required for non-blocking API |
| Notifications | SendGrid + Slack + Teams | Email + developer tools + enterprise platforms |
| Deployment | Docker Compose → Kubernetes | Cloud-agnostic, well-documented standard |
| First ERP connector | Odoo (open-source) | Easiest API to test; good for SME market |
| Scheduler (MVP) | APScheduler (in-process) | Simple; ships in hours; replace with Celery Beat in Phase 3 |
| Time-series data | TimescaleDB (PostgreSQL ext.) | Sensor queries fast; JOIN with production data natively |
| Secrets | AWS Secrets Manager / Key Vault | Never in environment variables for production |

---

## What To Build This Week

Based on everything above, the correct first 3 actions are:

1. **Today:** Rotate the hardcoded API key in `config.py` and move to `.env`. This unblocks everything safely.
2. **This week:** Create the FastAPI project structure and wrap the 3 most important agents (Demand, Inventory, Orchestrator) behind `POST /api/v1/agents/{type}/run` endpoints.
3. **Next week:** Add PostgreSQL schema, store `agent_run` results, and build a 2-page Streamlit dashboard reading from the DB.

Everything else in this document builds on those 3 weeks. The agents are done. The infrastructure is the roadmap.

---

*AMIS Real-World Blueprint — Version 1.0 — February 2026*
*Next review: after Phase 1 pilot customer feedback*
