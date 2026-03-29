"""
AMIS Machine Health Agent
Built with LangChain + Claude for autonomous machine health intelligence.
"""
import json
from agents.base_agent import BaseAgent
from prompts.machine_health_prompts import MACHINE_HEALTH_AGENT_SYSTEM_PROMPT
from tools import MACHINE_HEALTH_TOOLS


class MachineHealthAgent(BaseAgent):
    """
    Autonomous Machine Health Agent.

    This agent:
    1. Monitors the full machine fleet and flags at-risk equipment
    2. Analyzes sensor readings (vibration, temperature, pressure, RPM) for anomalies
    3. Predicts failure probability using MTBF + real-time sensor degradation
    4. Calculates OEE (Overall Equipment Effectiveness) with trend analysis
    5. Generates optimized maintenance schedules minimizing production disruption
    6. Delivers a safe production capacity ceiling to the Production Planning Agent
    """

    agent_name = "MACHINE HEALTH AGENT"

    def __init__(self):
        super().__init__(
            system_prompt=MACHINE_HEALTH_AGENT_SYSTEM_PROMPT,
            tools=MACHINE_HEALTH_TOOLS,
        )

    def get_capacity_output(self, plant_id: str = "PLANT-01") -> dict:
        """
        Generate a standardized capacity envelope for the Production Planning Agent.
        Runs capacity assessment programmatically and packages the result.

        This is used by the Production Planning Agent (and Orchestrator) to get
        the safe production ceiling without going through the full LLM loop.
        """
        from tools.machine_health import (
            assess_production_capacity_impact,
            generate_maintenance_schedule,
        )

        capacity_json = assess_production_capacity_impact.invoke({"include_risk_buffer": True})
        capacity = json.loads(capacity_json)

        schedule_json = generate_maintenance_schedule.invoke({
            "planning_horizon_days": 14,
            "production_demand_weekly": 1050.0,
        })
        schedule = json.loads(schedule_json)

        cross_agent = capacity["cross_agent_output_for_production_planning"]
        maintenance_windows = schedule["cross_agent_alert_for_production"]["windows"]

        return {
            "source_agent": "machine_health",
            "plant_id": plant_id,
            "recommended_production_ceiling_units_per_day": cross_agent["recommended_production_ceiling_units_per_day"],
            "recommended_production_ceiling_units_per_week": cross_agent["recommended_production_ceiling_units_per_week"],
            "max_safe_if_no_failures_units_per_week": cross_agent["max_safe_if_no_failures_units_per_day"] * 5,
            "machines_at_high_risk": cross_agent["machines_at_high_risk"],
            "production_lines_at_risk": cross_agent["production_lines_at_risk"],
            "capacity_risk_flag": cross_agent["capacity_risk_flag"],
            "alert": cross_agent["alert"],
            "maintenance_windows": maintenance_windows,
            "fleet_summary": capacity["capacity_assessment"],
        }
