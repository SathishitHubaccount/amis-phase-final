"""
AMIS FastAPI Backend
Production-ready API for React frontend
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import uuid
from datetime import datetime
import sys
import os
import io

# Fix Windows encoding issues with Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.demand_agent import DemandForecastingAgent
from agents.inventory_agent import InventoryManagementAgent
from agents.machine_health_agent import MachineHealthAgent
from agents.production_agent import ProductionPlanningAgent
from agents.supplier_agent import SupplierProcurementAgent
from agents.orchestrator_agent import OrchestratorAgent

# Import database functions
from database import (
    get_all_products, get_product, get_inventory, get_all_inventory, update_inventory,
    get_all_machines, get_machine, get_machines_by_product, update_machine,
    create_work_order, get_work_orders, update_work_order_status,
    log_activity, get_activity_log,
    get_all_suppliers, get_supplier,
    get_bom, get_database_stats,
    # Production planning
    get_production_lines, get_production_schedule, update_production_schedule,
    # History for charts
    get_inventory_history, get_machine_oee_history,
    # Inventory adjustment
    adjust_inventory,
    # Authentication
    get_user, update_last_login,
    # Demand forecasting
    create_demand_forecast, get_demand_forecasts, update_actual_demand,
    # Decisions audit
    ensure_decisions_table, save_decision, get_decisions,
)

# Authentication imports
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from auth import (
    create_access_token, get_current_active_user, verify_password,
    require_role, Token, User, ACCESS_TOKEN_EXPIRE_MINUTES
)

# CSV Export utilities
import exports
from fastapi.responses import Response

# Pipeline formatting
from pipeline_formatter import format_pipeline_result

# Approval system
from approval_system import get_approval_system

app = FastAPI(title="AMIS API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo (replace with database in production)
pipeline_runs: Dict[str, Dict[str, Any]] = {}
agent_runs: Dict[str, Dict[str, Any]] = {}

# Ensure decisions table exists on startup
ensure_decisions_table()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AgentRunRequest(BaseModel):
    agent_type: str
    prompt: str
    product_id: Optional[str] = "PROD-A"


class PipelineRunRequest(BaseModel):
    product_id: Optional[str] = "PROD-A"


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint - returns JWT access token

    Default users:
    - admin / admin123 (admin role)
    - manager / manager123 (manager role)
    - operator / operator123 (operator role)
    """
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    update_last_login(user["username"])

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current logged-in user information"""
    return current_user


@app.get("/api/auth/health")
async def auth_health():
    """Check if authentication system is working"""
    return {"status": "ok", "auth_enabled": True, "message": "Authentication system operational"}


# ============================================================================
# AGENT INSTANCES (LAZY INITIALIZATION)
# ============================================================================

_agents = {}

def get_agent(agent_type: str):
    """Get or create agent instance"""
    if agent_type not in _agents:
        agent_classes = {
            "demand": DemandForecastingAgent,
            "inventory": InventoryManagementAgent,
            "machine": MachineHealthAgent,
            "production": ProductionPlanningAgent,
            "supplier": SupplierProcurementAgent,
            "orchestrator": OrchestratorAgent,
        }
        if agent_type not in agent_classes:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
        _agents[agent_type] = agent_classes[agent_type]()
    return _agents[agent_type]


# ============================================================================
# BACKGROUND TASK RUNNERS
# ============================================================================

async def run_agent_task(run_id: str, agent_type: str, prompt: str):
    """Run agent in background and store results"""
    try:
        agent_runs[run_id]["status"] = "running"
        agent_runs[run_id]["started_at"] = datetime.utcnow().isoformat()

        # Run agent synchronously (convert to async in production)
        agent = get_agent(agent_type)
        result = await asyncio.to_thread(agent.run, prompt)

        agent_runs[run_id].update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "result": result,
            "error": None
        })
    except Exception as e:
        agent_runs[run_id].update({
            "status": "failed",
            "completed_at": datetime.utcnow().isoformat(),
            "error": str(e)
        })


async def run_pipeline_task(run_id: str, product_id: str):
    """Run full 5-agent pipeline in background"""
    try:
        pipeline_runs[run_id]["status"] = "running"
        pipeline_runs[run_id]["started_at"] = datetime.utcnow().isoformat()

        # Run orchestrator - use run_full_pipeline for structured output
        orchestrator = get_agent("orchestrator")

        # Get structured pipeline result (not just text)
        structured_result = await asyncio.to_thread(
            orchestrator.run_full_pipeline,
            product_id=product_id,
            planning_weeks=4
        )

        # Format human-readable text result for display
        text_result = format_pipeline_result(structured_result)

        # ========== NEW: AUTOMATICALLY SYNC TO DATABASE ==========
        from ai_database_bridge import get_bridge
        bridge = get_bridge()
        sync_result = bridge.sync_pipeline_results(structured_result, auto_execute=True)
        # ========================================================

        pipeline_runs[run_id].update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "result": text_result,
            "structured_result": structured_result,  # Store structured data too
            "database_sync": sync_result,  # Store sync status
            "agents_completed": ["demand", "inventory", "machine", "production", "supplier"],
            "error": None
        })
    except Exception as e:
        pipeline_runs[run_id].update({
            "status": "failed",
            "completed_at": datetime.utcnow().isoformat(),
            "error": str(e)
        })


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "AMIS API",
        "version": "1.0.0",
        "agents": ["demand", "inventory", "machine", "production", "supplier", "orchestrator"]
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents_loaded": len(_agents),
        "active_runs": len([r for r in agent_runs.values() if r["status"] == "running"])
    }


# ============================================================================
# AGENT EXECUTION ENDPOINTS
# ============================================================================

@app.post("/api/agents/run")
async def run_agent(request: AgentRunRequest, background_tasks: BackgroundTasks):
    """Run a single agent"""
    run_id = str(uuid.uuid4())

    agent_runs[run_id] = {
        "id": run_id,
        "agent_type": request.agent_type,
        "prompt": request.prompt,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None
    }

    background_tasks.add_task(run_agent_task, run_id, request.agent_type, request.prompt)

    return {"run_id": run_id, "status": "pending"}


@app.get("/api/agents/runs/{run_id}")
async def get_agent_run(run_id: str):
    """Get agent run status and results"""
    if run_id not in agent_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    return agent_runs[run_id]


@app.post("/api/pipeline/run")
async def run_pipeline(request: PipelineRunRequest, background_tasks: BackgroundTasks):
    """Run full 5-agent pipeline"""
    run_id = str(uuid.uuid4())

    pipeline_runs[run_id] = {
        "id": run_id,
        "product_id": request.product_id,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
        "agents_completed": [],
        "result": None,
        "error": None
    }

    background_tasks.add_task(run_pipeline_task, run_id, request.product_id)

    return {"run_id": run_id, "status": "pending"}


@app.get("/api/pipeline/runs/{run_id}")
async def get_pipeline_run(run_id: str):
    """Get pipeline run status and results"""
    if run_id not in pipeline_runs:
        raise HTTPException(status_code=404, detail="Run not found")

    run_data = pipeline_runs[run_id]

    # Add sync status to response
    if "database_sync" in run_data:
        run_data["sync_status"] = {
            "synced": run_data["database_sync"]["success"],
            "changes_count": len(run_data["database_sync"]["changes_made"]),
            "changes": run_data["database_sync"]["changes_made"],
            "warnings": run_data["database_sync"]["warnings"],
            "errors": run_data["database_sync"]["errors"]
        }

    return run_data


@app.get("/api/pipeline/runs")
async def list_pipeline_runs(limit: int = 10):
    """List recent pipeline runs"""
    sorted_runs = sorted(
        pipeline_runs.values(),
        key=lambda x: x["created_at"],
        reverse=True
    )
    return sorted_runs[:limit]


@app.get("/api/pipeline/latest-forecast/{product_id}")
async def get_latest_ai_forecast(product_id: str):
    """Get latest AI forecast for a product from pipeline runs"""
    print(f"[DEBUG] Looking for product_id: {product_id}")
    print(f"[DEBUG] Total pipeline_runs: {len(pipeline_runs)}")
    print(f"[DEBUG] All product_ids in runs: {[run.get('product_id') for run in pipeline_runs.values()]}")

    # Find latest completed pipeline run for this product
    product_runs = [
        run for run in pipeline_runs.values()
        if run.get("product_id") == product_id and run.get("status") == "completed"
    ]

    print(f"[DEBUG] Found {len(product_runs)} matching runs")

    if not product_runs:
        raise HTTPException(status_code=404, detail="No completed AI analysis found for this product")

    # Get most recent run
    latest_run = sorted(product_runs, key=lambda x: x["created_at"], reverse=True)[0]

    # Parse the AI result to extract forecast data
    result_text = latest_run.get("result", "")

    # Extract forecast numbers from the AI result
    # The AI result contains sections like:
    # "Market Demand: 1,345 units/week (base case)"
    # "scenarios": {"optimistic": {"weekly_avg": 1583}, "base": {"weekly_avg": 1345}, "pessimistic": {"weekly_avg": 1040}}

    import re
    import json

    forecast_data = {
        "product_id": product_id,
        "source": "ai_pipeline",
        "run_id": latest_run["id"],
        "generated_at": latest_run["completed_at"],
        "base_case": None,
        "optimistic": None,
        "pessimistic": None,
        "growth_rate": None,
        "confidence_interval": {}
    }

    # Try to extract data from markdown format
    try:
        # Pattern 1: Look for "Market Demand: 1,345 units/week (base case)"
        market_demand_match = re.search(r'Market Demand[:\*\s]+([0-9,]+)\s*units/week\s*\(base case\)', result_text, re.IGNORECASE)
        if market_demand_match:
            base_value = market_demand_match.group(1).replace(',', '')
            forecast_data["base_case"] = int(base_value)

        # Pattern 2: Look for JSON-like scenario data (from structured agent output)
        if "scenarios" in result_text:
            optimistic_match = re.search(r'"optimistic"[^}]*"weekly_avg"[:\s]+(\d+)', result_text, re.DOTALL)
            base_match = re.search(r'"base"[^}]*"weekly_avg"[:\s]+(\d+)', result_text, re.DOTALL)
            pessimistic_match = re.search(r'"pessimistic"[^}]*"weekly_avg"[:\s]+(\d+)', result_text, re.DOTALL)

            if optimistic_match:
                forecast_data["optimistic"] = int(optimistic_match.group(1))
            if base_match and not forecast_data["base_case"]:
                forecast_data["base_case"] = int(base_match.group(1))
            if pessimistic_match:
                forecast_data["pessimistic"] = int(pessimistic_match.group(1))

        # Pattern 3: Look for growth rate (e.g., "growing 3.3% weekly" or "3.12% per week")
        growth_match = re.search(r'growing\s+([0-9.]+)%\s*(?:weekly|per week)', result_text, re.IGNORECASE)
        if growth_match:
            forecast_data["growth_rate"] = float(growth_match.group(1))

        # If we found base_case, auto-calculate missing optimistic/pessimistic
        if forecast_data["base_case"]:
            if not forecast_data["optimistic"]:
                forecast_data["optimistic"] = int(forecast_data["base_case"] * 1.2)
            if not forecast_data["pessimistic"]:
                forecast_data["pessimistic"] = int(forecast_data["base_case"] * 0.8)

        # If still no data found, try to find any mention of weekly units
        if not forecast_data["base_case"]:
            weekly_units_match = re.search(r'(\d{3,})\s*units/week', result_text)
            if weekly_units_match:
                forecast_data["base_case"] = int(weekly_units_match.group(1))
                forecast_data["optimistic"] = int(forecast_data["base_case"] * 1.2)
                forecast_data["pessimistic"] = int(forecast_data["base_case"] * 0.8)

    except Exception as e:
        # If parsing fails, return basic suggestion
        forecast_data["error"] = f"Could not fully parse AI result: {str(e)}"
        forecast_data["base_case"] = 1000  # Default suggestion
        forecast_data["optimistic"] = 1200
        forecast_data["pessimistic"] = 800

    return forecast_data


# ============================================================================
# DASHBOARD DATA ENDPOINTS
# ============================================================================

@app.get("/api/dashboard/summary")
async def get_dashboard_summary():
    """Get dashboard summary data - NOW WITH REAL DATA FROM DATABASE!"""

    # Get all machines to calculate OEE and identify critical ones
    machines = get_all_machines()
    total_oee = sum(m['oee'] for m in machines) / len(machines) * 100 if machines else 0
    critical_machines = [m['id'] for m in machines if m.get('failure_risk', 0) * 100 > 40]
    machines_status = "critical" if len(critical_machines) > 2 else "at_risk" if len(critical_machines) > 0 else "healthy"

    # Get inventory to count items below reorder point
    all_inventory = []
    products = get_all_products()
    for product in products:
        inv = get_inventory(product['id'])
        if inv:
            all_inventory.append(inv)

    below_rop = sum(1 for inv in all_inventory if inv.get('current_stock', 0) < inv.get('reorder_point', 0))
    avg_days_supply = sum(
        inv.get('current_stock', 0) / max(inv.get('avg_daily_usage', 1), 1)
        for inv in all_inventory
    ) / len(all_inventory) if all_inventory else 0
    inventory_status = "critical" if below_rop > 2 else "at_risk" if below_rop > 0 else "healthy"

    # Get production schedule to calculate demand and attainment
    total_demand = 0
    total_planned = 0
    for product in products[:3]:  # Sample first 3 products
        schedule = get_production_schedule(product['id'], weeks=1)
        if schedule:
            total_demand += schedule[0].get('demand', 0)
            total_planned += schedule[0].get('planned_production', 0)

    production_gap = total_planned - total_demand
    production_attainment = round((total_planned / total_demand * 100)) if total_demand > 0 else 100
    production_status = "critical" if production_attainment < 85 else "watch" if production_attainment < 95 else "healthy"

    # Calculate overall system health (weighted average)
    health_scores = {
        'machines': 100 - (len(critical_machines) * 15),  # -15 per critical machine
        'inventory': max(0, 100 - (below_rop * 20)),       # -20 per item below ROP
        'production': production_attainment,
        'oee': total_oee  # Already converted to 0-100 percentage above
    }
    system_health = round(sum(health_scores.values()) / len(health_scores))
    overall_status = "critical" if system_health < 60 else "at_risk" if system_health < 80 else "healthy"

    # Build alerts from real data
    alerts = []
    alert_id = 1

    # Machine alerts
    for machine in machines:
        if machine.get('failure_risk', 0) > 40:
            alerts.append({
                "id": str(alert_id),
                "severity": "critical" if machine['failure_risk'] > 60 else "high",
                "title": f"{machine['id']} failure risk {machine['failure_risk']}% (7-day)",
                "category": "machine",
                "created_at": datetime.utcnow().isoformat()
            })
            alert_id += 1

    # Inventory alerts
    for inv in all_inventory:
        if inv.get('current_stock', 0) < inv.get('reorder_point', 0):
            alerts.append({
                "id": str(alert_id),
                "severity": "high" if inv.get('stockout_risk', 0) > 20 else "medium",
                "title": f"{inv.get('product_id')} below reorder point ({inv.get('current_stock')} units)",
                "category": "inventory",
                "created_at": datetime.utcnow().isoformat()
            })
            alert_id += 1

    # Limit to top 5 alerts
    alerts = sorted(alerts, key=lambda x: {"critical": 0, "high": 1, "medium": 2}.get(x['severity'], 3))[:5]

    return {
        "system_health": system_health,
        "status": overall_status,
        "metrics": {
            "demand": {
                "value": f"{total_demand:,}/wk",
                "trend": "+0.0%",  # Would need historical data to calculate
                "status": production_status
            },
            "inventory": {
                "value": f"{avg_days_supply:.1f} days",
                "below_rop": below_rop,
                "status": inventory_status
            },
            "machines": {
                "oee": f"{total_oee:.0f}%",
                "critical_machines": critical_machines,
                "status": machines_status
            },
            "production": {
                "attainment": f"{production_attainment}%",
                "gap": production_gap,
                "status": production_status
            }
        },
        "alerts": alerts,
        "last_updated": datetime.utcnow().isoformat()
    }


@app.post("/api/chat")
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """Chat with AMIS AI"""
    run_id = str(uuid.uuid4())

    # Determine which agent to use based on message content
    message_lower = request.message.lower()
    if any(word in message_lower for word in ["demand", "forecast", "sales"]):
        agent_type = "demand"
    elif any(word in message_lower for word in ["inventory", "stock", "reorder"]):
        agent_type = "inventory"
    elif any(word in message_lower for word in ["machine", "maintenance", "equipment"]):
        agent_type = "machine"
    elif any(word in message_lower for word in ["production", "schedule", "capacity"]):
        agent_type = "production"
    elif any(word in message_lower for word in ["supplier", "procurement", "order"]):
        agent_type = "supplier"
    else:
        agent_type = "orchestrator"  # Default to orchestrator for general questions

    agent_runs[run_id] = {
        "id": run_id,
        "agent_type": agent_type,
        "prompt": request.message,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None
    }

    background_tasks.add_task(run_agent_task, run_id, agent_type, request.message)

    return {
        "run_id": run_id,
        "agent_routed": agent_type,
        "status": "pending"
    }


# ============================================================================
# DATABASE-POWERED ENDPOINTS
# ============================================================================

@app.get("/api/products")
async def list_products():
    """Get all products from database"""
    products = get_all_products()
    return {"products": products}

@app.get("/api/products/{product_id}")
async def get_product_detail(product_id: str):
    """Get single product details"""
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/api/products/{product_id}/inventory")
async def get_product_inventory(product_id: str):
    """Get inventory data for specific product"""
    inventory = get_inventory(product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")

    # Log activity
    log_activity("API User", "View Inventory", f"Viewed inventory for {product_id}")

    return inventory

@app.get("/api/products/{product_id}/bom")
async def get_product_bom(product_id: str):
    """Get Bill of Materials for product"""
    bom = get_bom(product_id)
    # Remap field names to match frontend expectations
    normalized = [
        {
            **item,
            "quantity_needed": item.get("quantity"),
            "current_stock": item.get("stock"),
            "unit_cost": item.get("cost"),
            "supplier_name": item.get("supplier"),
        }
        for item in bom
    ]
    return {"product_id": product_id, "bom": normalized}

def _normalize_machine(m: dict) -> dict:
    """Normalize machine fields for frontend consumption."""
    failure_risk_pct = round(m.get("failure_risk", 0) * 100, 1)
    raw_status = m.get("status", "operational")
    if raw_status == "down":
        ui_status = "critical"
    elif failure_risk_pct > 40:
        ui_status = "at_risk"
    else:
        ui_status = "healthy"
    return {
        **m,
        "oee": round(m.get("oee", 0) * 100, 1),
        "availability": round(m.get("availability", 0) * 100, 1),
        "performance": round(m.get("performance", 0) * 100, 1),
        "quality": round(m.get("quality", 0) * 100, 1),
        "failure_risk": failure_risk_pct,
        "failureRisk": failure_risk_pct,
        "current_utilization": round(m.get("current_utilization", 0) * 100, 1),
        "status": ui_status,
        "raw_status": raw_status,
        "nextMaintenance": m.get("next_maintenance"),
    }

@app.get("/api/machines")
async def list_machines(product_id: Optional[str] = None):
    """Get all machines, optionally filtered by product"""
    if product_id:
        machines = get_machines_by_product(product_id)
        if not machines:  # product_machines join table empty — return all machines
            machines = get_all_machines()
    else:
        machines = get_all_machines()
    return {"machines": [_normalize_machine(m) for m in machines]}

@app.get("/api/machines/{machine_id}")
async def get_machine_detail(machine_id: str):
    """Get detailed machine info including alarms, spare parts, maintenance history"""
    machine = get_machine(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    # Log activity
    log_activity("API User", "View Machine Details", f"Viewed details for {machine['name']} ({machine_id})")

    return _normalize_machine(machine)

@app.post("/api/work-orders")
async def create_new_work_order(work_order: dict):
    """Create a work order"""
    try:
        wo_id = create_work_order(work_order)

        # Log activity
        log_activity(
            user=work_order.get('created_by', 'System User'),
            action='Work Order Created',
            details=f"Created {work_order['type']} work order {wo_id} for {work_order['machine_id']}, assigned to {work_order.get('assigned_to', 'Unassigned')}, Priority: {work_order['priority']}"
        )

        return {"work_order_id": wo_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/work-orders")
async def list_work_orders(machine_id: Optional[str] = None, limit: int = 50):
    """Get work orders, optionally filtered by machine"""
    work_orders = get_work_orders(machine_id, limit)
    return {"work_orders": work_orders}

@app.patch("/api/work-orders/{wo_id}/status")
async def update_wo_status(wo_id: str, status_update: dict):
    """Update work order status"""
    success = update_work_order_status(wo_id, status_update['status'])
    if not success:
        raise HTTPException(status_code=404, detail="Work order not found")

    log_activity("API User", "Work Order Updated", f"Updated status of {wo_id} to {status_update['status']}")
    return {"success": True}

@app.get("/api/suppliers")
async def list_suppliers():
    """Get all suppliers"""
    suppliers = get_all_suppliers()
    return {"suppliers": suppliers}

@app.get("/api/purchase-orders")
async def list_purchase_orders(status: Optional[str] = None):
    """Get purchase orders from the database, optionally filtered by status"""
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), "amis.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if status:
        cur.execute(
            "SELECT po.*, s.name as supplier_name FROM purchase_orders po LEFT JOIN suppliers s ON po.supplier_id = s.id WHERE po.status = ? ORDER BY po.order_date DESC",
            (status,)
        )
    else:
        cur.execute(
            "SELECT po.*, s.name as supplier_name FROM purchase_orders po LEFT JOIN suppliers s ON po.supplier_id = s.id ORDER BY po.order_date DESC LIMIT 20"
        )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"purchase_orders": rows}

@app.get("/api/suppliers/{supplier_id}")
async def get_supplier_detail(supplier_id: str):
    """Get detailed supplier info including certifications, contracts, incidents"""
    supplier = get_supplier(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    # Log activity
    log_activity("API User", "View Supplier Details", f"Viewed details for {supplier['name']} ({supplier_id})")

    return supplier

@app.get("/api/activity-log")
async def get_activities(limit: int = 100):
    """Get activity log for audit trail"""
    activities = get_activity_log(limit)
    return {"activities": activities}

@app.get("/api/database/stats")
async def get_db_stats():
    """Get database statistics"""
    stats = get_database_stats()
    return stats

# ============================================================================
# PRODUCTION PLANNING ENDPOINTS
# ============================================================================

@app.get("/api/production/lines")
async def list_production_lines(product_id: Optional[str] = None):
    """Get production lines, optionally filtered by product"""
    lines = get_production_lines(product_id)
    normalized = []
    for line in lines:
        raw_status = line.get("status", "operational")
        ui_status = "running" if raw_status == "operational" else "maintenance"
        normalized.append({
            **line,
            "status": ui_status,
            "utilization": round(line.get("utilization", 0) * 100, 1),
            "efficiency": round(line.get("efficiency", 0) * 100, 1),
        })
    return {"production_lines": normalized}

@app.get("/api/production/schedule/{product_id}")
async def get_schedule(product_id: str, weeks: int = 4):
    """Get production schedule for a product"""
    schedule = get_production_schedule(product_id, weeks)

    # Log activity
    log_activity("API User", "View Production Schedule", f"Viewed {weeks}-week schedule for {product_id}")

    return {"schedule": schedule, "product_id": product_id}

# ============================================================================
# HISTORY/TREND ENDPOINTS FOR CHARTS
# ============================================================================

@app.get("/api/inventory/{product_id}/history")
async def get_inventory_trend(product_id: str, days: int = 30):
    """Get inventory history for trend charts"""
    history = get_inventory_history(product_id, days)
    return {"history": history, "product_id": product_id}

@app.get("/api/machines/{machine_id}/oee-history")
async def get_oee_trend(machine_id: str, days: int = 30):
    """Get machine OEE history for trend charts"""
    history = get_machine_oee_history(machine_id, days)
    return {"history": history, "machine_id": machine_id}

# ============================================================================
# INVENTORY ADJUSTMENT ENDPOINT
# ============================================================================

@app.post("/api/inventory/{product_id}/adjust")
async def adjust_product_inventory(product_id: str, adjustment: dict):
    """Adjust inventory (add or remove stock)"""
    quantity = adjustment.get('quantity', 0)
    reason = adjustment.get('reason', 'Manual adjustment')
    user = adjustment.get('user', 'API User')

    success = adjust_inventory(product_id, quantity, reason, user)

    if not success:
        raise HTTPException(status_code=400, detail="Adjustment failed (invalid product or negative stock)")

    # Return updated inventory
    updated_inventory = get_inventory(product_id)
    return {"success": True, "inventory": updated_inventory}

# ============================================================================
# CSV EXPORT ENDPOINTS
# ============================================================================

@app.get("/api/export/inventory")
async def export_inventory():
    """Export all inventory data to CSV"""
    inventory_data = get_all_inventory()
    csv_data = exports.export_inventory(inventory_data)
    filename = exports.generate_filename("inventory_export")

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/export/machines")
async def export_machines_data():
    """Export all machines data to CSV"""
    machines_data = get_all_machines()
    csv_data = exports.export_machines(machines_data)
    filename = exports.generate_filename("machines_export")

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/export/machines/{machine_id}/oee")
async def export_machine_oee(machine_id: str, days: int = 30):
    """Export machine OEE history to CSV"""
    oee_data = get_machine_oee_history(machine_id, days)
    csv_data = exports.export_oee_history(oee_data, machine_id)
    filename = exports.generate_filename(f"machine_{machine_id}_oee")

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/export/production/{product_id}")
async def export_production_schedule_data(product_id: str, weeks: int = 4):
    """Export production schedule to CSV"""
    schedule_data = get_production_schedule(product_id, weeks)
    csv_data = exports.export_production_schedule(schedule_data)
    filename = exports.generate_filename(f"production_schedule_{product_id}")

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/export/suppliers")
async def export_suppliers_data():
    """Export all suppliers data to CSV"""
    suppliers_data = get_all_suppliers()
    csv_data = exports.export_suppliers(suppliers_data)
    filename = exports.generate_filename("suppliers_export")

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/export/work-orders")
async def export_work_orders_data(machine_id: Optional[str] = None):
    """Export work orders to CSV"""
    work_orders_data = get_work_orders(machine_id, limit=1000)
    csv_data = exports.export_work_orders(work_orders_data)
    filename = exports.generate_filename("work_orders_export")

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/export/inventory/{product_id}/history")
async def export_inventory_history_data(product_id: str, days: int = 30):
    """Export inventory history to CSV"""
    history_data = get_inventory_history(product_id, days)
    csv_data = exports.export_inventory_history(history_data, product_id)
    filename = exports.generate_filename(f"inventory_history_{product_id}")

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ============================================================================
# DEMAND FORECASTING ENDPOINTS
# ============================================================================

@app.post("/api/demand/forecast")
async def create_forecast(forecast: dict):
    """Create demand forecast"""
    try:
        forecast_id = create_demand_forecast(
            forecast['product_id'],
            forecast['week_number'],
            forecast
        )
        return {"success": True, "forecast_id": forecast_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/demand/forecast/{product_id}")
async def get_forecasts(product_id: str, weeks: int = 12):
    """Get demand forecasts for product"""
    forecasts = get_demand_forecasts(product_id, weeks)
    return {"forecasts": forecasts, "product_id": product_id}

@app.patch("/api/demand/actual/{product_id}/{week}")
async def update_actual(product_id: str, week: int, update: dict):
    """Update actual demand"""
    success = update_actual_demand(product_id, week, update['actual'])
    if not success:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return {"success": True}

# ============================================================================
# PRODUCTION SCHEDULE UPDATE ENDPOINT
# ============================================================================

@app.put("/api/production/schedule/{schedule_id}")
async def update_schedule(schedule_id: int, updates: dict):
    """Update production schedule"""
    success = update_production_schedule(schedule_id, updates)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"success": True}


# ============================================================================
# AGENT NEGOTIATION ENDPOINT
# ============================================================================

class NegotiationRequest(BaseModel):
    scenario_type: str
    product_id: Optional[str] = "PROD-A"
    customer_order: Optional[int] = 2000
    timeline_days: Optional[int] = 3
    custom_constraints: Optional[Dict[str, Any]] = None


@app.post("/api/negotiation/run")
async def run_negotiation(request: NegotiationRequest):
    """
    Run multi-agent negotiation for complex decision-making

    Scenario types:
    - demand_spike: Customer order exceeds capacity
    - supplier_failure: Primary supplier unable to deliver
    - machine_breakdown: Critical equipment failure
    - cost_pressure: Need to reduce costs while maintaining quality
    """
    try:
        from agent_negotiation import AgentNegotiator

        # Build scenario based on type
        if request.scenario_type == "demand_spike":
            # Get current capacity from database
            product = get_product(request.product_id)
            inventory_data = get_inventory(request.product_id)

            scenario = {
                "problem": f"Customer emergency order: {request.customer_order} units in {request.timeline_days} days",
                "constraints": {
                    "customer_order": request.customer_order,
                    "timeline_days": request.timeline_days,
                    "production_capacity": 1500,  # units per 3 days
                    "current_inventory": inventory_data.get('current_stock', 300) if inventory_data else 300,
                    "safety_stock_minimum": 200,
                    "overtime_cost_per_100_units": 3000,
                    "customer_lifetime_value": 500000,
                    "competitor_bidding": True,
                    **(request.custom_constraints or {})
                },
                "question": "Should we accept this order? If yes, how do we fulfill it?"
            }

        elif request.scenario_type == "supplier_failure":
            scenario = {
                "problem": f"Primary supplier for {request.product_id} cannot deliver critical components",
                "constraints": {
                    "affected_product": request.product_id,
                    "missing_components": 500,
                    "production_impact_days": 5,
                    "alternative_suppliers_available": 2,
                    "alternative_cost_premium": 0.25,  # 25% more expensive
                    "customer_orders_at_risk": 3,
                    **(request.custom_constraints or {})
                },
                "question": "How do we mitigate this supplier failure?"
            }

        elif request.scenario_type == "machine_breakdown":
            scenario = {
                "problem": f"Critical machine for {request.product_id} has failed",
                "constraints": {
                    "affected_product": request.product_id,
                    "machine_id": "MCH-004",
                    "repair_time_days": 5,
                    "repair_cost": 40000,
                    "alternative_machine_capacity": 0.6,  # 60% of failed machine
                    "production_loss_per_day": 300,
                    **(request.custom_constraints or {})
                },
                "question": "What's the best way to handle this breakdown?"
            }

        elif request.scenario_type == "cost_pressure":
            scenario = {
                "problem": f"Need to reduce manufacturing costs by 15% for {request.product_id}",
                "constraints": {
                    "affected_product": request.product_id,
                    "cost_reduction_target": 0.15,
                    "current_unit_cost": 50,
                    "quality_standards_must_maintain": True,
                    "volume_unchanged": True,
                    **(request.custom_constraints or {})
                },
                "question": "How can we achieve cost reduction without compromising quality?"
            }

        else:
            # Custom scenario
            scenario = {
                "problem": f"Custom scenario for {request.product_id}",
                "constraints": request.custom_constraints or {},
                "question": "What should we do?"
            }

        # Initialize agents for negotiation
        agents = [
            DemandForecastingAgent(),
            InventoryManagementAgent(),
            ProductionPlanningAgent()
        ]

        # Run negotiation
        negotiator = AgentNegotiator(agents)
        result = await asyncio.to_thread(negotiator.negotiate, scenario)

        # Log activity
        log_activity(
            "System",
            "Agent Negotiation",
            f"Negotiation completed for {request.scenario_type} scenario"
        )

        return {
            "status": "completed",
            "negotiation_id": str(uuid.uuid4()),
            "scenario_type": request.scenario_type,
            "result": result
        }

    except Exception as e:
        print(f"Error in negotiation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Negotiation failed: {str(e)}"
        )


# ============================================================================
# DECISIONS (AUDIT LOG) ENDPOINTS
# ============================================================================

class DecisionRequest(BaseModel):
    agent_type: str          # machine / inventory / demand / production / supplier
    title: str               # short description of what was recommended
    status: str              # Accepted | Modified | Dismissed
    action_by: Optional[str] = "Manager"
    note: Optional[str] = None    # manager's modification note
    detail: Optional[str] = None  # full AI recommendation text


@app.post("/api/decisions")
async def record_decision(request: DecisionRequest):
    """Save a manager's Accept / Modify / Dismiss decision permanently"""
    decision_id = save_decision(
        agent_type=request.agent_type,
        title=request.title,
        status=request.status,
        action_by=request.action_by,
        note=request.note,
        detail=request.detail,
    )
    return {"id": decision_id, "status": "saved"}


@app.get("/api/decisions")
async def list_decisions(limit: int = 50):
    """Return all recorded decisions for the Audit Log"""
    rows = get_decisions(limit)
    return {"decisions": rows, "total": len(rows)}


# ============================================================================
# APPROVAL ENDPOINTS
# ============================================================================

@app.get("/api/approvals/pending")
async def get_pending_approvals():
    """Return all pending AI decisions awaiting manager approval"""
    approval_system = get_approval_system()
    pending = approval_system.get_pending_as_dicts()
    return {"pending": pending, "count": len(pending)}


class ApprovalDecisionRequest(BaseModel):
    action: str          # "approve" | "reject" | "modify"
    approved_by: Optional[str] = "Manager"
    notes: Optional[str] = None


@app.post("/api/approvals/{decision_id}/decide")
async def decide_approval(decision_id: int, request: ApprovalDecisionRequest):
    """Accept, modify, or reject a pending AI decision"""
    approval_system = get_approval_system()

    # Fetch the decision
    conn_check = __import__('database').get_db_connection()
    cursor = conn_check.cursor()
    cursor.execute("SELECT * FROM ai_decisions WHERE id = ?", (decision_id,))
    row = cursor.fetchone()
    conn_check.close()

    if not row:
        raise HTTPException(status_code=404, detail="Decision not found")

    row = dict(row)

    import json as _json
    payload = _json.loads(row['payload']) if row.get('payload') else {}
    impact = _json.loads(row['impact_analysis']) if row.get('impact_analysis') else {}
    product_id = impact.get('product_id', 'PROD-A')

    if request.action in ('approve', 'modify'):
        success = approval_system.approve_decision(decision_id, request.approved_by, request.notes or '')
        if success and payload:
            from ai_database_bridge import get_bridge
            bridge = get_bridge()
            exec_result = bridge.execute_approved_decision(
                decision_id=decision_id,
                decision_type=row['decision_type'],
                payload=payload,
                product_id=product_id,
            )
            save_decision(
                agent_type=row['decision_type'].split('_')[0],
                title=row['action'],
                status='Accepted' if request.action == 'approve' else 'Modified',
                action_by=request.approved_by,
                note=request.notes,
                detail=row['description']
            )
            return {"status": "approved_and_executed", "changes": exec_result.get("changes", [])}
        return {"status": "approved", "executed": False}

    elif request.action == 'reject':
        success = approval_system.reject_decision(decision_id, request.approved_by, request.notes or 'Rejected by manager')
        save_decision(
            agent_type=row['decision_type'].split('_')[0],
            title=row['action'],
            status='Dismissed',
            action_by=request.approved_by,
            note=request.notes,
            detail=row['description']
        )
        return {"status": "rejected"}

    raise HTTPException(status_code=400, detail="action must be approve, modify, or reject")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
