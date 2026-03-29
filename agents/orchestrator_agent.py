"""
AMIS Orchestrator Agent
Built with LangChain + Claude to conduct the full 5-agent manufacturing pipeline.
"""
import json
from agents.base_agent import BaseAgent
from prompts.orchestrator_prompts import ORCHESTRATOR_AGENT_SYSTEM_PROMPT
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

    def run_full_pipeline(
        self,
        product_id: str = "PROD-A",
        plant_id: str = "PLANT-01",
        planning_weeks: int = 4,
    ) -> dict:
        """
        Run the complete AMIS pipeline programmatically (no LLM loop).
        Returns the full Manufacturing Intelligence Report as a structured dict.

        This is the Orchestrator's bridge method — used by external callers or
        for testing the full pipeline without the LLM reasoning layer.

        Pipeline order:
          Demand → Inventory → Machine Health → Production → Supplier → Synthesize
        """
        from tools.orchestrator import (
            get_demand_intelligence,
            get_inventory_intelligence,
            get_machine_health_intelligence,
            get_production_intelligence,
            get_supplier_intelligence,
            synthesize_manufacturing_report,
        )

        print("  [1/6] Running Demand Forecasting Agent...")
        demand_json = get_demand_intelligence.invoke({"product_id": product_id})

        print("  [2/6] Running Inventory Management Agent...")
        inventory_json = get_inventory_intelligence.invoke({
            "product_id": product_id,
            "planning_weeks": planning_weeks,
        })

        print("  [3/6] Running Machine Health Agent...")
        machine_json = get_machine_health_intelligence.invoke({"plant_id": plant_id})

        print("  [4/6] Running Production Planning Agent...")
        production_json = get_production_intelligence.invoke({
            "product_id": product_id,
            "planning_weeks": planning_weeks,
        })

        # Extract weekly target from production output for supplier
        production = json.loads(production_json)
        weekly_target = float(production.get("weekly_production_target", 980.0))

        print("  [5/6] Running Supplier & Procurement Agent...")
        supplier_json = get_supplier_intelligence.invoke({
            "weekly_units": weekly_target,
            "planning_weeks": planning_weeks,
        })

        print("  [6/6] Synthesizing Manufacturing Intelligence Report...")
        report_json = synthesize_manufacturing_report.invoke({
            "product_id": product_id,
            "plant_id": plant_id,
            "planning_weeks": planning_weeks,
        })

        report = json.loads(report_json)

        return {
            "source_agent": "orchestrator",
            "product_id": product_id,
            "plant_id": plant_id,
            "planning_horizon_weeks": planning_weeks,
            "pipeline_outputs": {
                "demand": json.loads(demand_json),
                "inventory": json.loads(inventory_json),
                "machine_health": json.loads(machine_json),
                "production": json.loads(production_json),
                "supplier": json.loads(supplier_json),
            },
            "manufacturing_intelligence_report": report,
        }
