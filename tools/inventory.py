"""
Inventory Management Tools
These are the ALGORITHMS the Inventory Agent uses as tools.
The LLM decides WHEN to call them, INTERPRETS the results, and REASONS about them.
"""
import json
import math
import random
from langchain_core.tools import tool
from data.database_queries import (
    get_current_inventory,
    get_warehouse_details,
    get_supplier_performance,
    get_historical_stockouts,
    get_reorder_history,
    get_product_info,
)


@tool
def get_inventory_status(product_id: str = "PROD-A") -> str:
    """
    Get complete inventory picture including current stock, warehouse zone utilization,
    incoming orders, supplier reliability, and recent stockout history.
    Use this as the FIRST tool call to understand the full inventory situation before analysis.

    Args:
        product_id: The product ID to check inventory for (default: PROD-A)
    """
    inventory = get_current_inventory(product_id)
    warehouse = get_warehouse_details(product_id)
    suppliers = get_supplier_performance(product_id)
    stockouts = get_historical_stockouts(product_id)
    product = get_product_info(product_id)
    reorders = get_reorder_history(product_id)

    incoming_total = sum(o["quantity"] for o in inventory["incoming_orders"])

    result = {
        "product_info": product,
        "current_inventory": inventory,
        "warehouse_details": warehouse,
        "supplier_summary": [
            {
                "supplier_id": s["supplier_id"],
                "supplier_name": s["supplier_name"],
                "avg_lead_time_days": s["avg_lead_time_days"],
                "lead_time_std_dev_days": s["lead_time_std_dev_days"],
                "on_time_delivery_pct": s["on_time_delivery_pct"],
                "quality_reject_rate_pct": s["quality_reject_rate_pct"],
                "unit_cost": s["unit_cost"],
                "min_order_qty": s["min_order_quantity"],
                "max_order_qty": s["max_order_quantity"],
            }
            for s in suppliers
        ],
        "recent_stockout_history": stockouts,
        "recent_reorder_history": reorders[:4],
        "health_indicators": {
            "days_of_supply": inventory["days_of_supply"],
            "above_safety_stock": inventory["current_stock"] > inventory["safety_stock"],
            "buffer_above_safety": inventory["current_stock"] - inventory["safety_stock"],
            "incoming_pipeline_units": incoming_total,
            "effective_days_of_supply": round(
                (inventory["current_stock"] + incoming_total) / inventory["avg_daily_consumption"], 1
            ) if inventory.get("avg_daily_consumption") else 0,
            "warehouse_utilization_pct": warehouse["total_utilization_pct"],
            "stockout_events_last_12_months": len(stockouts),
            "total_stockout_revenue_lost": sum(s["revenue_lost"] for s in stockouts),
        },
    }

    return json.dumps(result, indent=2, default=str)


@tool
def calculate_reorder_point(
    product_id: str = "PROD-A",
    expected_daily_demand: float = 142.0,
    demand_std_dev_daily: float = 25.0,
    lead_time_days: float = 5.0,
    lead_time_std_dev_days: float = 1.0,
    service_level_pct: float = 95.0,
) -> str:
    """
    Calculate the Reorder Point (ROP) using the standard formula that accounts for
    both demand variability and lead time variability.

    ROP = (avg_daily_demand * avg_lead_time) + safety_stock
    Safety Stock = Z * sqrt(lead_time * demand_variance + avg_demand^2 * lead_time_variance)

    Use this AFTER getting the demand forecast to determine WHEN to place the next order.

    Args:
        product_id: Product to calculate ROP for
        expected_daily_demand: Expected daily demand in units (from demand forecast / 7)
        demand_std_dev_daily: Daily demand standard deviation
        lead_time_days: Average supplier lead time in days
        lead_time_std_dev_days: Standard deviation of lead time
        service_level_pct: Target service level (e.g., 95 = 95%)
    """
    # Z-score lookup
    z_table = {
        85.0: 1.04, 90.0: 1.28, 92.0: 1.41, 95.0: 1.645,
        97.0: 1.88, 97.5: 1.96, 98.0: 2.05, 99.0: 2.326,
    }
    # Find closest service level
    z_score = z_table.get(service_level_pct)
    if z_score is None:
        closest = min(z_table.keys(), key=lambda x: abs(x - service_level_pct))
        z_score = z_table[closest]

    # Safety stock formula (accounts for both demand and lead time variability)
    demand_variance = demand_std_dev_daily ** 2
    lead_time_variance = lead_time_std_dev_days ** 2
    safety_stock = z_score * math.sqrt(
        lead_time_days * demand_variance + expected_daily_demand ** 2 * lead_time_variance
    )
    safety_stock = round(safety_stock)

    # Reorder point
    avg_demand_during_lead_time = expected_daily_demand * lead_time_days
    rop = round(avg_demand_during_lead_time + safety_stock)

    # Compare with current stock
    inventory = get_current_inventory(product_id)
    current_stock = inventory["current_stock"]
    current_safety = inventory["safety_stock"]
    incoming = sum(o["quantity"] for o in inventory["incoming_orders"])

    reorder_needed = current_stock < rop
    days_until_rop = round((current_stock - rop) / expected_daily_demand, 1) if current_stock > rop else 0

    result = {
        "product_id": product_id,
        "reorder_point_units": rop,
        "current_stock": current_stock,
        "safety_stock_calculated": safety_stock,
        "safety_stock_current_setting": current_safety,
        "avg_demand_during_lead_time": round(avg_demand_during_lead_time),
        "reorder_needed_now": reorder_needed,
        "units_above_rop": max(0, current_stock - rop),
        "days_until_rop_reached": days_until_rop,
        "incoming_pipeline_units": incoming,
        "effective_position": current_stock + incoming,
        "calculation_inputs": {
            "daily_demand": expected_daily_demand,
            "demand_std_dev": demand_std_dev_daily,
            "lead_time": lead_time_days,
            "lead_time_std_dev": lead_time_std_dev_days,
            "z_score": z_score,
            "service_level_target": f"{service_level_pct}%",
        },
    }

    return json.dumps(result, indent=2)


@tool
def optimize_safety_stock(
    product_id: str = "PROD-A",
    expected_daily_demand: float = 142.0,
    demand_std_dev_daily: float = 25.0,
    lead_time_days: float = 5.0,
    lead_time_std_dev_days: float = 1.0,
    holding_cost_per_unit_per_year: float = 2.30,
    stockout_cost_per_unit: float = 45.00,
) -> str:
    """
    Calculate optimal safety stock by evaluating multiple service levels (85% to 99%).
    For each level, compute the safety stock required AND the total cost (holding + expected stockout).
    Finds the service level that minimizes total cost.

    Use this to determine whether the current safety stock (300 units) is too high or too low.

    Args:
        product_id: Product to optimize for
        expected_daily_demand: Average daily demand from forecast
        demand_std_dev_daily: Daily demand variability
        lead_time_days: Average lead time
        lead_time_std_dev_days: Lead time variability
        holding_cost_per_unit_per_year: Annual holding cost per unit
        stockout_cost_per_unit: Cost per unit of unmet demand
    """
    z_levels = [
        (85.0, 1.04), (90.0, 1.28), (92.0, 1.41), (95.0, 1.645),
        (97.0, 1.88), (98.0, 2.05), (99.0, 2.326),
    ]

    demand_variance = demand_std_dev_daily ** 2
    lead_time_variance = lead_time_std_dev_days ** 2
    annual_demand = expected_daily_demand * 365

    analysis = []
    for service_level, z in z_levels:
        ss = z * math.sqrt(
            lead_time_days * demand_variance + expected_daily_demand ** 2 * lead_time_variance
        )
        ss = round(ss)

        annual_holding = round(ss * holding_cost_per_unit_per_year, 2)

        # Expected annual stockout cost
        stockout_prob = 1 - service_level / 100
        # Expected shortage per cycle * cycles per year
        cycles_per_year = annual_demand / (expected_daily_demand * lead_time_days * 2)
        expected_shortage_per_cycle = demand_std_dev_daily * math.sqrt(lead_time_days) * max(0.01, stockout_prob * 3)
        annual_stockout = round(expected_shortage_per_cycle * cycles_per_year * stockout_cost_per_unit, 2)

        total = round(annual_holding + annual_stockout, 2)

        analysis.append({
            "service_level_pct": service_level,
            "z_score": z,
            "safety_stock_units": ss,
            "annual_holding_cost": annual_holding,
            "expected_annual_stockout_cost": annual_stockout,
            "total_annual_cost": total,
        })

    # Find optimal
    optimal = min(analysis, key=lambda x: x["total_annual_cost"])

    # Current safety stock comparison
    inventory = get_current_inventory(product_id)
    current_ss = inventory["safety_stock"]
    current_holding = round(current_ss * holding_cost_per_unit_per_year, 2)

    # Find effective service level of current safety stock
    sigma = math.sqrt(
        lead_time_days * demand_variance + expected_daily_demand ** 2 * lead_time_variance
    )
    current_z = current_ss / sigma if sigma > 0 else 0
    # Approximate service level from z-score
    if current_z >= 2.326:
        current_service = "~99%+"
    elif current_z >= 2.05:
        current_service = "~98%"
    elif current_z >= 1.88:
        current_service = "~97%"
    elif current_z >= 1.645:
        current_service = "~95%"
    elif current_z >= 1.28:
        current_service = "~90%"
    else:
        current_service = f"~{min(90, round(50 + current_z * 30))}%"

    result = {
        "product_id": product_id,
        "current_safety_stock": current_ss,
        "optimal_safety_stock": optimal["safety_stock_units"],
        "optimal_service_level_pct": optimal["service_level_pct"],
        "analysis_by_service_level": analysis,
        "current_vs_optimal": {
            "current_annual_holding_cost": current_holding,
            "optimal_annual_holding_cost": optimal["annual_holding_cost"],
            "annual_savings_if_optimized": round(current_holding - optimal["annual_holding_cost"], 2),
            "current_effective_service_level": current_service,
            "optimal_total_annual_cost": optimal["total_annual_cost"],
        },
    }

    return json.dumps(result, indent=2)


@tool
def simulate_stockout_risk(
    product_id: str = "PROD-A",
    current_stock: int = 1850,
    expected_daily_demand: float = 142.0,
    demand_std_dev_daily: float = 25.0,
    horizon_days: int = 14,
    simulations: int = 1000,
) -> str:
    """
    Run Monte Carlo simulation of stockout probability over a specified horizon.
    Simulates daily demand draws and incoming supply to determine the probability
    of hitting zero stock on each day.

    Use this to quantify the RISK of running out before the next delivery arrives.

    Args:
        product_id: Product to simulate
        current_stock: Current units on hand
        expected_daily_demand: Average daily demand
        demand_std_dev_daily: Daily demand standard deviation
        horizon_days: Number of days to simulate forward (default: 14)
        simulations: Number of Monte Carlo runs (default: 1000)
    """
    # Get incoming orders from data
    inventory = get_current_inventory(product_id)
    incoming = inventory["incoming_orders"]

    # Track results per day
    daily_stocks = {d: [] for d in range(1, horizon_days + 1)}
    stockout_days = {d: 0 for d in range(1, horizon_days + 1)}
    any_stockout_count = 0

    for _ in range(simulations):
        stock = current_stock
        had_stockout = False

        for day in range(1, horizon_days + 1):
            # Simulate daily demand
            demand = max(0, int(random.gauss(expected_daily_demand, demand_std_dev_daily)))
            stock -= demand

            # Check if any incoming orders arrive today (with +/- 1 day jitter)
            for order in incoming:
                eta = order["eta_days"]
                jitter = random.choice([-1, 0, 0, 0, 1])  # mostly on time
                if day == eta + jitter:
                    stock += order["quantity"]

            daily_stocks[day].append(stock)
            if stock <= 0:
                stockout_days[day] += 1
                had_stockout = True

        if had_stockout:
            any_stockout_count += 1

    # Build daily risk profile
    daily_profile = []
    critical_days = []
    for day in range(1, horizon_days + 1):
        stocks = daily_stocks[day]
        avg_stock = round(sum(stocks) / len(stocks))
        stockout_pct = round((stockout_days[day] / simulations) * 100, 1)

        daily_profile.append({
            "day": day,
            "avg_stock": avg_stock,
            "min_stock": min(stocks),
            "max_stock": max(stocks),
            "stockout_probability_pct": stockout_pct,
        })

        if stockout_pct > 3.0:
            critical_days.append({
                "day": day,
                "stockout_probability_pct": stockout_pct,
                "avg_stock_level": avg_stock,
            })

    # Worst case analysis
    all_min_stocks = [(day, min(daily_stocks[day])) for day in range(1, horizon_days + 1)]
    worst_day, worst_stock = min(all_min_stocks, key=lambda x: x[1])

    result = {
        "product_id": product_id,
        "simulation_parameters": {
            "current_stock": current_stock,
            "daily_demand": expected_daily_demand,
            "demand_std_dev": demand_std_dev_daily,
            "horizon_days": horizon_days,
            "simulations_run": simulations,
            "incoming_orders": incoming,
        },
        "overall_stockout_probability_pct": round((any_stockout_count / simulations) * 100, 1),
        "daily_risk_profile": daily_profile,
        "critical_days": critical_days,
        "worst_case_scenario": {
            "min_stock_reached": worst_stock,
            "day_of_min_stock": worst_day,
            "units_short": max(0, -worst_stock),
        },
    }

    return json.dumps(result, indent=2)


@tool
def evaluate_holding_costs(
    product_id: str = "PROD-A",
    current_stock: int = 1850,
    safety_stock: int = 300,
    holding_cost_per_unit_per_year: float = 2.30,
    stockout_cost_per_unit: float = 45.00,
    avg_daily_demand: float = 142.0,
    warehouse_capacity: int = 5000,
) -> str:
    """
    Analyze the tradeoff between carrying costs and stockout risk at different inventory levels.
    Evaluates current position and suggests the economically optimal inventory level.
    Includes EOQ (Economic Order Quantity) analysis.

    Use this when deciding whether to order more (accept holding costs) or risk stockout.

    Args:
        product_id: Product to evaluate
        current_stock: Current inventory on hand
        safety_stock: Current safety stock setting
        holding_cost_per_unit_per_year: Annual holding cost per unit
        stockout_cost_per_unit: Cost per unit of unmet demand
        avg_daily_demand: Average daily demand
        warehouse_capacity: Maximum warehouse capacity
    """
    daily_holding_rate = holding_cost_per_unit_per_year / 365
    annual_demand = avg_daily_demand * 365
    ordering_cost_estimate = 150.00  # Estimated fixed cost per order

    # EOQ calculation
    eoq = round(math.sqrt(2 * annual_demand * ordering_cost_estimate / holding_cost_per_unit_per_year))
    reorder_freq_days = round(eoq / avg_daily_demand, 1)

    # Historical stockout data
    stockouts = get_historical_stockouts(product_id)
    total_stockout_cost = sum(s["revenue_lost"] for s in stockouts)
    avg_stockout_cost = round(total_stockout_cost / len(stockouts), 2) if stockouts else 0

    # Evaluate different inventory levels
    levels = [
        current_stock,
        current_stock - 500,
        current_stock + 500,
        safety_stock,
        round(avg_daily_demand * 7),  # 1 week supply
        round(avg_daily_demand * 14),  # 2 week supply
    ]
    levels = sorted(set(max(0, l) for l in levels))

    comparisons = []
    for level in levels:
        daily_hold = round(level * daily_holding_rate, 2)
        weekly_hold = round(daily_hold * 7, 2)
        days_supply = round(level / avg_daily_demand, 1) if avg_daily_demand > 0 else 0
        utilization = round((level / warehouse_capacity) * 100, 1)

        # Simple stockout risk estimate based on days of supply
        if days_supply > 10:
            risk = round(max(0.5, 15 - days_supply), 1)
        elif days_supply > 5:
            risk = round(25 - days_supply * 1.5, 1)
        else:
            risk = round(min(80, 50 - days_supply * 5), 1)

        comparisons.append({
            "stock_level": level,
            "days_of_supply": days_supply,
            "daily_holding_cost": daily_hold,
            "weekly_holding_cost": weekly_hold,
            "annual_holding_cost": round(daily_hold * 365, 2),
            "estimated_stockout_risk_pct": max(0.1, risk),
            "warehouse_utilization_pct": utilization,
        })

    result = {
        "product_id": product_id,
        "current_position": {
            "stock": current_stock,
            "above_safety_stock": current_stock - safety_stock,
            "daily_holding_cost": round(current_stock * daily_holding_rate, 2),
            "weekly_holding_cost": round(current_stock * daily_holding_rate * 7, 2),
            "annual_holding_cost": round(current_stock * holding_cost_per_unit_per_year, 2),
            "days_of_supply": round(current_stock / avg_daily_demand, 1),
            "capital_tied_up": round(current_stock * get_product_info(product_id)["unit_cost"], 2),
        },
        "eoq_analysis": {
            "economic_order_quantity": eoq,
            "optimal_reorder_frequency_days": reorder_freq_days,
            "annual_ordering_cost_at_eoq": round(annual_demand / eoq * ordering_cost_estimate, 2),
            "annual_holding_cost_at_eoq": round(eoq / 2 * holding_cost_per_unit_per_year, 2),
        },
        "cost_comparison_at_levels": comparisons,
        "historical_stockout_impact": {
            "events_last_12_months": len(stockouts),
            "total_revenue_lost": total_stockout_cost,
            "avg_cost_per_event": avg_stockout_cost,
            "avg_duration_days": round(sum(s["duration_days"] for s in stockouts) / len(stockouts), 1) if stockouts else 0,
        },
    }

    return json.dumps(result, indent=2)


@tool
def generate_replenishment_plan(
    product_id: str = "PROD-A",
    expected_weekly_demand: float = 1050.0,
    demand_std_dev_weekly: float = 120.0,
    planning_horizon_weeks: int = 4,
    target_service_level_pct: float = 95.0,
    current_stock: int = 1850,
) -> str:
    """
    Generate a week-by-week replenishment schedule that balances service level targets,
    supplier constraints, and holding costs. Allocates orders across suppliers based on
    reliability, cost, and capacity.

    Use this AFTER getting demand forecast and reorder point to create an actionable plan.

    Args:
        product_id: Product to plan for
        expected_weekly_demand: Weekly demand from forecast
        demand_std_dev_weekly: Weekly demand uncertainty
        planning_horizon_weeks: Number of weeks to plan (default: 4)
        target_service_level_pct: Service level target (default: 95%)
        current_stock: Starting inventory
    """
    suppliers = get_supplier_performance(product_id)
    inventory = get_current_inventory(product_id)
    incoming = inventory["incoming_orders"]

    # Z-score for target service level
    z_table = {85.0: 1.04, 90.0: 1.28, 95.0: 1.645, 97.0: 1.88, 99.0: 2.326}
    z = z_table.get(target_service_level_pct, 1.645)

    # Safety stock target
    daily_demand = expected_weekly_demand / 7
    daily_std = demand_std_dev_weekly / math.sqrt(7)
    if not suppliers:
        return json.dumps({"error": "No supplier data available for replenishment planning."})
    avg_lt = suppliers[0]["avg_lead_time_days"]  # Use primary supplier lead time
    lt_std = suppliers[0]["lead_time_std_dev_days"]
    target_safety_stock = round(z * math.sqrt(
        avg_lt * daily_std ** 2 + daily_demand ** 2 * lt_std ** 2
    ))

    # Supplier allocation: 65% Supplier A (reliable), 35% Supplier B (cheaper)
    sup_a = suppliers[0]
    sup_b = suppliers[1] if len(suppliers) > 1 else suppliers[0]
    split_a = 0.65
    split_b = 0.35

    weekly_plan = []
    stock = current_stock
    total_ordered = 0
    total_cost = 0.0

    for week in range(1, planning_horizon_weeks + 1):
        start_stock = stock

        # Add incoming pipeline orders in week 1
        incoming_this_week = 0
        if week == 1:
            incoming_this_week = sum(o["quantity"] for o in incoming)

        stock += incoming_this_week

        # Expected consumption
        consumption = round(expected_weekly_demand + random.gauss(0, demand_std_dev_weekly * 0.3))
        consumption = max(0, consumption)
        stock -= consumption

        # Check if we need to order
        order_placed = False
        order_details = None
        projected_next_week = stock - expected_weekly_demand

        if projected_next_week < target_safety_stock * 1.5:
            # Calculate order quantity to bring stock to target
            target_stock = round(expected_weekly_demand * 2 + target_safety_stock)
            order_qty = max(0, target_stock - stock)

            if order_qty > 0:
                # Split between suppliers
                qty_a = max(sup_a["min_order_quantity"], round(order_qty * split_a / 100) * 100)
                qty_b = max(sup_b["min_order_quantity"], round(order_qty * split_b / 100) * 100)
                qty_a = min(qty_a, sup_a["max_order_quantity"])
                qty_b = min(qty_b, sup_b["max_order_quantity"])

                cost_a = qty_a * sup_a["unit_cost"]
                cost_b = qty_b * sup_b["unit_cost"]

                order_placed = True
                order_details = {
                    "supplier_a_qty": qty_a,
                    "supplier_a_cost": round(cost_a, 2),
                    "supplier_a_eta_days": round(sup_a["avg_lead_time_days"]),
                    "supplier_b_qty": qty_b,
                    "supplier_b_cost": round(cost_b, 2),
                    "supplier_b_eta_days": round(sup_b["avg_lead_time_days"]),
                    "total_qty": qty_a + qty_b,
                    "total_cost": round(cost_a + cost_b, 2),
                    "expected_arrival": f"Week {week + 1}" if week < planning_horizon_weeks else "After planning horizon",
                }
                total_ordered += qty_a + qty_b
                total_cost += cost_a + cost_b

                # Orders from last week arrive this week (simplified)
                if week > 1 and weekly_plan[-1].get("order_placed"):
                    prev_order = weekly_plan[-1]["order_details"]
                    stock += prev_order["supplier_a_qty"]  # Supplier A arrives in ~1 week

        ending_stock = max(0, stock)

        weekly_plan.append({
            "week": week,
            "starting_stock": start_stock,
            "incoming_pipeline": incoming_this_week,
            "expected_demand": round(expected_weekly_demand),
            "projected_ending_stock": ending_stock,
            "stock_above_safety": ending_stock > target_safety_stock,
            "order_placed": order_placed,
            "order_details": order_details,
        })

        stock = ending_stock

    result = {
        "product_id": product_id,
        "planning_parameters": {
            "horizon_weeks": planning_horizon_weeks,
            "weekly_demand": round(expected_weekly_demand),
            "demand_uncertainty": round(demand_std_dev_weekly),
            "target_service_level": f"{target_service_level_pct}%",
            "target_safety_stock": target_safety_stock,
            "starting_stock": current_stock,
        },
        "weekly_plan": weekly_plan,
        "plan_summary": {
            "total_units_ordered": total_ordered,
            "total_procurement_cost": round(total_cost, 2),
            "avg_projected_stock": round(sum(w["projected_ending_stock"] for w in weekly_plan) / len(weekly_plan)),
            "min_projected_stock": min(w["projected_ending_stock"] for w in weekly_plan),
            "weeks_below_safety_stock": sum(1 for w in weekly_plan if not w["stock_above_safety"]),
        },
        "supplier_allocation": {
            "supplier_a": {
                "pct_of_orders": f"{split_a * 100:.0f}%",
                "reason": f"Higher reliability ({sup_a['on_time_delivery_pct']}% on-time), faster lead time ({sup_a['avg_lead_time_days']} days)",
            },
            "supplier_b": {
                "pct_of_orders": f"{split_b * 100:.0f}%",
                "reason": f"Lower cost (${sup_b['unit_cost']} vs ${sup_a['unit_cost']}), diversification benefit",
            },
        },
    }

    return json.dumps(result, indent=2)
