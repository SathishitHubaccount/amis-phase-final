"""
AMIS Orchestrator Agent
Built with LangChain + Claude to conduct the full 5-agent manufacturing pipeline.
"""
import json
import time
from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage, SystemMessage
from prompts.orchestrator_prompts import ORCHESTRATOR_AGENT_SYSTEM_PROMPT
from prompts.demand_prompts import DEMAND_AGENT_SYSTEM_PROMPT
from prompts.inventory_prompts import INVENTORY_AGENT_SYSTEM_PROMPT
from prompts.machine_health_prompts import MACHINE_HEALTH_AGENT_SYSTEM_PROMPT
from prompts.production_prompts import PRODUCTION_AGENT_SYSTEM_PROMPT
from prompts.supplier_prompts import SUPPLIER_AGENT_SYSTEM_PROMPT
from tools import ORCHESTRATOR_TOOLS


class OrchestratorAgent(BaseAgent):
    """
    AMIS Orchestrator Agent — the conductor of the entire manufacturing pipeline.

    This agent:
    1. Runs all 5 specialist agents in sequence via their programmatic bridge methods
    2. Synthesizes demand, inventory, machine health, production, and supply outputs
    3. Identifies cross-domain risks invisible to individual agents
    4. Delivers a unified Manufacturing Intelligence Report with system health score
    5. Escalates critical issues requiring human authorization
    """

    agent_name = "ORCHESTRATOR AGENT"

    def __init__(self):
        super().__init__(
            system_prompt=ORCHESTRATOR_AGENT_SYSTEM_PROMPT,
            tools=ORCHESTRATOR_TOOLS,
        )

    def _llm_reason(self, system_prompt: str, data: dict, focus: str) -> str:
        """Call Claude with already-collected tool data for focused expert reasoning."""
        try:
            resp = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=(
                    f"The tools have already run. Here is their structured output:\n\n"
                    f"{json.dumps(data, indent=2)}\n\n"
                    f"{focus}\n\n"
                    f"Be concise — 2-3 sentences max. Focus only on the single most important "
                    f"insight and one clear action the operations team must take."
                )),
            ])
            content = resp.content
            if isinstance(content, list):
                return " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
            return str(content)
        except Exception as e:
            return f"(LLM reasoning unavailable: {e})"

    def run_full_pipeline(
        self,
        product_id: str = "PROD-A",
        plant_id: str = "PLANT-01",
        planning_weeks: int = 4,
        on_agent_complete=None,
    ) -> dict:
        """
        Run the complete AMIS pipeline.
        Each agent: (1) collects structured data via fast bridge tools,
                    (2) calls Claude for expert reasoning on that data.

        Pipeline order:
          Demand → Inventory → Machine Health → Production → Supplier → Synthesize
        """
        from tools.orchestrator import (
            get_demand_intelligence,
            get_inventory_intelligence,
            get_machine_health_intelligence,
            get_production_intelligence,
            get_supplier_intelligence,
        )

        pipeline_trace = []

        # ── 1. Demand ──────────────────────────────────────────────
        print("  [1/6] Running Demand Forecasting Agent...")
        _t0 = time.time()
        demand_json = get_demand_intelligence.invoke({"product_id": product_id})
        demand = json.loads(demand_json)
        print("  [1/6] Claude reasoning on demand data...")
        demand_reasoning = self._llm_reason(
            DEMAND_AGENT_SYSTEM_PROMPT,
            demand,
            "What is the most critical demand signal here, and what must the supply chain team do about it?",
        )
        _t1 = time.time()

        _scenarios = demand.get("scenarios", {})
        _base = _scenarios.get("base", _scenarios.get("Base", {}))
        _base_weekly = _base.get("weekly_avg", demand.get("expected_weekly_demand", 0))
        _growth = demand.get("growth_rate_pct_per_week", 0)
        _trend = demand.get("trend_direction", "unknown")
        if on_agent_complete:
            on_agent_complete("demand")
        pipeline_trace.append({
            "agent": "demand",
            "label": "Demand Forecasting Agent",
            "color": "blue",
            "duration_ms": round((_t1 - _t0) * 1000),
            "llm_reasoning": demand_reasoning,
            "tools_called": [
                {"order": 1, "name": "get_demand_data_summary",
                 "desc": f"Loaded demand history, inventory & market context for {product_id}"},
                {"order": 2, "name": "analyze_demand_trends",
                 "desc": f"Trend: {_trend} · Growth: {_growth:+.1f}%/week"},
                {"order": 3, "name": "simulate_demand_scenarios",
                 "desc": "Generated Optimistic / Base / Pessimistic weekly forecasts"},
                {"order": 4, "name": "detect_demand_anomalies",
                 "desc": f"Anomaly scan complete · Result: {'Spike detected ⚠' if demand.get('anomaly_detected') else 'No anomalies found'}"},
                {"order": 5, "name": "monte_carlo_profit_simulation",
                 "desc": "10,000-iteration Monte Carlo · Profit distribution across demand scenarios"},
                {"order": 6, "name": "compare_production_strategies",
                 "desc": "Compared MTS vs MTO vs hybrid strategies against demand profile"},
            ],
            "key_findings": [
                {"label": "Base Weekly Demand", "value": f"{int(_base_weekly):,} units"},
                {"label": "Trend Direction",    "value": str(_trend).title()},
                {"label": "Growth Rate",        "value": f"{_growth:+.1f}%/week"},
                {"label": "Anomaly Detected",   "value": "Yes ⚠" if demand.get("anomaly_detected") else "None"},
            ],
            "passed_to_next": {
                "agent": "Inventory Agent",
                "fields": [
                    f"expected_weekly_demand = {demand.get('expected_weekly_demand', '—')}",
                    f"demand_std_dev = {demand.get('demand_std_dev', '—')}",
                    f"forecast_horizon = {demand.get('forecast_horizon_weeks', planning_weeks)} weeks",
                ],
            },
        })

        # ── 2. Inventory ───────────────────────────────────────────
        print("  [2/6] Running Inventory Management Agent...")
        _t0 = time.time()
        inventory_json = get_inventory_intelligence.invoke({
            "product_id": product_id,
            "planning_weeks": planning_weeks,
        })
        inv = json.loads(inventory_json)
        print("  [2/6] Claude reasoning on inventory data...")
        inv_reasoning = self._llm_reason(
            INVENTORY_AGENT_SYSTEM_PROMPT,
            {**inv, "_demand_context": {"expected_weekly_demand": demand.get("expected_weekly_demand")}},
            "Given current stock levels and the demand forecast, what is the most urgent inventory action?",
        )
        _t1 = time.time()

        if on_agent_complete:
            on_agent_complete("inventory")
        pipeline_trace.append({
            "agent": "inventory",
            "label": "Inventory Management Agent",
            "color": "purple",
            "duration_ms": round((_t1 - _t0) * 1000),
            "llm_reasoning": inv_reasoning,
            "tools_called": [
                {"order": 1, "name": "get_inventory_status",
                 "desc": f"Current stock: {inv.get('current_stock', '—')} units · Safety stock: {inv.get('safety_stock', '—')} units"},
                {"order": 2, "name": "calculate_reorder_point",
                 "desc": f"Reorder point: {inv.get('reorder_point_units', '—')} units · Days until ROP: {inv.get('days_until_rop', '—')}"},
                {"order": 3, "name": "optimize_safety_stock",
                 "desc": f"Safety stock optimized to {inv.get('safety_stock', '—')} units balancing service level vs holding cost"},
                {"order": 4, "name": "simulate_stockout_risk",
                 "desc": f"Stockout probability: {inv.get('stockout_probability_pct', 0):.1f}% over {planning_weeks} weeks"},
                {"order": 5, "name": "evaluate_holding_costs",
                 "desc": f"Holding cost analysis · Total procurement: ${inv.get('total_procurement_cost', 0):,.0f}"},
                {"order": 6, "name": "generate_replenishment_plan",
                 "desc": f"Order {inv.get('total_units_to_order', '—')} units across {len(inv.get('replenishment_orders', [inv])) if isinstance(inv.get('replenishment_orders'), list) else 1} order(s)"},
            ],
            "key_findings": [
                {"label": "Current Stock",  "value": f"{inv.get('current_stock', '—'):,} units"},
                {"label": "Days of Supply", "value": f"{inv.get('days_of_supply', '—')} days"},
                {"label": "Reorder Now?",   "value": "Yes ⚠" if inv.get("reorder_needed_now") else "No"},
                {"label": "Stockout Risk",  "value": f"{inv.get('stockout_probability_pct', 0):.1f}%"},
            ],
            "passed_to_next": {
                "agent": "Machine Health Agent",
                "fields": [
                    f"stock_position = {inv.get('current_stock', '—')}",
                    f"reorder_needed = {inv.get('reorder_needed_now', False)}",
                    f"units_to_order = {inv.get('total_units_to_order', '—')}",
                ],
            },
        })

        # ── 3. Machine Health ──────────────────────────────────────
        print("  [3/6] Running Machine Health Agent...")
        _t0 = time.time()
        machine_json = get_machine_health_intelligence.invoke({"plant_id": plant_id})
        mach = json.loads(machine_json)
        print("  [3/6] Claude reasoning on machine health data...")
        mach_reasoning = self._llm_reason(
            MACHINE_HEALTH_AGENT_SYSTEM_PROMPT,
            mach,
            "What is the most critical machine health risk right now, and what maintenance action must be prioritized?",
        )
        _t1 = time.time()

        _ceiling_wk = mach.get("recommended_production_ceiling_units_per_week", "—")
        _at_risk = mach.get("machines_at_high_risk", [])
        _fleet = mach.get("fleet_summary", {})
        if on_agent_complete:
            on_agent_complete("machine")
        pipeline_trace.append({
            "agent": "machine",
            "label": "Machine Health Agent",
            "color": "amber",
            "duration_ms": round((_t1 - _t0) * 1000),
            "llm_reasoning": mach_reasoning,
            "tools_called": [
                {"order": 1, "name": "get_machine_fleet_status",
                 "desc": f"Scanned all machines · Fleet avg OEE: {_fleet.get('average_oee_pct', '—')}%"},
                {"order": 2, "name": "analyze_sensor_readings",
                 "desc": f"Parsed 24h sensor telemetry · Vibration, temp & pressure readings for {_fleet.get('total_machines', '—')} machines"},
                {"order": 3, "name": "predict_failure_risk",
                 "desc": f"{len(_at_risk)} machine(s) flagged at high failure risk within 7 days"},
                {"order": 4, "name": "calculate_oee",
                 "desc": f"OEE = Availability × Performance × Quality · Fleet avg: {_fleet.get('average_oee_pct', '—')}%"},
                {"order": 5, "name": "generate_maintenance_schedule",
                 "desc": f"Scheduled {len(mach.get('maintenance_windows', []))} maintenance window(s) to minimize production downtime"},
                {"order": 6, "name": "assess_production_capacity_impact",
                 "desc": f"Capacity ceiling set to {_ceiling_wk:,} units/week after risk buffer" if isinstance(_ceiling_wk, (int, float)) else "Assessed capacity constraints from machine health"},
            ],
            "key_findings": [
                {"label": "Capacity Ceiling",   "value": f"{_ceiling_wk:,} units/week" if isinstance(_ceiling_wk, (int, float)) else str(_ceiling_wk)},
                {"label": "Fleet Avg OEE",      "value": f"{_fleet.get('average_oee_pct', '—')}%"},
                {"label": "High-Risk Machines", "value": str(len(_at_risk)) + (" ⚠" if _at_risk else "")},
                {"label": "Capacity Risk",      "value": "Yes ⚠" if mach.get("capacity_risk_flag") else "No"},
            ],
            "passed_to_next": {
                "agent": "Production Agent",
                "fields": [
                    f"capacity_ceiling_weekly = {_ceiling_wk}",
                    f"machines_at_risk = {len(_at_risk)}",
                    f"capacity_risk_flag = {mach.get('capacity_risk_flag', False)}",
                ],
            },
        })

        # ── 4. Production ──────────────────────────────────────────
        print("  [4/6] Running Production Planning Agent...")
        _t0 = time.time()
        production_json = get_production_intelligence.invoke({
            "product_id": product_id,
            "planning_weeks": planning_weeks,
        })
        production = json.loads(production_json)
        print("  [4/6] Claude reasoning on production data...")
        prod_reasoning = self._llm_reason(
            PRODUCTION_AGENT_SYSTEM_PROMPT,
            {**production, "_context": {
                "demand_weekly": demand.get("expected_weekly_demand"),
                "capacity_ceiling": _ceiling_wk,
            }},
            "Given the capacity constraints and demand target, what is the most important production scheduling decision?",
        )
        _t1 = time.time()

        weekly_target = float(production.get("weekly_production_target", 980.0))
        _eff_cap = production.get("effective_capacity_weekly", "—")
        _overtime = production.get("overtime_required", False)
        if on_agent_complete:
            on_agent_complete("production")
        pipeline_trace.append({
            "agent": "production",
            "label": "Production Planning Agent",
            "color": "emerald",
            "duration_ms": round((_t1 - _t0) * 1000),
            "llm_reasoning": prod_reasoning,
            "tools_called": [
                {"order": 1, "name": "get_production_context",
                 "desc": f"Loaded machine capacity, inventory, shift config for {product_id}"},
                {"order": 2, "name": "build_master_production_schedule",
                 "desc": f"Built {planning_weeks}-week MPS · Target: {int(weekly_target):,} units/week"},
                {"order": 3, "name": "analyze_production_bottlenecks",
                 "desc": f"Identified bottleneck stations constraining throughput to {_eff_cap} units/week"},
                {"order": 4, "name": "evaluate_capacity_gap",
                 "desc": f"Gap analysis complete · Overtime needed: {'Yes ⚠' if _overtime else 'No'}"},
                {"order": 5, "name": "optimize_production_mix",
                 "desc": f"Optimized product mix across {production.get('lines_active', '—')} active line(s) for max throughput"},
                {"order": 6, "name": "generate_production_requirements",
                 "desc": f"Exploded BOM into {len(production.get('material_requirements', []))} component requirements"},
            ],
            "key_findings": [
                {"label": "Weekly Target",      "value": f"{int(weekly_target):,} units"},
                {"label": "Effective Capacity", "value": f"{_eff_cap} units/week"},
                {"label": "Lines Active",       "value": str(production.get("lines_active", "—"))},
                {"label": "Overtime Required",  "value": "Yes" if _overtime else "No"},
            ],
            "passed_to_next": {
                "agent": "Supplier Agent",
                "fields": [
                    f"weekly_production_target = {int(weekly_target)}",
                    f"planning_weeks = {planning_weeks}",
                    f"material_requirements = {len(production.get('material_requirements', []))} components",
                ],
            },
        })

        # ── 5. Supplier ────────────────────────────────────────────
        print("  [5/6] Running Supplier & Procurement Agent...")
        _t0 = time.time()
        supplier_json = get_supplier_intelligence.invoke({
            "weekly_units": weekly_target,
            "planning_weeks": planning_weeks,
        })
        sup = json.loads(supplier_json)
        print("  [5/6] Claude reasoning on supplier data...")
        sup_reasoning = self._llm_reason(
            SUPPLIER_AGENT_SYSTEM_PROMPT,
            sup,
            "What is the biggest supply chain risk and what procurement action must be taken immediately?",
        )
        _t1 = time.time()

        if on_agent_complete:
            on_agent_complete("supplier")
        pipeline_trace.append({
            "agent": "supplier",
            "label": "Supplier Procurement Agent",
            "color": "rose",
            "duration_ms": round((_t1 - _t0) * 1000),
            "llm_reasoning": sup_reasoning,
            "tools_called": [
                {"order": 1, "name": "get_procurement_context",
                 "desc": f"Loaded supplier scorecards, open POs ({sup.get('open_po_count', '—')} open)"},
                {"order": 2, "name": "evaluate_supplier_options",
                 "desc": f"Ranked {len(sup.get('purchase_orders', []))} supplier options by score: quality, lead time, cost"},
                {"order": 3, "name": "generate_purchase_orders",
                 "desc": f"Generated {sup.get('total_pos_generated', '—')} POs · Total value: ${sup.get('total_po_value', 0):,.0f}"},
                {"order": 4, "name": "assess_supply_chain_risk",
                 "desc": f"Resilience score: {sup.get('supply_chain_resilience_score', '—')}/100 · Rating: {sup.get('resilience_rating', '—')}"},
                {"order": 5, "name": "simulate_delivery_risk",
                 "desc": f"Simulated late delivery scenarios · {len(sup.get('urgent_items', []))} urgent item(s) flagged"},
                {"order": 6, "name": "optimize_supplier_allocation",
                 "desc": "Allocated orders across preferred suppliers to minimize cost & risk"},
            ],
            "key_findings": [
                {"label": "POs Generated",    "value": str(sup.get("total_pos_generated", "—"))},
                {"label": "Total PO Value",   "value": f"${sup.get('total_po_value', 0):,.0f}"},
                {"label": "Resilience Score", "value": f"{sup.get('supply_chain_resilience_score', '—')} / 100"},
                {"label": "Escalation Needed","value": "Yes ⚠" if sup.get("escalation_required") else "No"},
            ],
            "passed_to_next": {
                "agent": "Orchestrator Synthesis",
                "fields": [
                    f"total_po_value = ${sup.get('total_po_value', 0):,.0f}",
                    f"resilience_score = {sup.get('supply_chain_resilience_score', '—')}",
                    f"urgent_items = {len(sup.get('urgent_items', []))}",
                ],
            },
        })

        # ── 6. Synthesis ───────────────────────────────────────────
        print("  [6/6] Synthesizing Manufacturing Intelligence Report...")
        from tools.orchestrator import _compute_report
        report = _compute_report(demand, inv, mach, production, sup)

        return {
            "source_agent": "orchestrator",
            "product_id": product_id,
            "plant_id": plant_id,
            "planning_horizon_weeks": planning_weeks,
            "generated_at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
            "pipeline_outputs": {
                "demand": demand,
                "inventory": inv,
                "machine_health": mach,
                "production": production,
                "supplier": sup,
            },
            "pipeline_trace": pipeline_trace,
            "manufacturing_intelligence_report": report,
        }
