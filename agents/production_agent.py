"""
AMIS Production Planning Agent
Built with LangChain + Claude for autonomous production scheduling intelligence.
"""
import json
from agents.base_agent import BaseAgent
from prompts.production_prompts import PRODUCTION_AGENT_SYSTEM_PROMPT
from tools import PRODUCTION_TOOLS


class ProductionPlanningAgent(BaseAgent):
    """
    Autonomous Production Planning Agent.

    This agent:
    1. Consolidates inputs from Demand, Inventory, and Machine Health agents
    2. Identifies the system constraint (bottleneck line/machine)
    3. Evaluates the gap between demand and available capacity
    4. Builds the Master Production Schedule (MPS) week-by-week
    5. Decides on overtime and contract manufacturing
    6. Generates raw material requirements for the Supplier Agent
    """

    agent_name = "PRODUCTION PLANNING AGENT"

    def __init__(self):
        super().__init__(
            system_prompt=PRODUCTION_AGENT_SYSTEM_PROMPT,
            tools=PRODUCTION_TOOLS,
        )

    def get_production_output(self, product_id: str = "PROD-A", planning_weeks: int = 4) -> dict:
        """
        Generate a standardized production output envelope for the Supplier Agent.
        Runs production tools programmatically and packages the result.

        This is used by the Supplier Agent (and Orchestrator) to get structured
        material requirements without going through the full LLM loop.
        """
        from tools.production import (
            get_production_context,
            build_master_production_schedule,
            generate_production_requirements,
        )

        # Get current context
        context_json = get_production_context.invoke({"product_id": product_id})
        context = json.loads(context_json)

        # Build MPS with current defaults (Line 4 down, MCH-002 maintenance Week 1)
        mps_json = build_master_production_schedule.invoke({
            "planning_weeks": planning_weeks,
            "target_weekly_output": 1050.0,
            "line4_returns_week": 1,
            "mch002_maintenance_week": 1,
        })
        mps = json.loads(mps_json)

        # Get weekly production target from MPS summary
        weekly_target = round(
            mps["mps_summary"]["total_planned_units"] / planning_weeks
        )

        # Generate material requirements
        req_json = generate_production_requirements.invoke({
            "weekly_units_to_produce": weekly_target,
            "planning_weeks": planning_weeks,
        })
        requirements = json.loads(req_json)

        return {
            "source_agent": "production_planning",
            "product_id": product_id,
            "planning_horizon_weeks": planning_weeks,
            "mps_summary": mps["mps_summary"],
            "weekly_production_target": weekly_target,
            "effective_capacity_weekly": context["capacity_summary"]["current_effective_units_per_week"],
            "lines_active": context["capacity_summary"]["active_lines"],
            "lines_down": context["capacity_summary"]["down_lines"],
            "overtime_required": mps["mps_summary"]["total_overtime_and_contract_cost"] > 0,
            "material_requirements": requirements.get("material_requirements", []),
            "procurement_alerts": (requirements.get("procurement_summary") or {}).get("component_alerts", []),
            "cross_agent_output_for_supplier": requirements.get("cross_agent_output_for_supplier", {}),
        }
