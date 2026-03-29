"""
Monte Carlo Simulation Tools
Financial impact simulation under demand uncertainty.
"""
import json
import math
import random
from langchain_core.tools import tool


@tool
def monte_carlo_profit_simulation(
    expected_demand: int = 1000,
    unit_price: float = 89.50,
    unit_cost: float = 52.00,
    holding_cost_per_unit: float = 2.30,
    stockout_cost_per_unit: float = 45.00,
    production_quantity: int = 1000,
    demand_std_dev: float = 120.0,
    simulations: int = 1000,
) -> str:
    """
    Run Monte Carlo simulation to evaluate the financial impact of a production decision.
    Simulates thousands of demand scenarios and calculates expected profit, risk metrics,
    and probability of different outcomes.
    
    Use this AFTER getting demand scenarios to evaluate which production strategy
    (aggressive, balanced, conservative) maximizes expected profit.
    
    Args:
        expected_demand: Expected demand in units
        unit_price: Selling price per unit
        unit_cost: Production cost per unit
        holding_cost_per_unit: Cost to hold excess inventory per unit
        stockout_cost_per_unit: Lost profit + penalty per unit of unmet demand
        production_quantity: How many units to produce (the decision variable)
        demand_std_dev: Standard deviation of demand uncertainty
        simulations: Number of Monte Carlo iterations
    """
    profits = []
    stockout_count = 0
    overstock_count = 0
    
    for _ in range(simulations):
        # Simulate actual demand from normal distribution
        actual_demand = max(0, int(random.gauss(expected_demand, demand_std_dev)))
        
        # Calculate units sold, excess, and shortage
        units_sold = min(production_quantity, actual_demand)
        excess = max(0, production_quantity - actual_demand)
        shortage = max(0, actual_demand - production_quantity)
        
        # Calculate profit
        revenue = units_sold * unit_price
        production_cost = production_quantity * unit_cost
        holding_penalty = excess * holding_cost_per_unit
        stockout_penalty = shortage * stockout_cost_per_unit
        
        profit = revenue - production_cost - holding_penalty - stockout_penalty
        profits.append(profit)
        
        if shortage > 0:
            stockout_count += 1
        if excess > 50:  # Meaningful overstock
            overstock_count += 1
    
    # Calculate statistics
    avg_profit = sum(profits) / len(profits)
    profits_sorted = sorted(profits)
    
    # Value at Risk (5th percentile - worst case)
    var_5 = profits_sorted[int(0.05 * simulations)]
    var_10 = profits_sorted[int(0.10 * simulations)]
    
    # Best case (95th percentile)
    best_95 = profits_sorted[int(0.95 * simulations)]
    
    std_profit = math.sqrt(sum((p - avg_profit) ** 2 for p in profits) / len(profits))
    
    result = {
        "simulation_parameters": {
            "expected_demand": expected_demand,
            "production_quantity": production_quantity,
            "unit_price": unit_price,
            "unit_cost": unit_cost,
            "simulations_run": simulations,
        },
        "profit_analysis": {
            "expected_profit": round(avg_profit, 2),
            "profit_std_dev": round(std_profit, 2),
            "worst_case_5pct": round(var_5, 2),
            "worst_case_10pct": round(var_10, 2),
            "best_case_95pct": round(best_95, 2),
            "min_profit": round(min(profits), 2),
            "max_profit": round(max(profits), 2),
        },
        "risk_metrics": {
            "stockout_probability_pct": round((stockout_count / simulations) * 100, 1),
            "overstock_probability_pct": round((overstock_count / simulations) * 100, 1),
            "profit_at_risk_5pct": round(avg_profit - var_5, 2),
            "sharpe_ratio": round(avg_profit / std_profit, 3) if std_profit > 0 else 0,
        },
        "recommendation_data": {
            "break_even_demand": math.ceil(production_quantity * unit_cost / unit_price),
            "margin_per_unit": round(unit_price - unit_cost, 2),
            "margin_pct": round(((unit_price - unit_cost) / unit_price) * 100, 1),
        },
    }
    
    return json.dumps(result, indent=2)


@tool
def compare_production_strategies(
    expected_demand: int = 1000,
    demand_std_dev: float = 120.0,
    unit_price: float = 89.50,
    unit_cost: float = 52.00,
) -> str:
    """
    Compare three production strategies (Conservative, Balanced, Aggressive) using
    Monte Carlo simulation. Each strategy produces a different quantity.
    
    Use this to recommend which strategy maximizes expected profit vs risk trade-off.
    
    Args:
        expected_demand: Expected demand in units
        demand_std_dev: Uncertainty in demand (standard deviation)
        unit_price: Selling price per unit
        unit_cost: Production cost per unit
    """
    strategies = {
        "conservative": {
            "production_qty": int(expected_demand * 0.85),
            "description": "Produce 85% of expected demand. Low overstock risk, higher stockout risk.",
        },
        "balanced": {
            "production_qty": expected_demand,
            "description": "Produce 100% of expected demand. Balanced risk.",
        },
        "aggressive": {
            "production_qty": int(expected_demand * 1.15),
            "description": "Produce 115% of expected demand. Higher profit potential, overstock risk.",
        },
    }
    
    results = {}
    simulations = 1000
    
    for name, strategy in strategies.items():
        qty = strategy["production_qty"]
        profits = []
        stockouts = 0
        
        for _ in range(simulations):
            actual = max(0, int(random.gauss(expected_demand, demand_std_dev)))
            sold = min(qty, actual)
            excess = max(0, qty - actual)
            shortage = max(0, actual - qty)
            
            profit = (sold * unit_price) - (qty * unit_cost) - (excess * 2.30) - (shortage * 45.0)
            profits.append(profit)
            if shortage > 0:
                stockouts += 1
        
        avg = sum(profits) / len(profits)
        sorted_p = sorted(profits)
        std = math.sqrt(sum((p - avg) ** 2 for p in profits) / len(profits))
        
        results[name] = {
            "production_quantity": qty,
            "description": strategy["description"],
            "expected_profit": round(avg, 2),
            "profit_std_dev": round(std, 2),
            "worst_case_5pct": round(sorted_p[int(0.05 * simulations)], 2),
            "best_case_95pct": round(sorted_p[int(0.95 * simulations)], 2),
            "stockout_probability_pct": round((stockouts / simulations) * 100, 1),
            "risk_adjusted_return": round(avg / std, 3) if std > 0 else 0,
        }
    
    # Determine winner
    best = max(results.items(), key=lambda x: x[1]["expected_profit"])
    best_risk_adj = max(results.items(), key=lambda x: x[1]["risk_adjusted_return"])
    
    return json.dumps({
        "strategies": results,
        "highest_expected_profit": best[0],
        "best_risk_adjusted": best_risk_adj[0],
        "expected_demand": expected_demand,
        "demand_uncertainty": demand_std_dev,
    }, indent=2)
