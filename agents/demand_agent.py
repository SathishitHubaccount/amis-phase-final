"""
AMIS Demand Forecasting Agent
Built with LangChain + Claude for autonomous demand intelligence.
"""
import json
from datetime import datetime
from agents.base_agent import BaseAgent
from prompts.demand_prompts import DEMAND_AGENT_SYSTEM_PROMPT
from tools import DEMAND_TOOLS


class DemandForecastingAgent(BaseAgent):
    """
    Autonomous Demand Forecasting Agent.

    This agent:
    1. Receives natural language requests
    2. Decides which tools to call (and in what order)
    3. Interprets tool results with business context
    4. Generates recommendations with reasoning
    5. Produces cross-agent alerts
    """

    agent_name = "DEMAND FORECASTING AGENT"

    def __init__(self):
        super().__init__(
            system_prompt=DEMAND_AGENT_SYSTEM_PROMPT,
            tools=DEMAND_TOOLS,
        )

    def get_forecast_output(self, product_id: str = "PROD-A") -> dict:
        """
        Generate a standardized forecast envelope for cross-agent consumption.
        Runs forecasting tools programmatically and packages the result.

        This is used by the Inventory Agent (and future agents) to get
        structured demand data without going through the full LLM loop.
        """
        from tools.forecasting import simulate_demand_scenarios, analyze_demand_trends

        scenarios_json = simulate_demand_scenarios.invoke({
            "product_id": product_id,
            "horizon_weeks": 4,
        })
        trends_json = analyze_demand_trends.invoke({
            "product_id": product_id,
        })

        scenarios = json.loads(scenarios_json)
        trends = json.loads(trends_json)

        horizon = scenarios["forecast_horizon_weeks"]

        return {
            "source_agent": "demand_forecasting",
            "timestamp": datetime.now().isoformat(),
            "product_id": product_id,
            "forecast_horizon_weeks": horizon,
            "expected_weekly_demand": scenarios["expected_weighted_demand"] // horizon,
            "demand_std_dev": trends["demand_statistics"]["std_deviation"],
            "scenarios": {
                name: {
                    "weekly_avg": s["total_units"] // horizon,
                    "probability": s["probability_weight"],
                }
                for name, s in scenarios["scenarios"].items()
            },
            "confidence_interval_95pct": scenarios["confidence_interval_95pct"],
            "trend_direction": trends["trend_analysis"]["direction"],
            "growth_rate_pct_per_week": trends["trend_analysis"]["growth_rate_pct_per_week"],
            "anomaly_detected": scenarios["historical_summary"]["spike_detected"],
            "recommended_strategy": "balanced",
        }
