"""
AMIS Supplier & Procurement Agent
Built with LangChain + Claude for autonomous supply chain intelligence.
"""
import json
from agents.base_agent import BaseAgent
from prompts.supplier_prompts import SUPPLIER_AGENT_SYSTEM_PROMPT
from tools import SUPPLIER_TOOLS


class SupplierProcurementAgent(BaseAgent):
    """
    Autonomous Supplier & Procurement Agent.

    This agent:
    1. Receives the production plan from the Production Planning Agent
    2. Evaluates all supplier options per component (cost, reliability, quality)
    3. Assesses supply chain risk (single-source, geographic, contract expiry)
    4. Simulates on-time delivery probability via Monte Carlo
    5. Optimizes dual-source splits for high-risk components
    6. Generates a complete purchase order package for execution
    """

    agent_name = "SUPPLIER & PROCUREMENT AGENT"

    def __init__(self):
        super().__init__(
            system_prompt=SUPPLIER_AGENT_SYSTEM_PROMPT,
            tools=SUPPLIER_TOOLS,
        )

    def get_procurement_output(self, weekly_units: float = 980.0, planning_weeks: int = 4) -> dict:
        """
        Generate a standardized procurement output envelope for the Orchestrator.
        Runs procurement tools programmatically and packages the result.

        This is used by the Orchestrator to get structured purchase order data
        and supply chain risk status without going through the full LLM loop.
        """
        from tools.supplier import (
            get_procurement_context,
            generate_purchase_orders,
            assess_supply_chain_risk,
        )

        # Get full procurement context
        context_json = get_procurement_context.invoke({
            "weekly_production_target": weekly_units,
            "planning_weeks": planning_weeks,
        })
        context = json.loads(context_json)

        # Generate purchase orders for the production plan
        po_json = generate_purchase_orders.invoke({
            "weekly_units_to_produce": weekly_units,
            "planning_weeks": planning_weeks,
        })
        po_data = json.loads(po_json)

        # Run supply chain risk assessment
        risk_json = assess_supply_chain_risk.invoke({})
        risk_data = json.loads(risk_json)

        cross_agent = po_data["cross_agent_output_for_orchestrator"]
        risk_overview = risk_data["supply_chain_risk_assessment"]
        open_pos = context["open_purchase_orders"]

        return {
            "source_agent": "supplier_procurement",
            "planning_horizon_weeks": planning_weeks,
            "weekly_production_target": weekly_units,
            "total_po_value": po_data["po_summary"]["total_procurement_value"],
            "total_pos_generated": po_data["po_summary"]["total_pos_to_place"],
            "purchase_orders": po_data["purchase_orders"],
            "urgent_items": cross_agent["urgent_items"],
            "earliest_delivery_days": cross_agent["earliest_delivery_days"],
            "latest_delivery_days": cross_agent["latest_delivery_days"],
            "supply_chain_resilience_score": risk_overview["overall_resilience_score"],
            "resilience_rating": risk_overview["resilience_rating"],
            "high_risk_components": risk_data["high_risk_components"],
            "medium_risk_components": risk_data["medium_risk_components"],
            "contract_risks": risk_data["contract_risks"],
            "escalation_required": risk_data["escalation_to_orchestrator"]["requires_escalation"],
            "escalation_reason": risk_data["escalation_to_orchestrator"]["reason"],
            "open_po_count": open_pos["total_open_pos"],
            "open_po_value": open_pos["total_open_value"],
        }
