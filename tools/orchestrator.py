"""
AMIS Orchestrator Tools
========================
These tools give the Orchestrator Agent programmatic access to all 5 specialist agents.
Each tool calls the agent's bridge method (no LLM loop) and returns structured JSON.
The Orchestrator LLM then reasons over the consolidated data.
"""
import json
from langchain_core.tools import tool


# ══════════════════════════════════════════════════════════════════
# TOOL 1: Demand Intelligence
# ══════════════════════════════════════════════════════════════════

@tool
def get_demand_intelligence(product_id: str = "PROD-A") -> str:
    """
    Retrieve structured demand intelligence from the Demand Forecasting Agent.

    Calls the Demand Agent's programmatic bridge (no LLM loop) and returns:
    - Multi-scenario weekly demand forecast (pessimistic/base/optimistic)
    - Trend direction and growth rate
    - Anomaly detection flag
    - 95% confidence interval
    - Recommended production strategy

    Use this as the first step in every full-pipeline orchestration run.
    The demand forecast sets the production TARGET for all downstream agents.

    Args:
        product_id: Product identifier (default PROD-A)

    Returns:
        JSON string with demand envelope including scenarios, trend, anomaly flag.
    """
    from agents.demand_agent import DemandForecastingAgent
    agent = DemandForecastingAgent()
    envelope = agent.get_forecast_output(product_id=product_id)
    return json.dumps(envelope, indent=2)


# ══════════════════════════════════════════════════════════════════
# TOOL 2: Inventory Intelligence
# ══════════════════════════════════════════════════════════════════

@tool
def get_inventory_intelligence(product_id: str = "PROD-A", planning_weeks: int = 4) -> str:
    """
    Retrieve structured inventory intelligence from the Inventory Management Agent.

    Calls the Inventory Agent's programmatic bridge (no LLM loop) and returns:
    - Current stock, safety stock, days of supply
    - Stockout probability over the planning horizon
    - Reorder point status and urgency
    - Replenishment plan summary (total units, cost, minimum projected stock)

    Use this after get_demand_intelligence to understand if current stock can
    absorb the forecast or if an urgent replenishment is needed.

    Args:
        product_id: Product identifier (default PROD-A)
        planning_weeks: Number of weeks to plan for (default 4)

    Returns:
        JSON string with inventory position, stockout risk, and replenishment summary.
    """
    from agents.inventory_agent import InventoryManagementAgent
    agent = InventoryManagementAgent()
    envelope = agent.get_inventory_output(product_id=product_id, planning_weeks=planning_weeks)
    return json.dumps(envelope, indent=2)


# ══════════════════════════════════════════════════════════════════
# TOOL 3: Machine Health Intelligence
# ══════════════════════════════════════════════════════════════════

@tool
def get_machine_health_intelligence(plant_id: str = "PLANT-01") -> str:
    """
    Retrieve structured machine health intelligence from the Machine Health Agent.

    Calls the Machine Health Agent's programmatic bridge (no LLM loop) and returns:
    - Recommended production ceiling (units/day and units/week)
    - Machines at high failure risk
    - Production lines at risk
    - Capacity risk flag and alert
    - Maintenance windows for the next 14 days
    - Fleet summary (OEE, availability, failure probabilities)

    Use this to establish the HARD capacity constraint before building the MPS.
    NEVER plan production above the capacity ceiling returned by this tool.

    Args:
        plant_id: Plant identifier (default PLANT-01)

    Returns:
        JSON string with capacity ceiling, at-risk machines, maintenance schedule.
    """
    from agents.machine_health_agent import MachineHealthAgent
    agent = MachineHealthAgent()
    envelope = agent.get_capacity_output(plant_id=plant_id)
    return json.dumps(envelope, indent=2)


# ══════════════════════════════════════════════════════════════════
# TOOL 4: Production Intelligence
# ══════════════════════════════════════════════════════════════════

@tool
def get_production_intelligence(product_id: str = "PROD-A", planning_weeks: int = 4) -> str:
    """
    Retrieve structured production intelligence from the Production Planning Agent.

    Calls the Production Planning Agent's programmatic bridge (no LLM loop) and returns:
    - Master Production Schedule (MPS) summary
    - Weekly production target and effective capacity
    - Active and down production lines
    - Overtime and contract manufacturing decisions
    - BOM-based material requirements for each component
    - Procurement alerts for at-risk components

    Use this AFTER get_machine_health_intelligence to get the production plan
    that respects the capacity ceiling. The material requirements from this tool
    feed directly into get_supplier_intelligence.

    Args:
        product_id: Product identifier (default PROD-A)
        planning_weeks: Number of weeks to plan for (default 4)

    Returns:
        JSON string with MPS, capacity, material requirements, and procurement alerts.
    """
    from agents.production_agent import ProductionPlanningAgent
    agent = ProductionPlanningAgent()
    envelope = agent.get_production_output(product_id=product_id, planning_weeks=planning_weeks)
    return json.dumps(envelope, indent=2)


# ══════════════════════════════════════════════════════════════════
# TOOL 5: Supplier Intelligence
# ══════════════════════════════════════════════════════════════════

@tool
def get_supplier_intelligence(weekly_units: float = 980.0, planning_weeks: int = 4) -> str:
    """
    Retrieve structured procurement intelligence from the Supplier & Procurement Agent.

    Calls the Supplier Agent's programmatic bridge (no LLM loop) and returns:
    - Complete purchase order package (all components, quantities, costs, delivery dates)
    - Supply chain resilience score (0-100)
    - High-risk and medium-risk components
    - Contract expiry risks
    - Escalation flag and reason
    - Open PO count and value

    Use this AFTER get_production_intelligence. Feed the weekly_units target from
    the Production Agent's output into this tool.

    Args:
        weekly_units: Weekly production target in units (default 980.0)
        planning_weeks: Number of weeks to plan for (default 4)

    Returns:
        JSON string with PO package, supply chain risk, and escalation status.
    """
    from agents.supplier_agent import SupplierProcurementAgent
    agent = SupplierProcurementAgent()
    envelope = agent.get_procurement_output(weekly_units=weekly_units, planning_weeks=planning_weeks)
    return json.dumps(envelope, indent=2)


# ══════════════════════════════════════════════════════════════════
# PRIVATE HELPER: Core synthesis logic (shared by tool + programmatic bridge)
# ══════════════════════════════════════════════════════════════════

def _compute_report(demand: dict, inventory: dict, machine: dict, production: dict, supplier: dict) -> dict:
    """
    Core synthesis logic. Takes 5 agent output dicts, returns the full report dict.
    Called by both synthesize_manufacturing_report tool and run_full_pipeline bridge.
    """

    # ── Domain Health Scoring ──────────────────────────────────────

    # Demand health (0-100): penalize anomalies and high-variance scenarios
    demand_score = 80
    if demand.get("anomaly_detected"):
        demand_score -= 20
    growth = demand.get("growth_rate_pct_per_week", 0)
    if growth > 3:
        demand_score -= 10  # rapid growth stresses capacity
    elif growth < -2:
        demand_score -= 15  # declining demand is a revenue risk
    demand_score = max(0, min(100, demand_score))

    trend = demand.get("trend_direction", "stable")
    if demand.get("anomaly_detected"):
        demand_status = "ALERT"
    elif trend == "increasing":
        demand_status = "WATCH"
    else:
        demand_status = "HEALTHY"

    # Inventory health (0-100): penalize stockout risk and low days of supply
    inventory_score = 100
    stockout_pct = inventory.get("stockout_probability_pct", 0)
    days_supply = inventory.get("days_of_supply", 0)
    weeks_below = inventory.get("weeks_below_safety_stock", 0)
    inventory_score -= stockout_pct * 1.5
    if days_supply < 7:
        inventory_score -= 30
    elif days_supply < 14:
        inventory_score -= 10
    inventory_score -= weeks_below * 10
    inventory_score = max(0, min(100, inventory_score))

    if inventory_score < 50:
        inventory_status = "CRITICAL"
    elif inventory_score < 70:
        inventory_status = "AT RISK"
    elif stockout_pct > 15:
        inventory_status = "WATCH"
    else:
        inventory_status = "HEALTHY"

    # Machine health (0-100): use capacity risk flag and at-risk machines
    machines_at_risk = len(machine.get("machines_at_high_risk", []))
    lines_at_risk = len(machine.get("production_lines_at_risk", []))
    capacity_risk = machine.get("capacity_risk_flag", False)
    machine_score = 100 - (machines_at_risk * 15) - (lines_at_risk * 10)
    if capacity_risk:
        machine_score -= 15
    machine_score = max(0, min(100, machine_score))

    if machine_score < 50:
        machine_status = "CRITICAL"
    elif machines_at_risk > 0 or capacity_risk:
        machine_status = "AT RISK"
    else:
        machine_status = "HEALTHY"

    # Production health (0-100): penalize overtime, down lines, capacity gap
    # lines_down is an integer count in the production envelope
    lines_down_raw = production.get("lines_down", 0)
    lines_down = lines_down_raw if isinstance(lines_down_raw, int) else len(lines_down_raw)
    overtime_required = production.get("overtime_required", False)
    weekly_target = production.get("weekly_production_target", 1)
    effective_cap = production.get("effective_capacity_weekly", 1)
    cap_utilization = min(weekly_target / effective_cap, 1.5) if effective_cap > 0 else 1.0

    production_score = 90
    production_score -= lines_down * 12
    if overtime_required:
        production_score -= 10
    if cap_utilization > 1.0:
        production_score -= 20  # demand exceeds capacity
    elif cap_utilization > 0.95:
        production_score -= 5
    production_score = max(0, min(100, production_score))

    if production_score < 50:
        production_status = "CRITICAL"
    elif lines_down > 1 or cap_utilization > 1.0:
        production_status = "AT RISK"
    elif lines_down > 0 or overtime_required:
        production_status = "WATCH"
    else:
        production_status = "HEALTHY"

    # Supply chain health (0-100): use resilience score from supplier agent
    supply_score = supplier.get("supply_chain_resilience_score", 70)
    high_risk_count = len(supplier.get("high_risk_components", []))
    if supplier.get("escalation_required"):
        supply_score -= 15
    supply_score -= high_risk_count * 5
    supply_score = max(0, min(100, supply_score))

    if supply_score < 50:
        supply_status = "CRITICAL"
    elif high_risk_count > 1 or supplier.get("escalation_required"):
        supply_status = "AT RISK"
    elif high_risk_count > 0:
        supply_status = "WATCH"
    else:
        supply_status = "HEALTHY"

    # Overall system health: weighted average
    overall_score = round(
        demand_score * 0.20
        + inventory_score * 0.20
        + machine_score * 0.25
        + production_score * 0.20
        + supply_score * 0.15
    )

    if overall_score >= 80:
        overall_status = "HEALTHY"
    elif overall_score >= 65:
        overall_status = "WATCH"
    elif overall_score >= 45:
        overall_status = "AT RISK"
    else:
        overall_status = "CRITICAL"

    # ── Cross-Domain Alerts ────────────────────────────────────────

    alerts = []

    # Demand spike + constrained capacity
    if demand.get("anomaly_detected") and (machines_at_risk > 0 or lines_down > 0):
        alerts.append({
            "severity": "CRITICAL",
            "domains": ["demand", "machine_health", "production"],
            "alert": "Demand anomaly detected while production capacity is constrained. "
                     f"{machines_at_risk} machine(s) at high risk. Risk of significant shortfall.",
        })

    # Growing demand + supply risk on key components
    if trend == "increasing" and high_risk_count > 0:
        risk_components = [c.get("component_id") for c in supplier.get("high_risk_components", [])]
        alerts.append({
            "severity": "HIGH",
            "domains": ["demand", "supply_chain"],
            "alert": f"Demand is trending upward but supply is fragile on critical components "
                     f"({', '.join(risk_components)}). Procurement must be accelerated.",
        })

    # Inventory below safety stock with stockout risk
    if not inventory.get("above_safety_stock") or stockout_pct > 20:
        alerts.append({
            "severity": "HIGH",
            "domains": ["inventory", "production"],
            "alert": f"Finished goods inventory at risk — stockout probability {stockout_pct}%. "
                     "Production must prioritize building safety stock buffer.",
        })

    # Capacity ceiling below demand target
    capacity_ceiling = machine.get("recommended_production_ceiling_units_per_week", 0)
    demand_base = demand.get("expected_weekly_demand", 0)
    if capacity_ceiling > 0 and demand_base > capacity_ceiling:
        gap = demand_base - capacity_ceiling
        alerts.append({
            "severity": "HIGH",
            "domains": ["machine_health", "production", "demand"],
            "alert": f"Machine health capacity ceiling ({capacity_ceiling} units/week) is BELOW "
                     f"base demand ({demand_base} units/week). Gap of {gap} units/week requires "
                     "overtime or contract manufacturing decisions.",
        })

    # Contract expiry
    contract_risks = supplier.get("contract_risks", [])
    urgent_contracts = [c for c in contract_risks if c.get("severity") in ("HIGH", "CRITICAL")]
    if urgent_contracts:
        names = [c.get("supplier_id", "") for c in urgent_contracts]
        alerts.append({
            "severity": "MEDIUM",
            "domains": ["supply_chain"],
            "alert": f"Supplier contract(s) expiring soon: {', '.join(names)}. "
                     "Renegotiation must begin immediately to avoid supply disruption.",
        })

    # Single-source components at high risk
    single_source = [
        c for c in supplier.get("high_risk_components", [])
        if "SINGLE SOURCE" in c.get("risk_flag", "")
    ]
    if single_source:
        ids = [c.get("component_id") for c in single_source]
        alerts.append({
            "severity": "MEDIUM",
            "domains": ["supply_chain"],
            "alert": f"Single-source components with elevated risk: {', '.join(ids)}. "
                     "Dual-source qualification should be initiated immediately.",
        })

    # Sort alerts by severity
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    alerts.sort(key=lambda x: severity_order.get(x["severity"], 99))

    # ── Priority Action Plan ───────────────────────────────────────

    actions = []
    action_id = 1

    if machines_at_risk > 0:
        actions.append({
            "priority": action_id,
            "urgency": "IMMEDIATE",
            "owner": "Maintenance",
            "action": f"Execute planned maintenance for {machines_at_risk} at-risk machine(s) "
                      f"({', '.join(machine.get('machines_at_high_risk', []))}) "
                      "before they cause unplanned downtime.",
            "impact": "Prevents production line stoppage and preserves capacity ceiling.",
        })
        action_id += 1

    if supplier.get("escalation_required"):
        actions.append({
            "priority": action_id,
            "urgency": "IMMEDIATE",
            "owner": "Procurement",
            "action": f"Address supply chain escalation: {supplier.get('escalation_reason', '')}. "
                      "Place dual-source orders for AM-300 and qualify alternative supplier.",
            "impact": "Prevents production stoppage due to component shortage.",
        })
        action_id += 1

    if inventory.get("reorder_needed_now"):
        actions.append({
            "priority": action_id,
            "urgency": "THIS WEEK",
            "owner": "Inventory / Procurement",
            "action": f"Trigger replenishment order immediately — stock is at or below reorder point "
                      f"({inventory.get('reorder_point_units')} units). "
                      f"Order {inventory.get('total_units_to_order')} units across planning horizon.",
            "impact": f"Reduces stockout probability from {stockout_pct}% to near zero.",
        })
        action_id += 1

    if overtime_required:
        actions.append({
            "priority": action_id,
            "urgency": "THIS WEEK",
            "owner": "Production Planning",
            "action": "Authorize overtime to close the capacity-demand gap. "
                      "Confirm shift supervisors and communicate extended hours to workforce.",
            "impact": f"Closes {weekly_target - effective_cap:.0f} unit/week capacity shortfall.",
        })
        action_id += 1

    if urgent_contracts:
        actions.append({
            "priority": action_id,
            "urgency": "THIS MONTH",
            "owner": "Procurement / Legal",
            "action": f"Initiate contract renegotiation with {', '.join([c.get('supplier_id') for c in urgent_contracts])}. "
                      "Contracts expire within 60-130 days.",
            "impact": "Prevents supply disruption from contract lapse and re-secures pricing.",
        })
        action_id += 1

    # ── Key Metrics Dashboard ──────────────────────────────────────

    dashboard = {
        "demand": {
            "weekly_demand_base": demand.get("expected_weekly_demand"),
            "trend": demand.get("trend_direction"),
            "growth_rate_pct_per_week": demand.get("growth_rate_pct_per_week"),
            "anomaly_detected": demand.get("anomaly_detected"),
        },
        "inventory": {
            "current_stock_units": inventory.get("current_stock"),
            "days_of_supply": inventory.get("days_of_supply"),
            "effective_days_of_supply": inventory.get("effective_days_of_supply"),
            "stockout_probability_pct": stockout_pct,
            "reorder_needed_now": inventory.get("reorder_needed_now"),
        },
        "machine_health": {
            "capacity_ceiling_units_per_week": machine.get("recommended_production_ceiling_units_per_week"),
            "machines_at_high_risk": machines_at_risk,
            "production_lines_at_risk": lines_at_risk,
            "capacity_risk_flag": capacity_risk,
        },
        "production": {
            "weekly_production_target": weekly_target,
            "effective_capacity_weekly": effective_cap,
            "capacity_utilization_pct": round(cap_utilization * 100, 1),
            "lines_down": production.get("lines_down", 0),
            "overtime_required": overtime_required,
        },
        "supply_chain": {
            "total_po_value": supplier.get("total_po_value"),
            "total_pos_generated": supplier.get("total_pos_generated"),
            "resilience_score": supply_score,
            "high_risk_components": high_risk_count,
            "escalation_required": supplier.get("escalation_required"),
        },
    }

    return {
        "report_type": "AMIS Full Manufacturing Intelligence Report",
        "system_health": {
            "overall_score": overall_score,
            "overall_status": overall_status,
            "domain_scores": {
                "demand": {"score": demand_score, "status": demand_status},
                "inventory": {"score": inventory_score, "status": inventory_status},
                "machine_health": {"score": machine_score, "status": machine_status},
                "production": {"score": production_score, "status": production_status},
                "supply_chain": {"score": supply_score, "status": supply_status},
            },
        },
        "cross_domain_alerts": alerts,
        "key_metrics": dashboard,
        "priority_actions": actions,
        "human_escalation_required": any(a["severity"] == "CRITICAL" for a in alerts) or supplier.get("escalation_required", False),
        "pipeline_summary": {
            "demand_target_weekly": demand.get("expected_weekly_demand"),
            "capacity_ceiling_weekly": machine.get("recommended_production_ceiling_units_per_week"),
            "planned_production_weekly": weekly_target,
            "inventory_days_of_supply": inventory.get("days_of_supply"),
            "total_procurement_value": supplier.get("total_po_value"),
            "supply_resilience_score": supply_score,
        },
    }


# ══════════════════════════════════════════════════════════════════
# TOOL 6: Manufacturing Report Synthesis
# ══════════════════════════════════════════════════════════════════

@tool
def synthesize_manufacturing_report(
    product_id: str = "PROD-A",
    plant_id: str = "PLANT-01",
    planning_weeks: int = 4,
) -> str:
    """
    Run the complete AMIS pipeline and produce a unified Manufacturing Intelligence Report.

    Calls all 5 specialist agents in sequence (Demand, Inventory, Machine Health,
    Production Planning, Supplier & Procurement) and synthesizes their outputs into:
    - Overall system health score (0-100) with domain breakdown
    - Cross-domain alerts (risks visible only by looking across all 5 agents)
    - Key metrics dashboard (demand vs capacity vs stock vs supply)
    - Priority action plan with owner and impact for each action
    - Human escalation flag for decisions requiring executive authorization

    Call this as the FINAL step of any full-pipeline analysis.
    You do NOT need to pass outputs from other tools — this runs all agents internally.

    Args:
        product_id: Product to analyze (default: PROD-A)
        plant_id: Plant to assess (default: PLANT-01)
        planning_weeks: Planning horizon in weeks (default: 4)

    Returns:
        JSON string with the complete Manufacturing Intelligence Report.
    """
    from agents.demand_agent import DemandForecastingAgent
    from agents.inventory_agent import InventoryManagementAgent
    from agents.machine_health_agent import MachineHealthAgent
    from agents.production_agent import ProductionPlanningAgent
    from agents.supplier_agent import SupplierProcurementAgent

    demand = DemandForecastingAgent().get_forecast_output(product_id)
    inventory = InventoryManagementAgent().get_inventory_output(product_id, planning_weeks)
    machine = MachineHealthAgent().get_capacity_output(plant_id)
    production = ProductionPlanningAgent().get_production_output(product_id, planning_weeks)
    weekly_target = float(production.get("weekly_production_target", 980.0))
    supplier = SupplierProcurementAgent().get_procurement_output(weekly_target, planning_weeks)

    report = _compute_report(demand, inventory, machine, production, supplier)
    return json.dumps(report, indent=2)
