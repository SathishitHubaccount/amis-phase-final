"""
AMIS Inventory Management Agent
Built with LangChain + Claude for autonomous inventory intelligence.
"""
import json
from agents.base_agent import BaseAgent
from prompts.inventory_prompts import INVENTORY_AGENT_SYSTEM_PROMPT
from tools import INVENTORY_TOOLS


class InventoryManagementAgent(BaseAgent):
    """
    Autonomous Inventory Management Agent.

    This agent:
    1. Monitors inventory positions and warehouse utilization
    2. Calculates reorder points and safety stock levels
    3. Simulates stockout risk via Monte Carlo methods
    4. Generates replenishment plans with supplier allocation
    5. Evaluates holding cost vs stockout risk tradeoffs
    6. Consumes demand forecasts from the Demand Agent (cross-agent input)
    """

    agent_name = "INVENTORY MANAGEMENT AGENT"

    def __init__(self):
        super().__init__(
            system_prompt=INVENTORY_AGENT_SYSTEM_PROMPT,
            tools=INVENTORY_TOOLS,
        )

    def get_inventory_output(self, product_id: str = "PROD-A", planning_weeks: int = 4) -> dict:
        """
        Generate a standardized inventory envelope for cross-agent consumption.
        Runs inventory tools programmatically and packages the result.

        This is used by the Orchestrator to get structured inventory data
        without going through the full LLM loop.
        """
        from tools.inventory import (
            get_inventory_status,
            calculate_reorder_point,
            simulate_stockout_risk,
            generate_replenishment_plan,
        )

        inv_json = get_inventory_status.invoke({"product_id": product_id})
        inv = json.loads(inv_json)

        rop_json = calculate_reorder_point.invoke({
            "product_id": product_id,
            "lead_time_days": 7,
        })
        rop = json.loads(rop_json)

        risk_json = simulate_stockout_risk.invoke({
            "product_id": product_id,
            "simulation_days": planning_weeks * 7,
        })
        risk = json.loads(risk_json)

        plan_json = generate_replenishment_plan.invoke({
            "product_id": product_id,
            "planning_weeks": planning_weeks,
        })
        plan = json.loads(plan_json)

        current = inv.get("current_inventory", {})
        health = inv.get("health_indicators", {})
        plan_summary = plan.get("plan_summary", {})

        return {
            "source_agent": "inventory_management",
            "product_id": product_id,
            "planning_horizon_weeks": planning_weeks,
            "current_stock": current.get("current_stock", 0),
            "safety_stock": current.get("safety_stock", 0),
            "days_of_supply": health.get("days_of_supply", 0),
            "effective_days_of_supply": health.get("effective_days_of_supply", 0),
            "above_safety_stock": health.get("above_safety_stock", False),
            "incoming_pipeline_units": health.get("incoming_pipeline_units", 0),
            "warehouse_utilization_pct": current.get("warehouse_utilization_pct", 0),
            "stockout_probability_pct": risk.get("overall_stockout_probability_pct", 0),
            "reorder_needed_now": rop.get("reorder_needed_now", False),
            "reorder_point_units": rop.get("reorder_point_units", 0),
            "days_until_rop": rop.get("days_until_rop_reached", 0),
            "total_units_to_order": plan_summary.get("total_units_ordered", 0),
            "total_procurement_cost": plan_summary.get("total_procurement_cost", 0),
            "min_projected_stock": plan_summary.get("min_projected_stock", 0),
            "weeks_below_safety_stock": plan_summary.get("weeks_below_safety_stock", 0),
            "stockout_events_last_12m": health.get("stockout_events_last_12_months", 0),
            "annual_stockout_cost": health.get("total_stockout_revenue_lost", 0),
        }
