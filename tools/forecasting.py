"""
Demand Forecasting Tools
These are the ALGORITHMS the agent uses as tools.
The LLM decides WHEN to call them, INTERPRETS the results, and REASONS about them.

NOTE: Historical data now comes from DATABASE (not generated on-the-fly).
This ensures repeatability, traceability, and SQL validation.
"""
import json
import math
import random
from langchain_core.tools import tool

# Import database query functions (NEW - replaces sample_data functions)
from data.database_queries import get_historical_demand, get_market_context

# All data now comes from database
from data.database_queries import get_product_info


@tool
def simulate_demand_scenarios(product_id: str = "PROD-A", horizon_weeks: int = 4) -> str:
    """
    Generate multiple demand scenarios (Optimistic, Base, Pessimistic) with probability weights.
    Use this when you need to forecast future demand with uncertainty quantification.
    Returns scenarios with weekly breakdown, probability weights, and confidence intervals.
    
    Args:
        product_id: The product ID to forecast for (default: PROD-A)
        horizon_weeks: Number of weeks to forecast ahead (default: 4)
    """
    historical = get_historical_demand(product_id)
    
    # Calculate trend from historical data
    demands = [w["demand_units"] for w in historical]
    n = len(demands)
    avg_demand = sum(demands) / n
    recent_avg = sum(demands[-4:]) / 4
    trend_pct = ((recent_avg - avg_demand) / avg_demand) * 100
    
    # Detect if there's a recent spike
    last_week = demands[-1]
    spike_detected = last_week > avg_demand * 1.3
    
    # Calculate volatility (standard deviation)
    variance = sum((d - avg_demand) ** 2 for d in demands) / n
    std_dev = math.sqrt(variance)
    volatility_pct = (std_dev / avg_demand) * 100
    
    # Generate scenarios
    scenarios = {
        "product_id": product_id,
        "forecast_horizon_weeks": horizon_weeks,
        "historical_summary": {
            "weeks_analyzed": n,
            "average_weekly_demand": round(avg_demand),
            "recent_4week_average": round(recent_avg),
            "trend": f"{'Upward' if trend_pct > 2 else 'Downward' if trend_pct < -2 else 'Stable'} ({trend_pct:+.1f}%)",
            "volatility": f"{volatility_pct:.1f}%",
            "spike_detected": spike_detected,
            "spike_week_demand": last_week if spike_detected else None,
        },
        "scenarios": {
            "optimistic": {
                "probability_weight": 0.20,
                "description": "Strong demand growth driven by market expansion and viral momentum",
                "weekly_forecast": [
                    round(recent_avg * (1.15 + 0.03 * w) + random.gauss(0, 30))
                    for w in range(horizon_weeks)
                ],
                "total_units": 0,  # calculated below
                "assumptions": [
                    "Viral social media momentum continues (+15% boost)",
                    "Trade show generates new enterprise contracts",
                    "Competitor supply issues persist",
                ],
            },
            "base": {
                "probability_weight": 0.55,
                "description": "Steady growth aligned with recent trend, viral spike normalizes",
                "weekly_forecast": [
                    round(recent_avg * (1.0 + 0.01 * w) + random.gauss(0, 25))
                    for w in range(horizon_weeks)
                ],
                "total_units": 0,
                "assumptions": [
                    "Demand returns to trend after temporary spike",
                    "Normal seasonal patterns hold",
                    "No major market disruptions",
                ],
            },
            "pessimistic": {
                "probability_weight": 0.25,
                "description": "Demand contraction due to market headwinds",
                "weekly_forecast": [
                    round(recent_avg * (0.82 - 0.02 * w) + random.gauss(0, 20))
                    for w in range(horizon_weeks)
                ],
                "total_units": 0,
                "assumptions": [
                    "Raw material price increases passed to customers",
                    "Competitor's new product captures market share",
                    "Economic slowdown reduces enterprise orders",
                ],
            },
        },
        "confidence_interval_95pct": {
            "lower": round(recent_avg * 0.75),
            "upper": round(recent_avg * 1.25),
        },
    }
    
    # Calculate totals
    for scenario in scenarios["scenarios"].values():
        scenario["total_units"] = sum(scenario["weekly_forecast"])
    
    # Expected weighted demand
    expected = sum(
        s["total_units"] * s["probability_weight"]
        for s in scenarios["scenarios"].values()
    )
    scenarios["expected_weighted_demand"] = round(expected)
    
    return json.dumps(scenarios, indent=2)


@tool
def analyze_demand_trends(product_id: str = "PROD-A") -> str:
    """
    Perform detailed trend analysis on historical demand data.
    Use this to understand demand patterns, seasonality, and growth rates.
    Returns trend direction, seasonality index, growth rate, and pattern analysis.
    
    Args:
        product_id: The product ID to analyze (default: PROD-A)
    """
    historical = get_historical_demand(product_id)
    demands = [w["demand_units"] for w in historical]
    prices = [w["avg_price"] for w in historical]
    
    n = len(demands)
    avg = sum(demands) / n
    
    # Simple linear regression for trend
    x_mean = (n - 1) / 2
    y_mean = avg
    numerator = sum((i - x_mean) * (demands[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator != 0 else 0
    
    # Week-over-week changes
    wow_changes = [
        round(((demands[i] - demands[i-1]) / demands[i-1]) * 100, 1)
        for i in range(1, n)
    ]
    
    # Detect anomalies (>2 std dev from mean)
    std_dev = math.sqrt(sum((d - avg) ** 2 for d in demands) / n)
    anomalies = [
        {
            "week": historical[i]["week"],
            "demand": demands[i],
            "deviation_from_avg": round(demands[i] - avg),
            "z_score": round((demands[i] - avg) / std_dev, 2) if std_dev > 0 else 0,
            "had_promotion": historical[i]["promotions_active"],
        }
        for i in range(n)
        if abs(demands[i] - avg) > 1.5 * std_dev
    ]
    
    # Price-demand correlation (simple)
    price_avg = sum(prices) / n
    cov = sum((demands[i] - avg) * (prices[i] - price_avg) for i in range(n)) / n
    price_std = math.sqrt(sum((p - price_avg) ** 2 for p in prices) / n)
    correlation = round(cov / (std_dev * price_std), 3) if std_dev * price_std > 0 else 0
    
    result = {
        "product_id": product_id,
        "trend_analysis": {
            "direction": "Upward" if slope > 5 else "Downward" if slope < -5 else "Stable",
            "slope_units_per_week": round(slope, 1),
            "growth_rate_pct_per_week": round((slope / avg) * 100, 2),
        },
        "demand_statistics": {
            "mean": round(avg),
            "std_deviation": round(std_dev),
            "min": min(demands),
            "max": max(demands),
            "coefficient_of_variation": round((std_dev / avg) * 100, 1),
        },
        "week_over_week_changes_pct": wow_changes,
        "anomalies_detected": anomalies,
        "price_demand_correlation": {
            "correlation_coefficient": correlation,
            "interpretation": (
                "Strong negative (higher price = lower demand)"
                if correlation < -0.5
                else "Weak/no correlation"
                if abs(correlation) < 0.3
                else "Moderate positive"
                if correlation > 0.3
                else "Moderate negative"
            ),
        },
        "market_context": get_market_context(),
    }
    
    return json.dumps(result, indent=2)


@tool
def get_demand_data_summary(product_id: str = "PROD-A") -> str:
    """
    Get a complete summary of all available demand data including historical demand,
    current inventory, market context, and production capacity.
    Use this as the FIRST tool call to understand the full picture before analysis.

    Args:
        product_id: The product ID to get data for (default: PROD-A)
    """
    # Import database functions
    from data.database_queries import get_historical_demand, get_market_context

    # Import from database queries
    from data.database_queries import (
        get_current_inventory,
        get_production_capacity,
        get_product_info,
    )
    
    historical = get_historical_demand(product_id)
    
    summary = {
        "product_info": get_product_info(product_id),
        "historical_demand_last_12_weeks": historical,
        "current_inventory": get_current_inventory(product_id),
        "market_context": get_market_context(),
        "production_capacity": get_production_capacity(),
    }
    
    return json.dumps(summary, indent=2, default=str)
