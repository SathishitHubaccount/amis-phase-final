"""
Anomaly Detection Tools
Detect unusual demand patterns and provide context for diagnosis.
"""
import json
import math
from langchain_core.tools import tool
from data.database_queries import get_historical_demand, get_market_context


@tool
def detect_demand_anomalies(product_id: str = "PROD-A", sensitivity: float = 1.5) -> str:
    """
    Detect anomalies in recent demand data using statistical methods.
    Flags any weeks where demand deviates significantly from expected patterns.
    
    Use this when you suspect unusual demand behavior or as part of routine monitoring.
    The LLM should INTERPRET the anomalies with market context to provide root cause hypotheses.
    
    Args:
        product_id: Product to analyze (default: PROD-A)
        sensitivity: Z-score threshold for flagging anomalies (default: 1.5, lower = more sensitive)
    """
    historical = get_historical_demand(product_id)

    if not historical:
        from data.sample_data import get_historical_demand as _fallback
        historical = _fallback(product_id)

    demands = [w["demand_units"] for w in historical]
    market = get_market_context()

    n = len(demands)
    if n == 0:
        return json.dumps({"product_id": product_id, "anomalies_found": 0, "anomalies": [], "note": "No historical data available."})
    avg = sum(demands) / n
    std = math.sqrt(sum((d - avg) ** 2 for d in demands) / n)
    
    anomalies = []
    for i, week in enumerate(historical):
        z_score = (week["demand_units"] - avg) / std if std > 0 else 0
        
        if abs(z_score) > sensitivity:
            # Calculate context
            prev_demand = demands[i - 1] if i > 0 else avg
            change_pct = ((week["demand_units"] - prev_demand) / prev_demand) * 100
            
            anomalies.append({
                "week": week["week"],
                "date": week["date"],
                "demand": week["demand_units"],
                "expected_demand": round(avg),
                "deviation_units": round(week["demand_units"] - avg),
                "deviation_pct": round(((week["demand_units"] - avg) / avg) * 100, 1),
                "z_score": round(z_score, 2),
                "week_over_week_change_pct": round(change_pct, 1),
                "type": "SPIKE" if z_score > 0 else "DIP",
                "severity": "HIGH" if abs(z_score) > 2.5 else "MEDIUM" if abs(z_score) > 2.0 else "LOW",
                "context": {
                    "had_promotion": week["promotions_active"],
                    "price_that_week": week["avg_price"],
                    "competitor_price": week["competitor_price"],
                },
            })
    
    # Provide contextual clues for diagnosis
    context_clues = {
        "social_media": market["social_media_mentions"],
        "competitor_activity": market["competitor_activity"],
        "upcoming_events": market["upcoming_events"],
        "economic_indicator": market["economic_indicator"],
    }
    
    return json.dumps({
        "product_id": product_id,
        "analysis_period": f"{historical[0]['week']} to {historical[-1]['week']}" if historical else "N/A",
        "baseline_demand": round(avg),
        "demand_std_dev": round(std),
        "sensitivity_threshold": sensitivity,
        "anomalies_found": len(anomalies),
        "anomalies": anomalies,
        "context_clues_for_diagnosis": context_clues,
        "note": "The LLM should cross-reference anomalies with context clues to generate root cause hypotheses.",
    }, indent=2)
