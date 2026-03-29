# AMIS — Autonomous Manufacturing Intelligence System
## Complete Project Documentation (A to Z)

---

## TABLE OF CONTENTS

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Complete Directory Structure](#3-complete-directory-structure)
4. [Architecture & System Design](#4-architecture--system-design)
5. [Database Schema](#5-database-schema)
6. [Backend & API](#6-backend--api)
7. [Authentication & Authorization](#7-authentication--authorization)
8. [Agent System](#8-agent-system)
9. [Tools — Algorithms & Calculations](#9-tools--algorithms--calculations)
10. [System Prompts](#10-system-prompts)
11. [Frontend / UI](#11-frontend--ui)
12. [Agent Pipeline — Execution Order & Data Flow](#12-agent-pipeline--execution-order--data-flow)
13. [Tool-by-Tool Input & Output — Demand Forecasting Agent](#13-tool-by-tool-input--output--demand-forecasting-agent)
14. [Tool-by-Tool Input & Output — Inventory Management Agent](#14-tool-by-tool-input--output--inventory-management-agent)
15. [Tool-by-Tool Input & Output — Machine Health Agent](#15-tool-by-tool-input--output--machine-health-agent)
16. [Tool-by-Tool Input & Output — Production Planning Agent](#16-tool-by-tool-input--output--production-planning-agent)
17. [Tool-by-Tool Input & Output — Supplier Agent](#17-tool-by-tool-input--output--supplier-agent)
18. [Cross-Agent Data Flow](#18-cross-agent-data-flow)
19. [Configuration & Environment](#19-configuration--environment)
20. [Quick Start Guide](#20-quick-start-guide)
21. [Project Statistics](#21-project-statistics)

---

## 1. Project Overview

**AMIS** (Autonomous Manufacturing Intelligence System) is a full-stack, AI-driven manufacturing operations platform. It uses a multi-agent architecture powered by **LangChain + Claude Sonnet 4** to autonomously monitor, forecast, plan, and procure — giving manufacturers a single unified intelligence layer across demand, inventory, machines, production, and supply chain.

### What Problem It Solves

Traditional manufacturing runs 5–6 departments in silos:
- Sales forecasting never talks to production planning
- A broken machine doesn't automatically update the replenishment plan
- A supplier contract expiring in 90 days doesn't trigger a procurement alert

AMIS connects all these domains through AI agents that share context and data, producing a **daily Manufacturing Intelligence Report** that tells exactly what needs to happen to keep production running, costs controlled, and customers served.

### Key Capabilities

| Capability | Description |
|---|---|
| Demand Forecasting | Multi-scenario forecasts (pessimistic/base/optimistic) with anomaly detection |
| Inventory Optimization | Safety stock, reorder points, EOQ, stockout risk (Monte Carlo) |
| Machine Health Monitoring | OEE, MTBF-based failure prediction, sensor anomaly detection |
| Production Planning | Master Production Schedule, bottleneck analysis, capacity gap evaluation |
| Supplier Procurement | Purchase order generation, delivery risk simulation, dual-source optimization |
| Orchestration | All 5 agents run in sequence, cross-domain risks identified, unified report |
| Natural Language Interface | Ask any question in plain English, routed to the right agent |
| Crisis Negotiation | Multi-round AI negotiation for demand spikes, supplier failures, machine breakdowns |

---

## 2. Technology Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Core language |
| FastAPI | 0.109.0 | Async REST API framework |
| LangChain | 0.1.0 | LLM orchestration & tool binding |
| LangChain-Anthropic | 0.1.0 | Claude model integration |
| Claude Sonnet 4 | claude-sonnet-4-6 | LLM powering all agents |
| SQLite | Built-in | Persistent database (amis.db) |
| Pydantic | 2.5.3 | Data validation & serialization |
| Uvicorn | 0.27.0 | ASGI server |
| Python-dotenv | 1.0.0 | Environment variable management |

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React | 18.2.0 | UI framework |
| Vite | 5.0.11 | Build tool & dev server |
| TailwindCSS | 3.4.1 | Utility-first CSS framework |
| Framer Motion | 10.18.0 | Animations & transitions |
| Recharts | 2.10.3 | Charts & data visualization |
| React Router DOM | 6.21.1 | Client-side routing |
| TanStack React Query | 5.17.9 | Server state management |
| Zustand | 4.4.7 | Client state management |
| Axios | 1.6.5 | HTTP client |
| Lucide React | 0.303.0 | Icon library |

---

## 3. Complete Directory Structure

```
amis_phase_final/
│
├── .env                               # API keys (do not commit)
├── .env.example                       # Environment variable template
├── config.py                          # Global config (model, temperature, tokens)
├── app.py                             # Legacy Streamlit entry point
├── main.py                            # Standalone CLI entry point
├── setup.sh                           # Linux/Mac setup script
├── setup.bat                          # Windows setup script
├── START_FRONTEND.bat                 # Frontend launcher
├── requirements.txt                   # Root Python dependencies
│
├── agents/                            # AI Agent classes
│   ├── __init__.py
│   ├── base_agent.py                  # ReAct Loop foundation (247 lines)
│   ├── demand_agent.py                # Demand Forecasting Agent (74 lines)
│   ├── inventory_agent.py             # Inventory Management Agent (92 lines)
│   ├── machine_health_agent.py        # Machine Health Agent (69 lines)
│   ├── production_agent.py            # Production Planning Agent (84 lines)
│   ├── supplier_agent.py              # Supplier & Procurement Agent (87 lines)
│   └── orchestrator_agent.py          # Master Orchestrator (106 lines)
│
├── tools/                             # Tool implementations (algorithms)
│   ├── __init__.py                    # Tool registry (100 lines)
│   ├── forecasting.py                 # Demand forecasting tools (241 lines)
│   ├── simulation.py                  # Monte Carlo profit simulation (191 lines)
│   ├── anomaly.py                     # Anomaly detection (77 lines)
│   ├── inventory.py                   # Inventory calculations (629 lines)
│   ├── machine_health.py              # OEE, MTBF, sensor analysis (768 lines)
│   ├── production.py                  # MPS, BOM, bottleneck (765 lines)
│   ├── supplier.py                    # PO generation, risk assessment (825 lines)
│   ├── orchestrator.py                # Agent bridging & synthesis (554 lines)
│   ├── scenario.py                    # What-if scenario analysis (692 lines)
│   ├── tracer.py                      # Execution audit log (370 lines)
│   └── validator.py                   # Data validation utilities (227 lines)
│
├── prompts/                           # Agent system prompts (personalities)
│   ├── __init__.py
│   ├── demand_prompts.py
│   ├── inventory_prompts.py
│   ├── machine_health_prompts.py
│   ├── production_prompts.py
│   ├── supplier_prompts.py
│   └── orchestrator_prompts.py
│
├── data/                              # Data access layer
│   ├── __init__.py
│   ├── database_queries.py            # All DB query wrapper functions
│   ├── sample_data.py                 # Simulated data generators
│   └── migrate_all_data.py            # Data migration utilities
│
├── backend/                           # FastAPI server & database
│   ├── main.py                        # FastAPI app + all endpoints (150+ lines)
│   ├── database.py                    # SQLite operations (100+ lines)
│   ├── auth.py                        # JWT auth & RBAC (60+ lines)
│   ├── schema.sql                     # Full DB schema (300+ lines)
│   ├── amis.db                        # SQLite database file (280 KB)
│   ├── requirements.txt               # Backend Python deps
│   ├── agent_negotiation.py           # Agent negotiation system
│   ├── ai_database_bridge.py          # AI <-> Database integration layer
│   ├── approval_system.py             # Approval workflow system
│   ├── exports.py                     # CSV/Excel export utilities
│   ├── pipeline_formatter.py          # Result formatting helpers
│   ├── init_database.py               # DB initialization script
│   ├── init_users.py                  # Default user seeding
│   ├── populate_full_database.py      # Sample data loader
│   ├── test_api_direct.py             # API endpoint tests
│   └── test_database_queries.py       # Database query tests
│
├── frontend/                          # React + Vite application
│   ├── package.json                   # Node dependencies & scripts
│   ├── vite.config.js                 # Vite config (proxy: localhost:8000)
│   ├── tailwind.config.js             # Tailwind theme customization
│   ├── postcss.config.js              # PostCSS config
│   ├── index.html                     # HTML shell
│   └── src/
│       ├── main.jsx                   # React entry point
│       ├── App.jsx                    # Router + route definitions
│       ├── index.css                  # Global styles
│       ├── pages/
│       │   ├── Login.jsx              # Authentication page
│       │   ├── Dashboard.jsx          # Command center / system health
│       │   ├── Pipeline.jsx           # 5-agent pipeline runner
│       │   ├── DemandIntelligence.jsx # Demand forecasting UI
│       │   ├── InventoryControl.jsx   # Inventory management UI
│       │   ├── MachineHealth.jsx      # Machine fleet monitoring UI
│       │   ├── ProductionPlanning.jsx # Production schedule UI
│       │   ├── SupplierManagement.jsx # Supplier & procurement UI
│       │   ├── Chat.jsx               # Natural language agent interface
│       │   └── Negotiation.jsx        # Crisis negotiation scenarios UI
│       ├── components/
│       │   ├── Layout.jsx             # App shell + sidebar navigation
│       │   ├── Card.jsx               # Reusable card container
│       │   ├── Badge.jsx              # Status badge (Normal/Warning/Critical)
│       │   ├── Modal.jsx              # Generic dialog wrapper
│       │   ├── ForecastInputModal.jsx # Demand forecast entry form
│       │   ├── InventoryAdjustmentModal.jsx  # Stock adjustment form
│       │   ├── MachineDetailModal.jsx # Equipment details popup
│       │   ├── WorkOrderModal.jsx     # Maintenance work order form
│       │   ├── ScheduleEditModal.jsx  # Production schedule editor
│       │   ├── SupplierDetailModal.jsx # Supplier info popup
│       │   ├── ProductSelector.jsx    # Product dropdown
│       │   ├── DateRangePicker.jsx    # Date range selector
│       │   ├── ActivityLog.jsx        # Recent activity feed
│       │   └── ExportButton.jsx       # CSV/JSON export button
│       └── lib/
│           ├── api.js                 # Axios API client (all endpoints)
│           ├── utils.js               # Helper functions
│           └── mockData.js            # Mock data for development
│
├── pages/                             # Legacy Streamlit pages
│   ├── 1_Pipeline.py
│   ├── 2_Ask_AMIS.py
│   ├── 3_Machine_Floor.py
│   └── 4_Validator.py
│
├── test_api_direct.py                 # Root-level API tests
├── test_api_key.py                    # API key validation
├── test_database_queries.py           # Database query tests
└── [70+ .md documentation files]     # Guides, summaries, blueprints
```

---

## 4. Architecture & System Design

### High-Level Architecture

```
┌────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                     │
│  Dashboard │ Pipeline │ Demand │ Inventory │ Machines   │
│  Production │ Suppliers │ Chat │ Negotiation            │
│                    Port: 5173                           │
└────────────────────────┬───────────────────────────────┘
                         │ HTTP (Axios)
                         ▼
┌────────────────────────────────────────────────────────┐
│                 BACKEND (FastAPI)                        │
│           REST API — Port: 8000                         │
│   Auth │ Agents │ Pipeline │ Chat │ Data CRUD           │
└──────────┬─────────────────────────────────────────────┘
           │
    ┌──────┴──────────────────────┐
    │                             │
    ▼                             ▼
┌────────────┐          ┌──────────────────────────┐
│  SQLite DB │          │   ORCHESTRATOR AGENT      │
│  amis.db   │          │  (LangChain + Claude)      │
└────────────┘          └──────────┬───────────────┘
                                   │ runs in sequence
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                     ▼
     ┌──────────────┐   ┌──────────────┐    ┌──────────────┐
     │ Demand Agent │   │Inventory Agent│    │Machine Health │
     └──────┬───────┘   └──────┬───────┘    └──────┬───────┘
            │                  │                    │
            ▼                  ▼                    ▼
     ┌──────────────────────────────────────────────────┐
     │              Production Planning Agent            │
     └──────────────────────────┬───────────────────────┘
                                │
                                ▼
     ┌──────────────────────────────────────────────────┐
     │           Supplier & Procurement Agent             │
     └──────────────────────────────────────────────────┘
```

### ReAct Loop Pattern (How Each Agent Works)

Each agent inherits from `BaseAgent` and uses the **ReAct (Reasoning + Acting)** loop:

```
User Input / Orchestrator Call
        ↓
  LLM reads system prompt (agent personality)
        ↓
  LLM selects which tool to call
        ↓
  Tool executes (DB query + algorithm)
        ↓
  Tool result returned to LLM
        ↓
  LLM interprets result, decides next tool
        ↓
  [Repeat until enough information]
        ↓
  LLM generates final structured response
        ↓
  Response returned to caller
```

---

## 5. Database Schema

### Database File
- **Location:** `backend/amis.db`
- **Type:** SQLite
- **Size:** ~280 KB
- **Schema file:** `backend/schema.sql`

### All Tables

#### `products`
| Column | Type | Description |
|---|---|---|
| id | TEXT (PK) | e.g. PROD-A |
| name | TEXT | Industrial Valve Assembly - Type A |
| category | TEXT | Industrial Equipment |
| status | TEXT | active / inactive |
| created_at | TIMESTAMP | Creation datetime |

#### `inventory`
| Column | Type | Description |
|---|---|---|
| product_id | TEXT (PK) | References products.id |
| current_stock | INTEGER | Units on hand (1,850) |
| safety_stock | INTEGER | Minimum buffer (300) |
| reorder_point | INTEGER | Trigger level (961) |
| avg_daily_usage | REAL | Average daily consumption (142.0) |
| lead_time | INTEGER | Days to restock (5) |
| stockout_risk | REAL | Current risk score (0.15) |
| warehouse_location | TEXT | WH-MAIN |
| bin_location | TEXT | A-12-B |
| last_replenishment_date | DATE | 2026-01-31 |
| unit_cost | REAL | $52.00 |
| holding_cost | REAL | $2.30/unit/year |

#### `machines`
| Column | Type | Description |
|---|---|---|
| id | TEXT (PK) | MCH-001 to MCH-006 |
| name | TEXT | Machine name |
| type | TEXT | robotic_assembly, cnc_machining, etc. |
| line | TEXT | Line 1–5 or "All Lines" |
| status | TEXT | operational / down / maintenance |
| oee | REAL | Overall Equipment Effectiveness (0–1) |
| availability | REAL | Uptime ratio (0–1) |
| performance | REAL | Speed ratio (0–1) |
| quality | REAL | Quality ratio (0–1) |
| failure_risk | REAL | Current failure probability (0–1) |
| production_capacity | INTEGER | Units per day at 100% |
| current_utilization | REAL | Current utilization (0–1) |
| vibration_level | REAL | Sensor reading (mm/s²) |
| temperature | REAL | Operating temperature (°C) |
| power_consumption | REAL | kW |
| runtime_hours | REAL | Total hours run |
| cycle_count | INTEGER | Total cycles |
| last_maintenance | DATE | Last service date |
| next_maintenance | DATE | Next scheduled service |

**Current machine data:**
| ID | Name | Line | Status | Health | OEE | Failure Risk |
|---|---|---|---|---|---|---|
| MCH-001 | Assembly Robot | Line 1 | operational | 91 | 89.6% | 9% |
| MCH-002 | CNC Machining Center | Line 2 | operational | 42 | 63.4% | 58% |
| MCH-003 | Hydraulic Press | Line 3 | operational | 74 | 78.9% | 26% |
| MCH-004 | Conveyor & Material Handling | Line 4 | **DOWN** | 0 | 0% | 100% |
| MCH-005 | Welding Station | Line 5 | operational | 96 | 93.7% | 4% |
| MCH-006 | Quality Inspection System | All Lines | operational | 98 | 96.9% | 2% |

#### `production_lines`
| Column | Type | Description |
|---|---|---|
| id | TEXT (PK) | Line 1–5 |
| name | TEXT | Line name |
| bottleneck_machine_id | TEXT | References machines.id |
| capacity_per_hour | INTEGER | Units per hour |
| status | TEXT | operational / down |
| utilization | REAL | Current utilization |
| efficiency | REAL | Current efficiency |

#### `bom_items` (Bill of Materials)
| Column | Type | Description |
|---|---|---|
| id | TEXT (PK) | BOM-001 to BOM-006 |
| product_id | TEXT | PROD-A |
| component_id | TEXT | SH-100, VSA-200, etc. |
| component_name | TEXT | Steel Housing, etc. |
| quantity | INTEGER | Units per finished product (all = 1) |
| stock | INTEGER | Current component stock |
| supplier_id | TEXT | SUP-A or SUP-B |
| cost | REAL | Unit cost |

**PROD-A BOM (6 components):**
| Component ID | Name | Stock | Cost | Supplier |
|---|---|---|---|---|
| SH-100 | Steel Housing | 2,100 | $25.00 | SUP-A |
| VSA-200 | Valve Seat Assembly | 1,650 | $14.00 | SUP-B |
| AM-300 | Actuator Motor | 1,900 | $8.50 | SUP-A |
| SOR-400 | Seals & O-rings Kit | 3,200 | $2.50 | SUP-A |
| FS-500 | Fastener Set | 4,100 | $1.50 | SUP-A |
| IL-600 | Inspection Labels & Packaging | 5,000 | $0.50 | SUP-A |

#### `suppliers`
| Column | Type | Description |
|---|---|---|
| id | TEXT (PK) | SUP-A, SUP-B |
| name | TEXT | Supplier A, Supplier B |
| location | TEXT | USA - Regional |
| score | INTEGER | Composite score (0–100) |
| rating | TEXT | A, B+, etc. |
| on_time_delivery | REAL | Percentage (92.5, 85.0) |
| quality_score | REAL | (98.8, 97.9) |
| lead_time | INTEGER | Days (4, 7) |
| lead_time_variability | INTEGER | Std dev days (0.8, 1.5) |
| risk | TEXT | low / medium / high |
| moq | INTEGER | Min order qty (100, 200) |
| payment_terms | TEXT | NET-30, NET-45 |

#### `supplier_contracts`
| Column | Type | Description |
|---|---|---|
| id | TEXT (PK) | CTR-SUP-A-2026 |
| supplier_id | TEXT | SUP-A / SUP-B |
| start_date | DATE | 2026-01-01 |
| end_date | DATE | 2026-12-31 / 2026-06-30 |
| volume | INTEGER | Annual contracted volume |
| status | TEXT | active |

#### `supplier_risk`
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto |
| component_id | TEXT | SH-100, etc. |
| component_name | TEXT | Steel Housing, etc. |
| sourcing_type | TEXT | single_source / dual_source / multi_source |
| qualified_suppliers | INTEGER | Count of qualified suppliers |
| geographic_risk | TEXT | low / medium / high |
| lead_time_risk | TEXT | low / medium / high |
| risk_score | REAL | 0–100 |
| mitigation_strategy | TEXT | Action recommendation |

**Risk scores:**
| Component | Sourcing Type | Risk Score | Category |
|---|---|---|---|
| AM-300 | single_source | 72.0 | HIGH |
| SH-100 | single_source | 65.0 | HIGH |
| VSA-200 | dual_source | 35.0 | MEDIUM |
| SOR-400 | multi_source | 15.0 | LOW |
| FS-500 | multi_source | 10.0 | LOW |
| IL-600 | multi_source | 8.0 | LOW |

#### `purchase_orders`
| Column | Type | Description |
|---|---|---|
| po_id | TEXT (PK) | PO-2026-018 etc. |
| product_id | TEXT | PROD-A |
| supplier_id | TEXT | SUP-A / SUP-B |
| order_date | DATE | Order placement date |
| expected_delivery_date | DATE | Promised delivery |
| actual_delivery_date | DATE | Actual delivery (NULL if open) |
| quantity | INTEGER | Units ordered |
| unit_cost | REAL | Cost per unit |
| total_cost | REAL | Total order value |
| status | TEXT | open / in_transit / processing / delivered |
| notes | TEXT | Tracking notes |

#### `historical_demand_data`
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto |
| product_id | TEXT | PROD-A |
| week | TEXT | 2025-W50, 2026-W01, etc. |
| date | DATE | Week start date |
| demand_units | INTEGER | Units demanded |
| anomaly | BOOLEAN | Flagged anomaly |
| avg_price | REAL | Average selling price |
| promotions_active | BOOLEAN | Promotion running |
| competitor_price | REAL | Competitor price that week |

#### `demand_forecasts`
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto |
| product_id | TEXT | PROD-A |
| week | TEXT | Forecast week |
| optimistic | INTEGER | Optimistic scenario units |
| base | INTEGER | Base scenario units |
| pessimistic | INTEGER | Pessimistic scenario units |
| actual | INTEGER | Actual demand (filled in later) |
| created_at | TIMESTAMP | When forecast was created |

#### `market_context_data`
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto |
| season | TEXT | Q1 typically sees 15% higher demand |
| economic_indicator | TEXT | Manufacturing PMI at 52.3 (expansion) |
| industry_trend | TEXT | Growing at 7.2% YoY |
| raw_material_price_trend | TEXT | Cost trend description |
| competitor_activity | TEXT | Competitive landscape notes |
| upcoming_events | TEXT | Trade shows, contract renewals |
| market_sentiment | TEXT | Positive / Negative / Neutral |

#### `production_schedule`
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto |
| week_number | INTEGER | Week number |
| week_start_date | DATE | Week start |
| planned_production | INTEGER | Target units |
| actual_production | INTEGER | Actual units produced |
| capacity | INTEGER | Available capacity |
| overtime_hours | REAL | OT hours used |

#### `shift_config`
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto |
| shifts_per_day | INTEGER | 2 |
| hours_per_shift | REAL | 8.0 |
| days_per_week | INTEGER | 5 |
| overtime_available | BOOLEAN | true |
| max_overtime_hours | REAL | 4.0 hours/day |

#### `maintenance_history`
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto |
| machine_id | TEXT | References machines.id |
| date | DATE | Service date |
| type | TEXT | planned / unplanned |
| technician | TEXT | Technician name |
| duration_hours | REAL | Time taken |
| cost | REAL | Service cost |
| notes | TEXT | Work performed |

#### `machine_oee_history`
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto |
| machine_id | TEXT | References machines.id |
| date | TEXT | Period (YYYY-MM) |
| oee | REAL | OEE value |
| availability | REAL | Availability |
| performance | REAL | Performance |
| quality | REAL | Quality |

#### `sensor_readings`
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto |
| machine_id | TEXT | References machines.id |
| timestamp | TIMESTAMP | Reading time |
| vibration | REAL | mm/s² |
| temperature | REAL | °C |
| pressure | REAL | PSI |
| rpm | REAL | Rotations per minute |

#### `warehouse_zones`
| Column | Type | Description |
|---|---|---|
| zone_id | TEXT (PK) | A, B, C |
| zone_name | TEXT | Primary Storage, Fast-Pick, Overflow |
| capacity | INTEGER | Max units (2500, 1000, 1500) |
| current_units | INTEGER | Units stored now |
| zone_type | TEXT | bulk / pick_pack / overflow |
| cost_per_unit_per_day | REAL | Holding cost by zone |

#### `stockout_events`
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto |
| product_id | TEXT | PROD-A |
| event_date | DATE | When stockout occurred |
| duration_days | INTEGER | How long it lasted |
| units_short | INTEGER | Units unable to fulfill |
| root_cause | TEXT | Cause description |
| revenue_lost | REAL | Financial impact |
| customers_affected | INTEGER | Number of customers impacted |

**Historical stockout events:**
| Event | Date | Duration | Units Short | Revenue Lost | Root Cause |
|---|---|---|---|---|---|
| SO-001 | 2025-10-15 | 3 days | 420 | $37,590 | Supplier A delayed 4 days |
| SO-002 | 2025-08-22 | 1 day | 180 | $16,110 | Enterprise demand spike |
| SO-003 | 2025-06-03 | 5 days | 650 | $58,175 | Quality issue → batch recall |

#### `users`
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto |
| username | TEXT | Login name |
| email | TEXT | User email |
| role | TEXT | admin / manager / operator |
| hashed_password | TEXT | SHA-256 hash |
| created_at | TIMESTAMP | Account creation |

#### `activity_log`
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto |
| user | TEXT | Username |
| action | TEXT | What was done |
| resource | TEXT | What was affected |
| timestamp | TIMESTAMP | When |
| details | TEXT | Additional context |

#### Other Tables
- `machine_alarms` — Active equipment alerts
- `spare_parts` — Spare parts inventory per machine
- `work_orders` — Maintenance work orders
- `supplier_certifications` — ISO/quality certifications
- `supplier_incidents` — Past supplier failures or delays
- `product_machines` — Which machines produce which products

---

## 6. Backend & API

### FastAPI Server
- **File:** `backend/main.py`
- **Port:** 8000
- **CORS Origins:** `http://localhost:5173`, `http://localhost:3000`
- **Docs:** `http://localhost:8000/docs` (auto-generated Swagger UI)

### Authentication Endpoints
```
POST  /api/auth/login        → { username, password } → { access_token, token_type }
GET   /api/auth/me           → Current user info (requires Bearer token)
GET   /api/auth/health       → Auth system status
```

### Agent Execution Endpoints
```
POST  /api/agents/run                  → { agent_type, product_id, plant_id }
                                         agent_type: "demand"|"inventory"|"machine"|"production"|"supplier"
GET   /api/agents/runs/{run_id}        → Poll status: { status, result, steps }

POST  /api/pipeline/run                → { product_id, plant_id, planning_weeks }
GET   /api/pipeline/runs/{run_id}      → Poll full pipeline status
GET   /api/pipeline/runs?limit=10      → Recent pipeline runs list
```

### Product & Inventory Endpoints
```
GET   /api/products                    → All products list
GET   /api/products/{id}               → Product detail
GET   /api/products/{id}/inventory     → Inventory position
GET   /api/products/{id}/bom           → Bill of Materials

GET   /api/inventory/{id}/history      → 30-day stock history
POST  /api/inventory/{id}/adjust       → Adjust stock level (audit logged)
```

### Machine Endpoints
```
GET   /api/machines                    → All machines with current status
GET   /api/machines/{id}               → Machine detail + sensor data
GET   /api/machines/{id}/oee-history   → OEE trend (6 months)
POST  /api/work-orders                 → Create maintenance work order
```

### Production Endpoints
```
GET   /api/production/lines            → All production lines
GET   /api/production/schedule/{id}    → Production schedule for product
PUT   /api/production/schedule/{id}    → Update schedule
```

### Supplier Endpoints
```
GET   /api/suppliers                   → All suppliers with performance
GET   /api/suppliers/{id}              → Supplier detail + contracts
```

### Demand Endpoints
```
POST  /api/demand/forecast             → Create demand forecast (AI-generated or manual)
GET   /api/demand/forecast/{id}        → Get forecasts (12 weeks default)
PATCH /api/demand/actual/{id}/{week}   → Record actual demand
```

### Dashboard & Utility Endpoints
```
GET   /api/dashboard/summary           → System health score + KPIs
GET   /api/activity-log?limit=100      → Audit trail
GET   /api/database/stats              → DB table counts and sizes
POST  /api/chat                        → Natural language query
```

---

## 7. Authentication & Authorization

### Method: JWT (JSON Web Tokens)

**Algorithm:** HS256
**Token lifetime:** 480 minutes (8 hours)
**Secret Key:** `amis-secret-key-change-in-production-2026` (change in prod)

### Default Users

| Username | Password | Role | Access Level |
|---|---|---|---|
| admin | admin123 | admin | Full access, approve orders, manage users |
| manager | manager123 | manager | Operational access, limited approval |
| operator | operator123 | operator | Read/view only, no approvals |

### Login Flow

1. Frontend sends `POST /api/auth/login` with `{ username, password }`
2. Backend hashes password (SHA-256) and validates against DB
3. Returns `{ access_token: "eyJ...", token_type: "bearer" }`
4. Frontend stores token in `localStorage`
5. All API calls include header: `Authorization: Bearer {token}`
6. Backend validates token on every protected route

---

## 8. Agent System

### BaseAgent (`agents/base_agent.py`, 247 lines)

The foundation class all agents inherit from.

**Initialization:**
```python
class BaseAgent:
    def __init__(self, system_prompt: str, tools: list):
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-6",
            temperature=0.3,
            max_tokens=4096
        ).bind_tools(tools)
        self.system_prompt = system_prompt
        self.tools = {tool.name: tool for tool in tools}
        self.trace_log = []
```

**Main Loop (`run` method):**
```python
def run(self, user_input: str) -> str:
    messages = [SystemMessage(self.system_prompt), HumanMessage(user_input)]
    while True:
        response = self.llm.invoke(messages)
        if response.tool_calls:
            for tool_call in response.tool_calls:
                result = self.tools[tool_call["name"]].invoke(tool_call["args"])
                messages.append(ToolMessage(result, tool_call_id=tool_call["id"]))
        else:
            return response.content  # Final answer
```

---

### Demand Forecasting Agent (`agents/demand_agent.py`, 74 lines)

**Identity:** Senior demand planning expert, 12 years experience
**Tools:** 6 tools from `tools/forecasting.py`, `tools/simulation.py`, `tools/anomaly.py`
**Bridge Method:** `get_forecast_output(product_id, horizon_weeks)`

**Tools assigned:**
1. `get_demand_data_summary`
2. `simulate_demand_scenarios`
3. `analyze_demand_trends`
4. `monte_carlo_profit_simulation`
5. `compare_production_strategies`
6. `detect_demand_anomalies`

**Structured output for Orchestrator:**
```json
{
  "weekly_forecast": 1769,
  "trend_slope": 37.3,
  "anomaly_weeks": ["2026-W06"],
  "recommended_strategy": "balanced",
  "confidence_interval": [1621, 1917]
}
```

---

### Inventory Management Agent (`agents/inventory_agent.py`, 92 lines)

**Identity:** Inventory optimization specialist
**Tools:** 6 tools from `tools/inventory.py`
**Bridge Method:** `get_inventory_output(product_id, planning_weeks)`

**Tools assigned:**
1. `get_inventory_status`
2. `calculate_reorder_point`
3. `optimize_safety_stock`
4. `simulate_stockout_risk`
5. `evaluate_holding_costs`
6. `generate_replenishment_plan`

**Structured output for Orchestrator:**
```json
{
  "current_stock": 1850,
  "days_of_supply": 29.2,
  "reorder_point": 961,
  "optimal_safety_stock": 355,
  "stockout_risk_14d": 36.2,
  "replenishment_plan": {...}
}
```

---

### Machine Health Agent (`agents/machine_health_agent.py`, 69 lines)

**Identity:** Equipment reliability engineer, 15 years maintenance
**Tools:** 6 tools from `tools/machine_health.py`
**Bridge Method:** `get_capacity_output(plant_id)`

**Tools assigned:**
1. `get_machine_fleet_status`
2. `analyze_sensor_readings`
3. `predict_failure_risk`
4. `calculate_oee`
5. `generate_maintenance_schedule`
6. `assess_production_capacity_impact`

**Structured output for Orchestrator:**
```json
{
  "capacity_ceiling_per_day": 199,
  "capacity_ceiling_per_week": 1393,
  "machines_at_risk": ["MCH-004"],
  "lines_at_risk": ["Line 4"],
  "capacity_risk_flag": true,
  "maintenance_windows": [...]
}
```

---

### Production Planning Agent (`agents/production_agent.py`, 84 lines)

**Identity:** Senior production planner, 15 years MPS experience
**Tools:** 6 tools from `tools/production.py`
**Bridge Method:** `get_production_output(product_id, planning_weeks)`

**Tools assigned:**
1. `get_production_context`
2. `build_master_production_schedule`
3. `analyze_production_bottlenecks`
4. `evaluate_capacity_gap`
5. `optimize_production_mix`
6. `generate_production_requirements`

**Critical rule:** NEVER plan above Machine Health Agent's risk-adjusted capacity ceiling.

**Structured output for Orchestrator:**
```json
{
  "weekly_production_target": 980,
  "mps": { "week1": 945, "week2": 1050, "week3": 1050, "week4": 1050 },
  "total_planned_units": 4095,
  "attainment_pct": 97.5,
  "material_requirements": [...],
  "ot_contract_cost": 61297.60
}
```

---

### Supplier & Procurement Agent (`agents/supplier_agent.py`, 87 lines)

**Identity:** Supply chain strategist, 10 years procurement
**Tools:** 6 tools from `tools/supplier.py`
**Bridge Method:** `get_procurement_output(weekly_units, planning_weeks)`

**Tools assigned:**
1. `get_procurement_context`
2. `evaluate_supplier_options`
3. `generate_purchase_orders`
4. `assess_supply_chain_risk`
5. `simulate_delivery_risk`
6. `optimize_supplier_allocation`

**Structured output for Orchestrator:**
```json
{
  "pos_placed": 6,
  "total_po_value": 74206.55,
  "urgent_items": [],
  "delivery_eta_days": 4,
  "resilience_score": 66,
  "escalation_required": true,
  "escalation_reason": "2 high-risk components and 1 contract expiry"
}
```

---

### Orchestrator Agent (`agents/orchestrator_agent.py`, 106 lines)

**Identity:** Chief Manufacturing Intelligence Officer
**Bridge Method:** `run_full_pipeline(product_id, plant_id, planning_weeks)`

**Pipeline execution order (hardcoded):**
```python
# Step 1
demand_json    = get_demand_intelligence(product_id)
# Step 2
inventory_json = get_inventory_intelligence(product_id, planning_weeks)
# Step 3
machine_json   = get_machine_health_intelligence(plant_id)
# Step 4
production_json = get_production_intelligence(product_id, planning_weeks)
# Step 5 — extracts weekly_target from Step 4
weekly_target  = production["weekly_production_target"]
supplier_json  = get_supplier_intelligence(weekly_target, planning_weeks)
# Step 6
report_json    = synthesize_manufacturing_report(product_id, plant_id, planning_weeks)
```

**Final report includes:**
- System health score (0–100)
- Status: healthy / caution / critical / crisis
- Top 3 cross-domain risks
- Recommended immediate actions
- Full agent output bundle
- Execution audit trail

---

## 9. Tools — Algorithms & Calculations

### Demand Tools (`tools/forecasting.py`, 241 lines)

#### `get_demand_data_summary`
- **DB queries:** `historical_demand_data`, `inventory`, `market_context_data`, `production_lines`, `shift_config`
- **Returns:** 12 weeks history, inventory position, market signals, production capacity

#### `analyze_demand_trends`
- **Algorithm:** Linear regression on demand values
- **Formula:** `slope = (n·Σxy − Σx·Σy) / (n·Σx² − (Σx)²)`
- **Returns:** Trend slope, avg demand, std dev, seasonality, growth rate

#### `detect_demand_anomalies`
- **Algorithm:** Z-score detection
- **Formula:** `Z = (demand − mean) / std_dev`; flag if Z > 2.0
- **Returns:** Anomaly weeks, deviation %, root cause hypothesis

#### `simulate_demand_scenarios`
- **Scenarios:** Pessimistic (−17%), Base, Optimistic (+20%)
- **Probabilities:** 25% / 55% / 20%
- **Returns:** Weekly breakdown per scenario, 4-week totals

#### `monte_carlo_profit_simulation` (`tools/simulation.py`)
- **Runs:** 1,000 simulations
- **Variables:** demand uncertainty, price elasticity, cost variance
- **Returns:** Expected profit, P10/P50/P90, risk exposure

### Inventory Tools (`tools/inventory.py`, 629 lines)

#### `calculate_reorder_point`
- **Formula:**
  ```
  Safety Stock (SS) = Z × √(LT × σ²_demand + μ²_demand × σ²_LT)
  ROP = (avg_daily_demand × lead_time) + SS
  ```
- **Inputs from DB:** `inventory.avg_daily_usage=142`, `inventory.lead_time=5`, demand std=25, LT std=1
- **At 95% service level (Z=1.645):**
  ```
  SS  = 1.645 × √(5×625 + 142²×1²) = 1.645 × 152.6 = 251
  ROP = 142×5 + 251 = 710+251 = 961
  ```

#### `optimize_safety_stock`
- **Tests 7 service levels:** 85%, 90%, 92%, 95%, 97%, 98%, 99%
- **Total cost = annual_holding_cost + expected_annual_stockout_cost**
- **Optimal:** Lowest total cost (99% at $3,571/year given stockout history of $111,875)

#### `simulate_stockout_risk`
- **Monte Carlo:** 1,000 simulations over 14-day horizon
- **Each sim:** `stock[d] = stock[d-1] − gauss(142, 25)`
- **Result:** 36.2% stockout probability by day 14

#### `evaluate_holding_costs`
- **EOQ:** `√(2 × annual_demand × ordering_cost / holding_cost) = √(2×51830×75/2.3) ≈ 2600`
- **Daily cost:** `stock × holding_cost / 365 = 1850×2.3/365 = $11.66/day`

#### `generate_replenishment_plan`
- **Logic:** Projects inventory weekly, triggers order when end_stock near safety_stock
- **Supplier split:** 65% SUP-A (reliability), 35% SUP-B (cost)

### Machine Health Tools (`tools/machine_health.py`, 768 lines)

#### `predict_failure_risk`
- **Sensor degradation factor:**
  - Vibration WARNING → 45% MTBF reduction → factor = 0.55
  - Critical → 65% reduction
- **Effective MTBF:** `original_mtbf × sensor_factor = 180 × 0.55 = 99 days`
- **Failure probability (exponential distribution):**
  ```
  P(fail in t days) = 1 − e^(−t/MTBF_effective)
  P(fail in 7 days) = 1 − e^(−7/99) = 6.8%
  ```
- **Median time to failure:** `MTBF × ln(2) = 99 × 0.6931 = 68.6 days`

#### `calculate_oee`
- **Formula:** `OEE = Availability × Performance × Quality`
- **MCH-002:** `0.85 × 0.77 × 0.968 = 63.4%` (Poor — below 65% benchmark)
- **Units lost:** `max_output × (1 − OEE) = 60 × 0.366 = 22 units/day`

#### `assess_production_capacity_impact`
- **Per line:** `effective_output = max_output × efficiency_factor`
- **Total:** `53+45+45+0+56+0 = 199 units/day` (MCH-004 DOWN = 0)
- **Weekly:** `199 × 7 = 1,393 units/week` → production ceiling

### Production Tools (`tools/production.py`, 765 lines)

#### `build_master_production_schedule`
- **Week 1** (Line 4 DOWN + MCH-002 maintenance):
  ```
  base_capacity    = (13+0+11+0+13) × 5 = 185 units
  overtime         = 13 units/hr × 4 hrs/day × 5 days = 260 units
  contract_mfg     = 500 units (max per week)
  total_W1         = 185+260+500 = 945 units
  shortfall        = 1050−945 = 105 units
  ```
- **Weeks 2–4** (all lines back):
  ```
  base_capacity    = (13+15+11+10+13) × 5 = 310 units
  overtime         = 260 units
  contract_mfg     = 1050−310−260 = 480 units
  total            = 310+260+480 = 1050 units
  ```
- **Additional costs:**
  ```
  Overtime cost    = units × unit_cost × 0.35 premium = 260 × 52 × 0.35 = $4,732/week
  Contract cost    = units × unit_cost × 0.42 premium = 500 × 52 × 0.42 = $10,920 (W1)
  ```

#### `analyze_production_bottlenecks` (Theory of Constraints)
- **Primary bottleneck:** Machine/line with largest capacity loss
- **Weekly margin lost:** `capacity_lost × unit_margin = capacity_lost × (89.5−52.0) = × $37.50`
- Line 4: `60 × 37.5 = $2,250/week lost`

#### `generate_production_requirements` (BOM Explosion / MRP)
- **Formula:** `total_needed = weekly_units × planning_weeks × qty_per_unit`
- **Net to order:** `total_needed − current_stock`
- **Weeks of supply:** `current_stock / weekly_qty_needed`
- **Order deadline:** `weeks_of_supply − (lead_time_days / 7)`

### Supplier Tools (`tools/supplier.py`, 825 lines)

#### `generate_purchase_orders`
- **Total units:** `weekly_target × planning_weeks = 980 × 4 = 3,920`
- **Pipeline:** Uses dict comprehension → last PO's qty per component = 800
- **Net to order:** `max(0, total_needed − on_hand − pipeline) + 10% safety buffer`
- **Volume discounts:** ≥500 units → 2%, ≥1,000 units → 3.5%
- **Supplier selection (standard):** `score = cost × 0.60 + lead_time × 0.40`

#### `simulate_delivery_risk` (Monte Carlo)
- **1,000 simulations:**
  ```python
  actual_lt = max(1.0, gauss(avg_lt, lt_std))
  if random() > on_time_pct: actual_lt += uniform(1, 3)
  if actual_lt <= required_by: on_time++
  ```
- **SUP-A for SH-100:** 98.5% on-time, LOW risk

#### `optimize_supplier_allocation`
- **Tests 7 splits:** 100/0, 80/20, 70/30, 60/40, 50/50, 40/60, 30/70
- **Feasibility filter:** OTD ≥ 88% AND concentration ≤ 80%
- **Optimal:** Minimum cost among feasible splits
- **VSA-200 result:** 70% SUP-A / 30% SUP-B = $25,273 (OTD=90.2%, conc=70%)

#### `assess_supply_chain_risk`
- **Resilience score:** `round(100 − avg_risk_score) = round(100 − 34.17) = 66`
- **Ratings:** ≥75=STRONG, ≥55=MODERATE, <55=WEAK
- **Contract risk:** Flags contracts expiring within 180 days

---

## 10. System Prompts

All 6 agent prompts follow the same reasoning framework:

### 6-Step Reasoning Framework (in every prompt)

1. **PERCEIVE** — Gather full context before forming opinions. Never analyze in a vacuum.
2. **ANALYZE** — Call multiple tools. Let the data speak.
3. **INTERPRET** — Add intelligence. Don't just relay numbers — explain what they mean.
4. **REASON** — Evaluate trade-offs explicitly. Name the competing factors.
5. **RECOMMEND** — Give a clear, actionable recommendation with justification.
6. **EXPLAIN** — Show your work. Cite specific numbers from tool results.

### Agent Identities

| Agent | Identity | Domain Expertise |
|---|---|---|
| Demand | Senior demand planning expert, 12 years | Forecasting, trend analysis, market intelligence |
| Inventory | Inventory optimization specialist | Safety stock, EOQ, stockout prevention |
| Machine Health | Equipment reliability engineer, 15 years | OEE, predictive maintenance, MTBF |
| Production | Senior production planner, 15 years MPS | Master scheduling, capacity planning, BOM/MRP |
| Supplier | Supply chain strategist, 10 years | Procurement, dual-sourcing, risk mitigation |
| Orchestrator | Chief Manufacturing Intelligence Officer | Cross-domain synthesis, executive reporting |

### Critical Rules Embedded in Prompts

- **Production Agent:** "NEVER plan above Machine Health Agent's risk-adjusted capacity ceiling"
- **All Agents:** "Always call get_[context] first before making any recommendations"
- **Orchestrator:** "Identify risks that are invisible to individual agents — only visible at the intersection of domains"

---

## 11. Frontend / UI

### Technology
- **Framework:** React 18 with Vite
- **Port:** 5173 (dev)
- **Styling:** TailwindCSS (dark theme, sky-blue primary)
- **Charts:** Recharts (Line, Area, Bar, Pie)
- **Animations:** Framer Motion
- **Icons:** Lucide React
- **State:** React Query (server) + Zustand (client)

### Pages (10 Pages)

#### Login (`/login`)
- Username/password form
- JWT token received and stored in `localStorage`
- Redirects to Dashboard on success
- Shows error on invalid credentials

#### Dashboard — Command Center (`/`)
- **System Health Score** (0–100): Composite of machine health, inventory levels, production attainment
- **Status Badge:** Healthy / Caution / Critical / Crisis
- **KPI Cards:** Current stock, active machines, weekly production, supplier risk
- **Active Alerts:** Real-time alerts from machine_alarms and inventory tables
- **Recent Activity Feed:** Last 20 actions from activity_log
- **Auto-refresh:** Every 30 seconds
- **Quick Actions:** Run pipeline, view machines, check inventory

#### Pipeline Runner (`/pipeline`)
- **Trigger:** "Run Full Analysis" button
- **Progress Display:** Shows each of 6 steps executing in real-time
  - Step 1/6: Running Demand Forecasting Agent...
  - Step 2/6: Running Inventory Management Agent...
  - Step 3/6: Running Machine Health Agent...
  - Step 4/6: Running Production Planning Agent...
  - Step 5/6: Running Supplier & Procurement Agent...
  - Step 6/6: Synthesizing Manufacturing Intelligence Report...
- **Results Panel:** Expandable sections for each agent's output
- **Final Report:** System health score, top risks, recommended actions
- **Export:** Download results as JSON or CSV

#### Demand Intelligence (`/demand`)
- **Forecast Display:** 3-scenario chart (optimistic/base/pessimistic with confidence bands)
- **Historical Demand Chart:** 12-week trend with anomaly markers (spike in W06 highlighted)
- **Trend Analysis Panel:** Growth rate, slope, volatility
- **Market Context Cards:** PMI, industry trend, upcoming events, competitor activity
- **Manual Forecast Entry:** ForecastInputModal — enter custom scenarios
- **AI Forecast Import:** Trigger agent and import results
- **Accuracy Tracker:** Predicted vs. actual comparison
- **Product Selector:** Switch between products

#### Inventory Control (`/inventory`)
- **Stock Status Card:** Current stock (1,850), safety stock (300), days of supply (29.2)
- **Progress Bar:** Warehouse utilization (37% of 5,000 capacity)
- **Reorder Alert:** Shows if current stock is below ROP (961)
- **Incoming Pipeline:** 4 open POs totalling 2,300 units
- **30-Day History Chart:** Stock level trend
- **Warehouse Zones Table:** Zone A/B/C utilization and cost
- **BOM Component Status:** 6 components with weeks-of-supply
- **Adjustment Modal:** InventoryAdjustmentModal — record stock corrections with reason
- **Supplier Summary:** Lead times, on-time %, reject rates

#### Machine Health (`/machines`)
- **Fleet Overview Grid:** All 6 machines with status badges
  - Normal (green), Warning (yellow), Caution (orange), Critical/DOWN (red)
- **OEE Dashboard:** Availability, Performance, Quality gauges per machine
- **Fleet Health Avg:** 66.8/100
- **Capacity Summary:** 199 effective units/day vs. 268 theoretical max
- **Machine Detail Modal:** MachineDetailModal
  - Sensor readings (vibration, temperature, pressure, RPM)
  - 7-day trend charts per sensor
  - Failure risk prediction (probability, median days to failure)
  - Maintenance history
- **Maintenance Schedule:** 30-day maintenance calendar
- **Work Order Creation:** WorkOrderModal — request maintenance
- **Production Capacity Impact:** Line-by-line contribution table

#### Production Planning (`/production`)
- **MPS Table:** Week-by-week schedule for 4 weeks
  - Line contribution per week
  - OT and contract manufacturing units
  - Shortfall highlighting (Week 1 = 105 units short)
- **Capacity Gap Chart:** Target vs. available capacity
- **Bottleneck Ranking:** Lines sorted by capacity lost and margin lost
- **Overtime/Contract Cost Calculator:** Shows cost of supplemental capacity
- **Schedule Edit Modal:** ScheduleEditModal — adjust weekly targets
- **Scenario Comparison:** Pessimistic/Base/Optimistic expected profits
- **BOM Requirements:** Raw material needs per week

#### Supplier Management (`/suppliers`)
- **Supplier Scorecards:** SUP-A and SUP-B side-by-side
  - On-time delivery %, quality reject %, lead time, variability
  - Contract status and expiry warning
- **Risk Assessment Panel:**
  - Resilience score: 66/MODERATE
  - High-risk components: AM-300, SH-100
  - SUP-B contract expiry alert (101 days)
- **Open POs Table:** 4 active POs with status
- **Component Risk Matrix:** All 6 components with risk scores
- **Supplier Detail Modal:** SupplierDetailModal
  - Full performance history
  - Contract terms
  - Delivery simulation chart
- **Dual-Source Allocation:** VSA-200 70/30 split visualization
- **Purchase Order Generation:** Trigger PO run with custom parameters

#### Ask AMIS — Chat (`/chat`)
- **Natural Language Input:** Text box for any question
- **Agent Routing:** Backend routes to most relevant agent
- **Examples:**
  - "What is our stockout risk in the next 2 weeks?"
  - "Which machines are at risk of failure?"
  - "Should we activate overtime this week?"
  - "What raw materials do we need to order?"
- **Response Display:** Formatted agent response with numbers and recommendations
- **Conversation History:** Maintains session context across turns
- **Agent Indicator:** Shows which agent answered each response
- **Export Chat:** Download conversation as text

#### Crisis Negotiation (`/negotiation`)
- **Scenario Selector:**
  1. **Demand Spike** — Customer order exceeds current capacity
  2. **Supplier Failure** — Primary supplier (SUP-A) goes unavailable
  3. **Machine Breakdown** — Critical machine failure mid-week
  4. **Cost Pressure** — Management directive: reduce costs 10%
- **Multi-Round Negotiation:** Agents negotiate across domains
- **Resolution Display:** Final agreed compromise plan
- **Financial Impact:** Cost and revenue impact of each option

### UI Components (14 Reusable Components)

| Component | File | Purpose |
|---|---|---|
| Layout | `Layout.jsx` | App shell, sidebar, top nav, user menu |
| Card | `Card.jsx` | Consistent container with header/footer slots |
| Badge | `Badge.jsx` | Color-coded status: Normal/Warning/Caution/Critical/Down |
| Modal | `Modal.jsx` | Generic dialog with backdrop, close button, confirm/cancel |
| ForecastInputModal | `ForecastInputModal.jsx` | Form: week, optimistic, base, pessimistic values |
| InventoryAdjustmentModal | `InventoryAdjustmentModal.jsx` | Form: qty change, reason, date |
| MachineDetailModal | `MachineDetailModal.jsx` | Machine sensors, OEE, history, risk prediction |
| WorkOrderModal | `WorkOrderModal.jsx` | Form: machine, type, priority, description |
| ScheduleEditModal | `ScheduleEditModal.jsx` | Form: week, target qty, notes |
| SupplierDetailModal | `SupplierDetailModal.jsx` | Supplier full profile, contracts, delivery history |
| ProductSelector | `ProductSelector.jsx` | Dropdown: select active product (PROD-A, etc.) |
| DateRangePicker | `DateRangePicker.jsx` | Start/end date selection for history views |
| ActivityLog | `ActivityLog.jsx` | Scrollable feed of recent user actions |
| ExportButton | `ExportButton.jsx` | Dropdown: Export as CSV / JSON / Excel |

### API Client (`frontend/src/lib/api.js`)
All requests through Axios with:
- `baseURL: http://localhost:8000`
- Interceptor: Attaches `Authorization: Bearer {token}` to every request
- Error handling: 401 → redirect to login

---

## 12. Agent Pipeline — Execution Order & Data Flow

### Execution Order

```
1  →  Demand Forecasting Agent
2  →  Inventory Management Agent
3  →  Machine Health Agent
4  →  Production Planning Agent
5  →  Supplier & Procurement Agent
6  →  Orchestrator Agent (synthesis)
```

### What Each Agent Does & Passes Forward

```
┌─────────────────────────────────────────────────────────────┐
│  AGENT 1 — DEMAND FORECASTING                               │
│  Responsible for: Understanding what the market wants       │
│  Key tools: get_demand_data_summary, analyze_demand_trends  │
│             detect_demand_anomalies, simulate_scenarios      │
│                                                             │
│  Reads from DB:                                             │
│    - historical_demand_data (12 weeks)                      │
│    - market_context_data (PMI, trends, events)              │
│    - inventory (current position)                           │
│                                                             │
│  Key outputs:                                               │
│    forecast_weekly: 1,769 units/week                        │
│    trend_slope: +37.3 units/week                            │
│    anomaly: 2026-W06 (2,054 units, Z=2.68)                  │
│    market: Q1 surge, trade show in 11d                      │
│                                                             │
│  Passes to next: forecast demand for planning               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENT 2 — INVENTORY MANAGEMENT                             │
│  Responsible for: Ensuring stock never runs out or bloats   │
│  Key tools: calculate_reorder_point, simulate_stockout_risk │
│             optimize_safety_stock, generate_replenishment   │
│                                                             │
│  Reads from DB:                                             │
│    - inventory (stock=1850, safety=300, usage=142/day)      │
│    - purchase_orders (2300 units in pipeline)               │
│    - suppliers (lead times)                                 │
│    - stockout_events (3 events, $111,875 lost)              │
│                                                             │
│  Key outputs:                                               │
│    effective_dos: 29.2 days                                 │
│    reorder_point: 961 units                                 │
│    optimal_safety_stock: 355 units (99% service)            │
│    stockout_risk_14d: 36.2%                                 │
│    replenishment: order 1200u in W3, 2400u in W4            │
│                                                             │
│  Passes to next: inventory health, replenishment needs      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENT 3 — MACHINE HEALTH                                   │
│  Responsible for: Real production ceiling (not theoretical) │
│  Key tools: predict_failure_risk, calculate_oee             │
│             generate_maintenance_schedule                   │
│             assess_production_capacity_impact               │
│                                                             │
│  Reads from DB:                                             │
│    - machines (6 machines, MCH-004=DOWN, MCH-002=42 health) │
│    - sensor_readings (vibration MCH-002: +134% above base)  │
│    - maintenance_history                                    │
│    - machine_oee_history                                    │
│                                                             │
│  Key outputs:                                               │
│    capacity_ceiling: 199 units/day / 1,393/week             │
│    MCH-004: DOWN (100% fail risk)                           │
│    MCH-002: WARNING (6.8% fail in 7 days, OEE=63.4%)        │
│    maintenance: MCH-002 within 2d, MCH-003 within 7d        │
│    capacity_risk_flag: TRUE                                 │
│                                                             │
│  Passes to next: hard capacity ceiling + maintenance windows│
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENT 4 — PRODUCTION PLANNING                              │
│  Responsible for: Building the actual weekly plan (MPS)     │
│  Key tools: build_master_production_schedule                │
│             analyze_production_bottlenecks                  │
│             evaluate_capacity_gap                           │
│             generate_production_requirements (BOM/MRP)      │
│                                                             │
│  Reads from DB:                                             │
│    - production_lines (5 lines, Line 4=DOWN)                │
│    - shift_config (2 shifts × 8hrs, OT avail)               │
│    - bom_items (6 components per unit)                      │
│    - production_schedule (historical attainment 99.1%)      │
│                                                             │
│  Respects: capacity ceiling from Agent 3 (1,393/week)       │
│                                                             │
│  Key outputs:                                               │
│    W1: 945 units (Line 4+Line 2 both down, OT+contract)     │
│    W2-W4: 1,050 units each                                  │
│    weekly_target: 980 (passed to Agent 5)                   │
│    BOM alerts: VSA-200 runs out in 1.6 weeks                │
│    OT+contract cost: $61,297.60 over 4 weeks                │
│                                                             │
│  Passes to next: weekly_target=980, BOM requirements        │
└──────────────────────────┬──────────────────────────────────┘
                           │ weekly_target = 980
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENT 5 — SUPPLIER & PROCUREMENT                           │
│  Responsible for: Procuring all materials for the plan      │
│  Key tools: evaluate_supplier_options                       │
│             generate_purchase_orders                        │
│             assess_supply_chain_risk                        │
│             simulate_delivery_risk (Monte Carlo)            │
│             optimize_supplier_allocation                    │
│                                                             │
│  Reads from DB:                                             │
│    - suppliers (SUP-A: 92.5% OTD, 4d lead; SUP-B: 85%, 7d) │
│    - supplier_contracts (SUP-B expires in 101 days)         │
│    - supplier_risk (AM-300=72, SH-100=65 HIGH risk)         │
│    - purchase_orders (4 open POs in transit/processing)     │
│    - bom_items (component stocks)                           │
│                                                             │
│  Key outputs:                                               │
│    6 POs placed via SUP-A, total $74,206.55                 │
│    All delivery in 4 days                                   │
│    Resilience score: 66/MODERATE                            │
│    ESCALATION: 2 single-source + SUP-B expiry               │
│    VSA-200 optimal split: 70% SUP-A / 30% SUP-B             │
│                                                             │
│  Passes to next: PO summary + escalation flags              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENT 6 — ORCHESTRATOR (SYNTHESIS)                         │
│  Responsible for: Unified report + cross-domain risks       │
│                                                             │
│  Cross-domain insights (invisible to individual agents):    │
│    - Demand growing +37/week BUT capacity declining         │
│    - Week 1 shortfall of 105 units = $3,937 margin lost     │
│    - VSA-200 runs out in 1.6 weeks (7-day LT = order NOW)   │
│    - AM-300 single-source: zero backup if SUP-A disrupted   │
│    - MCH-002 vibration accelerating → failure before W2?    │
│                                                             │
│  Final report:                                              │
│    System Health Score: (calculated)                        │
│    Status: critical / caution / healthy                     │
│    Top 3 risks with financial impact                        │
│    Immediate action list                                    │
│    Full audit trail                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 13. Tool-by-Tool Input & Output — Demand Forecasting Agent

### TOOL 1: `get_demand_data_summary`
**Input:** `{ "product_id": "PROD-A" }`

**Key Output Fields:**
```json
{
  "historical_demand_last_12_weeks": [
    { "week": "2025-W50", "demand_units": 1360, "anomaly": false },
    { "week": "2026-W06", "demand_units": 2054, "anomaly": true },
    { "week": "2026-W09", "demand_units": 1736, "anomaly": false }
  ],
  "current_inventory": {
    "current_stock": 1850, "safety_stock": 300,
    "avg_daily_consumption": 142.0, "days_of_supply": 13.0
  },
  "market_context": {
    "season": "Q1 typically sees 15% higher demand",
    "economic_indicator": "Manufacturing PMI at 52.3 (expansion)",
    "upcoming_events": ["Industry trade show in 11 days", "Major client contract renewal in 4 days"]
  },
  "production_capacity": {
    "max_daily_output": 29, "current_utilization_pct": 83.0,
    "available_lines": ["Line 1","Line 2","Line 3","Line 5"],
    "lines_under_maintenance": ["Line 4"]
  }
}
```

### TOOL 2: `analyze_demand_trends`
**Input:** `{ "product_id": "PROD-A", "weeks_back": 12 }`

**Key Output Fields:**
```json
{
  "trend_analysis": {
    "avg_weekly_demand": 1573,
    "trend_direction": "upward",
    "weekly_growth_rate": 37.3,
    "demand_volatility_std": 176,
    "confidence_interval_95pct": { "lower": 1621, "upper": 1917 }
  },
  "forecast_next_4_weeks": [1769, 1806, 1843, 1880]
}
```
- **Avg demand (12 weeks):** `(1360+1469+1401+1421+1511+1572+1528+1535+2054+1605+1682+1736) / 12 = 1573` ✓
- **Trend slope:** Linear regression on 12 weekly values = **+37.3 units/week** ✓

### TOOL 3: `detect_demand_anomalies`
**Input:** `{ "product_id": "PROD-A" }`

**Key Output Fields:**
```json
{
  "anomalies_detected": [{
    "week": "2026-W06",
    "demand_units": 2054,
    "z_score": 2.68,
    "deviation_pct": 30.6,
    "flag": "DEMAND_SPIKE",
    "likely_causes": ["Promotion active", "Competitor price increase"]
  }],
  "clean_demand_avg": 1543
}
```
- **Z-score:** `(2054 − 1573) / 176 = 481/176 = 2.73` ≈ **2.68** ✓ (flagged > 2.0)

### TOOL 4: `simulate_demand_scenarios`
**Input:** `{ "product_id": "PROD-A", "horizon_weeks": 4 }`

**Key Output Fields:**
```json
{
  "scenarios": {
    "pessimistic": { "probability": 0.25, "weekly_demand": 875,  "4wk_total": 3500  },
    "base":        { "probability": 0.55, "weekly_demand": 1050, "4wk_total": 4200  },
    "optimistic":  { "probability": 0.20, "weekly_demand": 1260, "4wk_total": 5040  }
  },
  "expected_weekly_demand": 1050
}
```

### TOOL 5: `monte_carlo_profit_simulation`
**Input:** `{ "product_id": "PROD-A", "simulations": 1000 }`

**Key Output Fields:**
```json
{
  "expected_weekly_profit": 58705.5,
  "expected_4wk_profit": 234822.0,
  "risk_metrics": {
    "p10_profit": 49255.5,
    "p50_profit": 58705.5,
    "p90_profit": 78312.5
  }
}
```

### TOOL 6: `compare_production_strategies`
**Input:** `{ "product_id": "PROD-A" }`

**Key Output Fields:**
```json
{
  "strategies": {
    "conservative": { "weekly_units": 875,  "fill_rate": 83.3%, "risk": "low"    },
    "balanced":     { "weekly_units": 1050, "fill_rate": 94.8%, "risk": "medium" },
    "aggressive":   { "weekly_units": 1260, "fill_rate": 79.0%, "risk": "high"   }
  },
  "recommended": "balanced"
}
```

---

## 14. Tool-by-Tool Input & Output — Inventory Management Agent

### TOOL 1: `get_inventory_status`
**Input:** `{ "product_id": "PROD-A" }`

**Key Output Fields:**
```json
{
  "current_inventory": {
    "current_stock": 1850, "safety_stock": 300,
    "days_of_supply": 13.0, "incoming_pipeline_units": 2300
  },
  "health_indicators": {
    "effective_days_of_supply": 29.2,
    "buffer_above_safety": 1550,
    "stockout_events_last_12_months": 3,
    "total_stockout_revenue_lost": 111875.0
  },
  "warehouse_details": {
    "zones": [
      { "zone_id": "A", "capacity": 2500, "current_units": 1200, "utilization_pct": 48.0 },
      { "zone_id": "B", "capacity": 1000, "current_units": 450,  "utilization_pct": 45.0 },
      { "zone_id": "C", "capacity": 1500, "current_units": 200,  "utilization_pct": 13.3 }
    ]
  }
}
```
- **Effective DOS:** `(1850 + 2300) / 142 = 4150/142 = 29.2 days` ✓

### TOOL 2: `calculate_reorder_point`
**Input:** `{ "product_id": "PROD-A", "service_level": 0.95 }`

**Key Output Fields:**
```json
{
  "reorder_point_units": 961,
  "safety_stock_calculated": 251,
  "avg_demand_during_lead_time": 710,
  "days_until_rop_reached": 6.3,
  "effective_position": 4150,
  "calculation_inputs": {
    "daily_demand": 142.0, "demand_std_dev": 25.0,
    "lead_time": 5.0, "lead_time_std_dev": 1.0, "z_score": 1.645
  }
}
```
- `SS = 1.645 × √(5×625 + 20164) = 1.645 × 152.6 = 251` ✓
- `ROP = 142×5 + 251 = 961` ✓

### TOOL 3: `optimize_safety_stock`
**Input:** `{ "product_id": "PROD-A", "target_service_level": 0.95 }`

**Key Output Fields:**
```json
{
  "optimal_safety_stock": 355,
  "optimal_service_level_pct": 99.0,
  "analysis_by_service_level": [
    { "service_level_pct": 95.0, "z_score": 1.645, "safety_stock_units": 251, "total_annual_cost": 14350.08 },
    { "service_level_pct": 99.0, "z_score": 2.326, "safety_stock_units": 355, "total_annual_cost": 3571.06  }
  ]
}
```
- **Why 99% optimal:** Historical stockouts = $111,875/year. Cost of 99% SS = only $3,571 total.

### TOOL 4: `simulate_stockout_risk`
**Input:** `{ "product_id": "PROD-A", "simulations": 1000 }`

**Key Output Fields:**
```json
{
  "overall_stockout_probability_pct": 36.2,
  "daily_risk_profile": [
    { "day": 11, "stockout_probability_pct": 0.0  },
    { "day": 12, "stockout_probability_pct": 1.9  },
    { "day": 13, "stockout_probability_pct": 20.0 },
    { "day": 14, "stockout_probability_pct": 36.2 }
  ],
  "worst_case_scenario": { "min_stock_reached": -409, "day_of_min_stock": 14 }
}
```

### TOOL 5: `evaluate_holding_costs`
**Input:** `{ "product_id": "PROD-A" }`

**Key Output Fields:**
```json
{
  "current_position": {
    "daily_holding_cost": 11.66, "annual_holding_cost": 4255.0, "capital_tied_up": 96200.0
  },
  "eoq_analysis": {
    "economic_order_quantity": 2600,
    "optimal_reorder_frequency_days": 18.3
  }
}
```
- `EOQ = √(2×51830×75/2.3) ≈ 2600` ✓
- `Capital tied up = 1850 × $52.0 = $96,200` ✓

### TOOL 6: `generate_replenishment_plan`
**Input:** `{ "product_id": "PROD-A", "forecast_demand_weekly": 1769 }`

**Key Output Fields:**
```json
{
  "weekly_plan": [
    { "week": 1, "starting_stock": 1850, "incoming_pipeline": 2300, "ending_stock": 3112, "order_placed": false },
    { "week": 3, "starting_stock": 2084, "ending_stock": 1071, "order_placed": true,
      "order_details": { "total_qty": 1200, "total_cost": 61400.0, "expected_arrival": "Week 4" }
    }
  ],
  "plan_summary": { "total_units_ordered": 3600, "total_cost": 184200.0, "weeks_below_safety": 0 }
}
```

---

## 15. Tool-by-Tool Input & Output — Machine Health Agent

### TOOL 1: `get_machine_fleet_status`
**Input:** `{ "plant_id": "PLANT-01" }`

**Key Output Fields:**
```json
{
  "fleet_summary": {
    "total_machines": 6, "operational": 5, "down": 1,
    "on_warning": 1, "on_caution": 1, "fleet_health_avg_score": 66.8
  },
  "production_capacity": {
    "theoretical_max_units_per_day": 268,
    "effective_capacity_after_degradation_units_per_day": 203,
    "total_capacity_loss_pct": 24.3
  },
  "active_alerts": [
    { "severity": "CRITICAL", "machine_id": "MCH-004", "message": "Machine is down" },
    { "severity": "WARNING",  "machine_id": "MCH-002", "message": "Health score 42/100 — sensor anomalies" }
  ]
}
```
- **Fleet health avg:** `(91+42+74+0+96+98)/6 = 66.8` ✓

### TOOL 2: `analyze_sensor_readings`
**Input:** `{ "machine_id": "MCH-002", "hours_back": 24 }`

**Key Output Fields:**
```json
{
  "sensor_analysis": [
    { "sensor": "vibration", "baseline": 1.8, "current": 4.22, "deviation_pct": 134.4,
      "status": "warning", "trend_direction": "rising",
      "7_day_values": [2.00, 2.37, 2.74, 3.11, 3.48, 3.85, 4.22] },
    { "sensor": "temperature", "baseline": 72.0, "current": 80.8, "deviation_pct": 12.2,
      "status": "normal", "trend_direction": "rising" }
  ],
  "overall_sensor_status": "warning"
}
```
- **Vibration deviation:** `(4.22−1.8)/1.8 × 100 = 134.4%` ✓

### TOOL 3: `predict_failure_risk`
**Input:** `{ "machine_id": "MCH-002", "horizon_days": 7 }`

**Key Output Fields:**
```json
{
  "failure_prediction": {
    "failure_probability_pct": 6.8,
    "effective_mtbf_days": 99.0,
    "original_mtbf_days": 180,
    "sensor_degradation_factor": 0.55,
    "expected_median_days_to_failure": 68.6
  },
  "financial_impact": {
    "planned_maintenance_cost": 1200,
    "unplanned_failure_total_cost": 14550,
    "cost_of_inaction": 13350
  }
}
```
- `Effective MTBF = 180 × 0.55 = 99 days` ✓
- `P(fail in 7d) = 1 − e^(−7/99) = 6.8%` ✓
- `Median TF = 99 × ln(2) = 68.6 days` ✓

### TOOL 4: `calculate_oee`
**Input:** `{ "machine_id": "MCH-002", "period_months": 1 }`

**Key Output Fields:**
```json
{
  "oee_current": {
    "oee_pct": 63.4, "availability_pct": 85.0,
    "performance_pct": 77.0, "quality_pct": 96.8,
    "benchmark_classification": "Poor (<65%) — significant improvement opportunity"
  },
  "production_impact": {
    "max_possible_units_per_day": 60,
    "actual_units_per_day_at_current_oee": 38,
    "units_lost_per_day_to_oee": 22,
    "units_lost_per_week": 154
  }
}
```
- `OEE = 0.85 × 0.77 × 0.968 = 63.4%` ✓

### TOOL 5: `generate_maintenance_schedule`
**Input:** `{ "planning_horizon_days": 30, "prioritize_critical": true }`

**Key Output Fields:**
```json
{
  "maintenance_schedule": [
    { "machine_id": "MCH-004", "action": "CORRECTIVE MAINTENANCE IN PROGRESS", "urgency": "immediate" },
    { "machine_id": "MCH-002", "action": "SCHEDULE PREVENTIVE MAINTENANCE",    "urgency": "high",
      "recommended_window": "Within 2 days",
      "financial_case": { "planned_cost": 1200, "expected_inaction_cost": 1280, "net_savings": 80 }
    },
    { "machine_id": "MCH-003", "action": "SCHEDULE PREVENTIVE MAINTENANCE",    "urgency": "medium",
      "recommended_window": "Within 7 days" }
  ],
  "cross_agent_alert_for_production": {
    "windows": [
      { "machine_id": "MCH-004", "window": "Ongoing — est. return TBD",  "duration_days": 1.5 },
      { "machine_id": "MCH-002", "window": "Within 2 days (by Day 2)",   "duration_days": 0.9 },
      { "machine_id": "MCH-003", "window": "Within 7 days (by Day 7)",   "duration_days": 0.9 }
    ]
  }
}
```

### TOOL 6: `assess_production_capacity_impact`
**Input:** `{ "include_risk_buffer": true }`

**Key Output Fields:**
```json
{
  "capacity_assessment": {
    "theoretical_max_units_per_day": 268,
    "effective_capacity_units_per_day": 199,
    "effective_capacity_units_per_week": 1393
  },
  "line_by_line_detail": [
    { "machine_id": "MCH-001", "max_output_per_day": 55, "effective_output_per_day": 53, "efficiency_factor_pct": 97.0 },
    { "machine_id": "MCH-002", "max_output_per_day": 60, "effective_output_per_day": 45, "efficiency_factor_pct": 75.0 },
    { "machine_id": "MCH-003", "max_output_per_day": 50, "effective_output_per_day": 45, "efficiency_factor_pct": 90.0 },
    { "machine_id": "MCH-004", "max_output_per_day": 45, "effective_output_per_day": 0,  "efficiency_factor_pct": 0.0  },
    { "machine_id": "MCH-005", "max_output_per_day": 58, "effective_output_per_day": 56, "efficiency_factor_pct": 97.0 }
  ],
  "cross_agent_output_for_production_planning": {
    "recommended_production_ceiling_units_per_week": 1393,
    "capacity_risk_flag": true,
    "alert": "CAPACITY RISK: Do NOT commit to targets above the risk-adjusted ceiling."
  }
}
```
- `Total effective: 53+45+45+0+56 = 199 units/day` ✓
- `Weekly: 199 × 7 = 1,393 units` ✓

---

## 16. Tool-by-Tool Input & Output — Production Planning Agent

### TOOL 1: `get_production_context`
**Input:** `{ "product_id": "PROD-A" }`

**Key Output Fields:**
```json
{
  "capacity_summary": {
    "theoretical_max_units_per_week": 340,
    "current_effective_units_per_week": 235,
    "capacity_loss_pct": 30.9,
    "active_lines": 4, "down_lines": 1
  },
  "shift_config": {
    "overtime": { "available": true, "max_overtime_hours_per_day": 4.0, "cost_premium_pct": 35, "additional_units_per_overtime_hour": 13 },
    "contract_manufacturing": { "available": true, "cost_premium_pct": 42, "max_capacity_units_per_week": 500 },
    "current_base_capacity": { "effective_units_per_week": 980 }
  },
  "production_history_summary": {
    "avg_attainment_pct": 99.1,
    "recent_shortfalls": [{ "week": "2025-W49", "actual": 972, "planned": 1050 }]
  }
}
```

### TOOL 2: `build_master_production_schedule`
**Input:** `{ "planning_weeks": 4, "target_weekly_output": 1050.0, "line4_returns_week": 1, "mch002_maintenance_week": 1 }`

**Key Output Fields:**
```json
{
  "master_production_schedule": {
    "schedule": [
      { "week": 1, "base_capacity": 185, "overtime_units": 260, "contract_manufacturing_units": 500,
        "total_planned_output": 945, "shortfall_units": 105, "demand_met_pct": 90.0,
        "additional_cost": 15652.0, "overtime_cost": 4732.0, "contract_cost": 10920.0 },
      { "week": 2, "base_capacity": 310, "overtime_units": 260, "contract_manufacturing_units": 480,
        "total_planned_output": 1050, "shortfall_units": 0, "demand_met_pct": 100 },
      { "week": 3, "total_planned_output": 1050, "shortfall_units": 0 },
      { "week": 4, "total_planned_output": 1050, "shortfall_units": 0 }
    ]
  },
  "mps_summary": {
    "total_planned_units": 4095, "overall_attainment_pct": 97.5,
    "total_overtime_and_contract_cost": 61297.6
  }
}
```
- **W1:** `185 + 260 + 500 = 945` ✓, shortfall `1050−945 = 105` ✓
- **OT cost W1:** `260 × 52.0 × 0.35 = $4,732` ✓
- **Contract cost W1:** `500 × 52.0 × 0.42 = $10,920` ✓

### TOOL 3: `analyze_production_bottlenecks`
**Input:** `{}`

**Key Output Fields:**
```json
{
  "bottleneck_analysis": {
    "primary_bottleneck": { "line_id": "Line 4", "weekly_margin_lost": 2250.0 },
    "system_efficiency_pct": 69.1,
    "total_capacity_lost_per_week": 105,
    "total_weekly_margin_lost": 3937.5
  },
  "line_by_line_ranking": [
    { "line_id": "Line 4", "capacity_lost_per_week": 60, "weekly_margin_lost": 2250.0 },
    { "line_id": "Line 2", "capacity_lost_per_week": 20, "weekly_margin_lost": 750.0  },
    { "line_id": "Line 1", "capacity_lost_per_week": 10, "weekly_margin_lost": 375.0  },
    { "line_id": "Line 3", "capacity_lost_per_week": 10, "weekly_margin_lost": 375.0  },
    { "line_id": "Line 5", "capacity_lost_per_week": 5,  "weekly_margin_lost": 187.5  }
  ]
}
```
- `Unit margin = $89.5 − $52.0 = $37.50`
- `Line 4 margin lost = 60 × 37.5 = $2,250/week` ✓

### TOOL 4: `evaluate_capacity_gap`
**Input:** `{ "target_weekly_output": 1050, "current_capacity": 980 }`

**Key Output Fields:**
```json
{
  "gap_assessment": {
    "available_base_capacity_weekly": 235,
    "weekly_gap_units": 815,
    "gap_as_pct_of_demand": 77.6
  },
  "options": {
    "option_1_overtime":             { "units_available_per_week": 260, "additional_cost_per_week": 4732.0,  "closes_gap_pct": 31.9 },
    "option_2_contract_manufacturing":{ "units_available_per_week": 500, "additional_cost_per_week": 10920.0, "closes_gap_pct": 93.3 },
    "option_3_partial_fulfillment":  { "unmet_demand_units_per_week": 55, "total_revenue_at_risk_per_week": 5012.0 }
  },
  "recommended_action_cost_per_week": 15652.0
}
```

### TOOL 5: `optimize_production_mix`
**Input:** `{ "product_id": "PROD-A" }`

**Key Output Fields:**
```json
{
  "selected_scenario": "base",
  "scenario_analysis": [
    { "scenario": "pessimistic", "probability": 0.25, "weekly_demand": 875,  "net_profit": 53061.3,  "horizon_profit": 212245.2 },
    { "scenario": "base",        "probability": 0.55, "weekly_demand": 1050, "net_profit": 58705.5,  "horizon_profit": 234822.0 },
    { "scenario": "optimistic",  "probability": 0.20, "weekly_demand": 1260, "net_profit": 49255.5,  "horizon_profit": 197022.0 }
  ],
  "expected_value_analysis": { "expected_horizon_profit": 221617.8 },
  "recommended_production_target": { "weekly_units": 995, "demand_fill_rate_pct": 94.8 }
}
```
- **Expected value:** `0.25×212245 + 0.55×234822 + 0.20×197022 = $221,618` ✓

### TOOL 6: `generate_production_requirements`
**Input:** `{ "weekly_units_to_produce": 1050, "planning_weeks": 4 }`

**Key Output Fields:**
```json
{
  "production_plan": { "weekly_units": 1050, "planning_weeks": 4, "total_units": 4200 },
  "material_requirements": [
    { "component_id": "SH-100",  "total_qty_needed": 4200, "current_stock": 2100, "weeks_of_supply": 2.0, "net_qty_to_order": 2100, "alert": "STOCK RUNS OUT in 2.0 weeks — order within 1.4 weeks" },
    { "component_id": "VSA-200", "total_qty_needed": 4200, "current_stock": 1650, "weeks_of_supply": 1.6, "net_qty_to_order": 2550, "alert": "STOCK RUNS OUT in 1.6 weeks — order within 1 weeks" },
    { "component_id": "AM-300",  "total_qty_needed": 4200, "current_stock": 1900, "weeks_of_supply": 1.8, "net_qty_to_order": 2300, "alert": "STOCK RUNS OUT in 1.8 weeks — order within 1.2 weeks" },
    { "component_id": "SOR-400", "total_qty_needed": 4200, "current_stock": 3200, "weeks_of_supply": 3.0, "net_qty_to_order": 1000, "alert": "STOCK RUNS OUT in 3.0 weeks — order within 2.4 weeks" },
    { "component_id": "FS-500",  "total_qty_needed": 4200, "current_stock": 4100, "weeks_of_supply": 3.9, "net_qty_to_order": 100  },
    { "component_id": "IL-600",  "total_qty_needed": 4200, "current_stock": 5000, "weeks_of_supply": 4.8, "net_qty_to_order": 0    }
  ],
  "procurement_summary": { "total_material_cost_to_order": 110400.0, "components_needing_order": 5 }
}
```
- `VSA-200: 4200−1650 = 2550 to order; 1650/1050 = 1.57 weeks supply` ✓
- **Most urgent:** VSA-200 (1.6 weeks supply, 7-day lead time = order within 1 week)

---

## 17. Tool-by-Tool Input & Output — Supplier Agent

### TOOL 1: `get_procurement_context`
**Input:** `{ "product_id": "PROD-A" }`

**Key Output Fields:**
```json
{
  "component_status": [
    { "component_id": "SH-100",  "current_stock": 2100, "open_po_qty": 2300, "effective_stock": 4400, "weeks_of_supply_effective": 4.49 },
    { "component_id": "VSA-200", "current_stock": 1650, "open_po_qty": 2300, "effective_stock": 3950, "weeks_of_supply_effective": 4.03 }
  ],
  "supplier_summary": [
    { "supplier_id": "SUP-A", "on_time_delivery_pct": 92.5, "avg_lead_time_days": 4.0, "contract_expiry": "2026-12-31", "preferred": true  },
    { "supplier_id": "SUP-B", "on_time_delivery_pct": 85.0, "avg_lead_time_days": 7.0, "contract_expiry": "2026-06-30", "preferred": false }
  ],
  "procurement_health": {
    "components_below_reorder": 0, "components_with_open_po": 6
  }
}
```
- **weeks_of_supply effective:** `effective_stock / 980 = 4400/980 = 4.49` ✓

### TOOL 2: `evaluate_supplier_options`
**Input:** `{ "component_id": "SH-100", "quantity_needed": 1412, "required_by_days": 7 }`

**Key Output Fields:**
```json
{
  "risk_flag": "SINGLE SOURCE - Steel Housing",
  "supplier_options": [{
    "supplier_id": "SUP-A",
    "unit_cost_base": 25.0, "volume_discount_pct": 3.5,
    "unit_cost_discounted": 24.125, "total_order_cost": 34064.5,
    "savings_vs_list": 1235.5,
    "feasible_for_required_date": true,
    "on_time_probability_pct": 92.5,
    "composite_score": 5.4
  }],
  "recommended_supplier": "SUP-A"
}
```
- `Discounted cost = 25.0 × (1−0.035) = $24.125` ✓
- `Total = 24.125 × 1412 = $34,064.50` ✓

### TOOL 3: `generate_purchase_orders`
**Input:** `{ "weekly_production_target": 980, "planning_weeks": 4, "urgency_override": "standard" }`

**Key Output Fields:**
```json
{
  "purchase_order_run": { "total_units_to_produce": 3920, "urgency_mode": "standard" },
  "purchase_orders": [
    { "component_id": "SH-100",  "quantity_to_order": 1412, "unit_cost": 24.125, "total_cost": 34064.50, "lead_time_days": 4.0, "urgency": "STANDARD" },
    { "component_id": "VSA-200", "quantity_to_order": 1862, "unit_cost": 13.51,  "total_cost": 25155.62, "lead_time_days": 4.0, "urgency": "STANDARD" },
    { "component_id": "AM-300",  "quantity_to_order": 1612, "unit_cost": 8.2025, "total_cost": 13222.43, "lead_time_days": 4.0, "urgency": "STANDARD" },
    { "component_id": "SOR-400", "quantity_to_order": 392,  "unit_cost": 2.5,    "total_cost": 980.00,   "lead_time_days": 4.0, "urgency": "STANDARD" },
    { "component_id": "FS-500",  "quantity_to_order": 392,  "unit_cost": 1.5,    "total_cost": 588.00,   "lead_time_days": 4.0, "urgency": "STANDARD" },
    { "component_id": "IL-600",  "quantity_to_order": 392,  "unit_cost": 0.5,    "total_cost": 196.00,   "lead_time_days": 4.0, "urgency": "STANDARD" }
  ],
  "po_summary": { "total_pos_to_place": 6, "total_procurement_value": 74206.55, "urgent_pos": 0 }
}
```
- `SH-100: max(0, 3920−2100−800)+392 = 1020+392 = 1412` ✓
- `Total = 34064.50+25155.62+13222.43+980+588+196 = $74,206.55` ✓

### TOOL 4: `assess_supply_chain_risk`
**Input:** `{}`

**Key Output Fields:**
```json
{
  "supply_chain_risk_assessment": {
    "overall_resilience_score": 66, "resilience_rating": "MODERATE",
    "high_risk_components": 2, "single_source_components": 2
  },
  "high_risk_components": [
    { "component_id": "AM-300", "risk_score": 72.0, "risk_flag": "SINGLE SOURCE - Actuator Motor", "weeks_to_qualify_alternative": 12 },
    { "component_id": "SH-100", "risk_score": 65.0, "risk_flag": "SINGLE SOURCE - Steel Housing",  "weeks_to_qualify_alternative": 12 }
  ],
  "contract_risks": [
    { "supplier_id": "SUP-B", "expiry_date": "2026-06-30", "days_until_expiry": 101, "severity": "MEDIUM" }
  ],
  "escalation_to_orchestrator": { "requires_escalation": true, "reason": "2 high-risk components and 1 contract expiry warnings" }
}
```
- `Resilience = round(100 − (72+65+35+15+10+8)/6) = round(100−34.17) = 66` ✓

### TOOL 5: `simulate_delivery_risk`
**Input:** `{ "component_id": "SH-100", "supplier_id": "SUP-A", "order_quantity": 1412, "required_by_days": 7, "simulations": 1000 }`

**Key Output Fields:**
```json
{
  "delivery_risk": {
    "on_time_probability_pct": 98.5, "late_probability_pct": 1.5,
    "risk_level": "LOW"
  },
  "lead_time_distribution": {
    "avg_lead_time_days": 4.0, "p50_lead_time_days": 4.0,
    "p90_lead_time_days": 5.1, "p95_lead_time_days": 5.3
  },
  "late_delivery_impact": { "avg_delay_if_late_days": 0.5, "expected_stockout_cost": 47.25 },
  "recommendation": "Standard order — low risk, proceed"
}
```

### TOOL 6: `optimize_supplier_allocation`
**Input:** `{ "component_id": "VSA-200", "total_qty_needed": 1862, "planning_weeks": 4 }`

**Key Output Fields:**
```json
{
  "allocation_analysis": [
    { "split": "100/0", "total_cost": 25155.62, "weighted_on_time_pct": 92.5, "concentration_risk_pct": 100.0 },
    { "split": "70/30", "total_cost": 25273.01, "weighted_on_time_pct": 90.2, "concentration_risk_pct": 70.0  },
    { "split": "50/50", "total_cost": 25546.64, "weighted_on_time_pct": 88.8, "concentration_risk_pct": 50.0  }
  ],
  "recommended_allocation": {
    "split": "70/30", "qty_supplier_a": 1303, "qty_supplier_b": 559,
    "total_cost": 25273.01, "weighted_on_time_pct": 90.2,
    "savings_vs_single_source": -117.39
  },
  "recommendation_reason": "Split 70/30 minimizes cost while maintaining 90.2% OTD and limiting concentration to 70%"
}
```
- **Why not 100% SUP-A:** Concentration risk = 100% (zero resilience if SUP-A disrupted)
- **70/30 tradeoff:** Pays $117 more but reduces single-point-of-failure risk

---

## 18. Cross-Agent Data Flow

### What Each Agent Passes to the Next

| From | To | Data Passed |
|---|---|---|
| Demand Agent | Inventory Agent | Weekly forecast = 1,769 units, trend = +37.3/week |
| Inventory Agent | Production Agent | Current stock = 1,850, replenishment plan, stockout risk 36.2% |
| Machine Health Agent | Production Agent | **Hard ceiling = 1,393 units/week**, maintenance windows for MCH-002 and MCH-004 |
| Production Agent | Supplier Agent | **weekly_target = 980**, BOM requirements (5 components need ordering), VSA-200 most urgent |
| Supplier Agent | Orchestrator | POs placed = 6, total value = $74,206.55, escalation = true (2 high-risk + SUP-B expiry) |
| All Agents | Orchestrator | Full output JSON bundle for synthesis |

### Cross-Domain Risks (Only Visible to Orchestrator)

| Risk | Agents Involved | Impact |
|---|---|---|
| Demand growing (+37/wk) but capacity declining | Demand + Machine Health | Gap widens each week |
| VSA-200 runs out in 1.6 weeks with 7-day lead time | Production + Supplier | Production halts Week 2 if not ordered immediately |
| AM-300 = only 1 supplier, 12 weeks to qualify alternative | Production + Supplier | Factory-stopping risk if SUP-A disrupted |
| MCH-002 vibration accelerating — may fail before Week 2 | Machine Health + Production | W2 plan assumes MCH-002 returns, but failure risk = 6.8% |
| SUP-B contract expires in 101 days | Supplier + Production | Loses dual-source for VSA-200 if not renewed |

---

## 19. Configuration & Environment

### `config.py`
```python
MODEL_NAME    = "claude-sonnet-4-6"
TEMPERATURE   = 0.3
MAX_TOKENS    = 4096
VERBOSE       = True
DATABASE_PATH = "backend/amis.db"
```

### `.env` / `.env.example`
```bash
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite:///backend/amis.db
SECRET_KEY=amis-secret-key-change-in-production-2026
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

### `frontend/vite.config.js`
```javascript
server: {
  proxy: {
    '/api': { target: 'http://localhost:8000', changeOrigin: true }
  }
}
```

---

## 20. Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+
- Anthropic API Key (from console.anthropic.com)

### Step 1 — Clone & Configure
```bash
cd amis_phase_final
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Step 2 — Backend Setup
```bash
cd backend
pip install -r requirements.txt
python init_database.py        # Create tables
python init_users.py           # Create default users
python populate_full_database.py  # Load sample data
```

### Step 3 — Frontend Setup
```bash
cd frontend
npm install
```

### Step 4 — Run
```bash
# Terminal 1 (Backend)
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 (Frontend)
cd frontend
npm run dev
```

### Step 5 — Access
```
Browser: http://localhost:5173
Login:   admin / admin123
API Docs: http://localhost:8000/docs
```

### Step 6 — Run Your First Pipeline
1. Login with admin / admin123
2. Navigate to "Pipeline" in the sidebar
3. Click "Run Full Analysis"
4. Watch all 6 agents execute in sequence
5. View the Manufacturing Intelligence Report

---

## 21. Project Statistics

| Metric | Count |
|---|---|
| Total Python lines | ~15,255 |
| Agent code | 765 lines |
| Tool code | 5,439 lines |
| Backend server code | 3,000+ lines |
| Frontend pages | 10 pages |
| Frontend components | 14 reusable components |
| Database tables | 20+ tables |
| API endpoints | 40+ endpoints |
| Agent personalities | 6 system prompts |
| Tools available | 36 tools (6 per agent) |
| Python dependencies | 7 core packages |
| npm packages | 40+ packages |
| Default users | 3 (admin, manager, operator) |
| Documentation files | 70+ markdown files |
| Documentation lines | ~39,951 lines |
| Database size | 280 KB (SQLite) |
| Product in demo | PROD-A (Industrial Valve Assembly) |
| Machines in demo | 6 machines (MCH-001 to MCH-006) |
| Suppliers in demo | 2 (SUP-A, SUP-B) |
| BOM components | 6 (SH-100, VSA-200, AM-300, SOR-400, FS-500, IL-600) |
| Historical demand weeks | 12 weeks |
| Monte Carlo simulations | 1,000 per run |
| Planning horizon | 4 weeks (default) |

---

*Documentation generated: 2026-03-22*
*AMIS Phase 1 — Autonomous Manufacturing Intelligence System*
