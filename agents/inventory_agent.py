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

        current = inv["current_inventory"]
        health = inv["health_indicators"]

        return {
            "source_agent": "inventory_management",
            "product_id": product_id,
            "planning_horizon_weeks": planning_weeks,
            "current_stock": current["current_stock"],
            "safety_stock": current["safety_stock"],
            "days_of_supply": health["days_of_supply"],
            "effective_days_of_supply": health["effective_days_of_supply"],
            "above_safety_stock": health["above_safety_stock"],
            "incoming_pipeline_units": health["incoming_pipeline_units"],
            "warehouse_utilization_pct": current["warehouse_utilization_pct"],
            "stockout_probability_pct": risk["overall_stockout_probability_pct"],
            "reorder_needed_now": rop["reorder_needed_now"],
            "reorder_point_units": rop["reorder_point_units"],
            "days_until_rop": rop["days_until_rop_reached"],
            "total_units_to_order": plan["plan_summary"]["total_units_ordered"],
            "total_procurement_cost": plan["plan_summary"]["total_procurement_cost"],
            "min_projected_stock": plan["plan_summary"]["min_projected_stock"],
            "weeks_below_safety_stock": plan["plan_summary"]["weeks_below_safety_stock"],
            "stockout_events_last_12m": health["stockout_events_last_12_months"],
            "annual_stockout_cost": health["total_stockout_revenue_lost"],
        }
