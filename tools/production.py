"""
Production Planning Tools
These are the ALGORITHMS the Production Planning Agent uses as tools.
The LLM decides WHEN to call them, INTERPRETS the results, and REASONS about them.
"""
import json
import math
import random
from langchain_core.tools import tool
from data.database_queries import (
    get_production_lines,
    get_bill_of_materials,
    get_production_history,
    get_shift_configuration,
    get_machine_fleet,
    get_current_inventory,
    get_product_info,
)


@tool
def get_production_context(product_id: str = "PROD-A") -> str:
    """
    Consolidate all upstream inputs needed for production planning:
    machine capacity, current inventory position, recent production history,
    shift configuration, and product information.

    Use this as the FIRST tool call to get the full picture before building
    any schedule. This is the Production Planning Agent's 'PERCEIVE' step.

    Args:
        product_id: The product to plan production for (default: PROD-A)
    """
    lines = get_production_lines()
    fleet = get_machine_fleet()
    inventory = get_current_inventory(product_id)
    product = get_product_info(product_id)
    history = get_production_history(product_id, weeks=8)
    shifts = get_shift_configuration()
    bom = get_bill_of_materials(product_id)

    # Summarize active vs down lines
    active_lines = [l for l in lines if l["status"] == "operational"]
    down_lines = [l for l in lines if l["status"] == "down"]
    warning_lines = [l for l in lines if l["current_efficiency_pct"] < 80 and l["status"] == "operational"]

    # Current effective capacity
    effective_daily = sum(l["effective_output_per_day"] for l in active_lines)
    effective_weekly = effective_daily * 5
    theoretical_daily = sum(l["max_output_per_day"] for l in lines)
    theoretical_weekly = theoretical_daily * 5

    # Production attainment trend (last 6 completed weeks)
    completed = [w for w in history if w["actual_units"] is not None]
    avg_attainment = round(sum(w["attainment_pct"] for w in completed) / len(completed), 1) if completed else 0
    avg_overtime_hrs = round(sum(w["overtime_hours"] for w in completed) / len(completed), 1) if completed else 0

    # Component stock check: weeks of supply per component
    component_coverage = []
    if bom:
        for comp in bom.get("components", []):
            weeks_supply = round(comp["current_stock_units"] / max(1, effective_weekly), 2)
            component_coverage.append({
                "component_id": comp["component_id"],
                "name": comp["component_name"],
                "current_stock": comp["current_stock_units"],
                "weeks_of_supply": weeks_supply,
                "reorder_point": comp["reorder_point"],
                "below_reorder": comp["current_stock_units"] <= comp["reorder_point"],
            })

    result = {
        "product_id": product_id,
        "product_name": product["product_name"],
        "capacity_summary": {
            "theoretical_max_units_per_day": theoretical_daily,
            "theoretical_max_units_per_week": theoretical_weekly,
            "current_effective_units_per_day": effective_daily,
            "current_effective_units_per_week": effective_weekly,
            "capacity_loss_pct": round((1 - effective_daily / theoretical_daily) * 100, 1),
            "active_lines": len(active_lines),
            "down_lines": len(down_lines),
            "degraded_lines_on_warning": len(warning_lines),
        },
        "line_status": [
            {
                "line_id": l["line_id"],
                "status": l["status"],
                "effective_output_per_day": l["effective_output_per_day"],
                "efficiency_pct": l["current_efficiency_pct"],
                "machine": l["machine_name"],
                "estimated_return": l.get("estimated_return_date"),
            }
            for l in lines
        ],
        "inventory_position": {
            "current_stock_units": inventory["current_stock"],
            "safety_stock_units": inventory["safety_stock"],
            "days_of_supply": inventory["days_of_supply"],
            "incoming_pipeline": inventory["incoming_orders"],
        },
        "shift_config": shifts,
        "production_history_summary": {
            "weeks_analyzed": len(completed),
            "avg_attainment_pct": avg_attainment,
            "avg_overtime_hours_per_week": avg_overtime_hrs,
            "recent_shortfalls": [
                {"week": w["week"], "actual": w["actual_units"], "planned": w["planned_units"], "reason": w["shortfall_reason"]}
                for w in completed if w["attainment_pct"] < 98
            ],
        },
        "component_coverage": component_coverage,
        "financials": {
            "unit_cost": product["unit_cost"],
            "unit_price": product["unit_price"],
            "margin_pct": product["margin_pct"],
            "overtime_cost_premium_pct": shifts["overtime"]["cost_premium_pct"],
            "contract_mfg_cost_premium_pct": shifts["contract_manufacturing"]["cost_premium_pct"],
        },
    }

    return json.dumps(result, indent=2, default=str)


@tool
def build_master_production_schedule(
    planning_weeks: int = 4,
    target_weekly_output: float = 1050.0,
    line4_returns_week: int = 1,
    mch002_maintenance_week: int = 1,
) -> str:
    """
    Build the Master Production Schedule (MPS) week by week.
    Allocates production targets across active lines, accounts for maintenance
    windows and machine return-to-service dates, and projects inventory levels.

    This is the core output of the Production Planning Agent.

    Args:
        planning_weeks: How many weeks to plan (default: 4)
        target_weekly_output: Demand-driven output target per week (default: 1050)
        line4_returns_week: Which week Line 4 returns from repair (default: 1 = this week)
        mch002_maintenance_week: Which week MCH-002 goes in for planned maintenance (default: 1)
    """
    lines = get_production_lines()
    inventory = get_current_inventory()
    shifts = get_shift_configuration()

    current_stock = inventory["current_stock"]
    safety_stock = inventory["safety_stock"]
    incoming = sum(o["quantity"] for o in inventory["incoming_orders"])

    # Line 4 starts down; MCH-002 goes to planned maintenance
    # After maintenance MCH-002 comes back at 95% efficiency
    weekly_schedule = []
    total_produced = 0
    total_overtime_cost = 0.0
    total_contract_units = 0

    unit_cost = 52.00
    unit_price = 89.50
    ot_premium = shifts["overtime"]["cost_premium_pct"] / 100
    contract_premium = shifts["contract_manufacturing"]["cost_premium_pct"] / 100

    for week in range(1, planning_weeks + 1):
        # Determine which lines are active this week
        line_schedule = []
        week_capacity = 0

        for line in lines:
            lid = line["line_id"]
            base_eff = line["current_efficiency_pct"] / 100
            max_out = line["max_output_per_day"]

            # Line 4 availability
            if lid == "Line 4":
                if week < line4_returns_week + 1:
                    # Still down
                    line_schedule.append({
                        "line_id": lid, "status": "down",
                        "planned_output": 0, "note": "Corrective maintenance in progress",
                    })
                    continue
                else:
                    # Returned — runs at 85% initially (burn-in period)
                    base_eff = 0.85

            # MCH-002 maintenance
            if lid == "Line 2" and week == mch002_maintenance_week:
                line_schedule.append({
                    "line_id": lid, "status": "planned_maintenance",
                    "planned_output": 0,
                    "note": f"Planned MCH-002 maintenance Week {week} — returns at 95% efficiency",
                })
                continue
            elif lid == "Line 2" and week > mch002_maintenance_week:
                # After maintenance: improved to 95%
                base_eff = 0.95

            daily_output = round(max_out * base_eff)
            weekly_output = daily_output * 5  # 5 working days

            line_schedule.append({
                "line_id": lid,
                "status": "operational",
                "efficiency_pct": round(base_eff * 100),
                "daily_output": daily_output,
                "planned_weekly_output": weekly_output,
            })
            week_capacity += weekly_output

        # Assess gap
        gap = target_weekly_output - week_capacity
        overtime_units = 0
        contract_units = 0
        overtime_cost = 0.0
        contract_cost = 0.0

        if gap > 0:
            # Fill gap with overtime first (cheaper)
            ot_max = shifts["overtime"]["additional_units_per_overtime_hour"] * \
                     shifts["overtime"]["max_overtime_hours_per_day"] * 5  # per week
            ot_units = min(gap, ot_max)
            overtime_units = round(ot_units)
            overtime_cost = round(overtime_units * unit_cost * ot_premium, 2)
            remaining_gap = gap - overtime_units

            # Then contract manufacturing
            if remaining_gap > 0:
                contract_units = round(min(
                    remaining_gap,
                    shifts["contract_manufacturing"]["max_capacity_units_per_week"]
                ))
                contract_cost = round(contract_units * unit_cost * contract_premium, 2)

        total_produced_this_week = week_capacity + overtime_units + contract_units
        shortfall = max(0, target_weekly_output - total_produced_this_week)

        # Inventory projection
        stock_start = current_stock + (incoming if week == 1 else 0)
        stock_end = max(0, stock_start + total_produced_this_week - target_weekly_output)
        above_safety = stock_end >= safety_stock

        overtime_cost_week = overtime_cost + contract_cost
        total_overtime_cost += overtime_cost_week
        total_contract_units += contract_units

        weekly_schedule.append({
            "week": week,
            "target_output": round(target_weekly_output),
            "line_schedule": line_schedule,
            "base_capacity": week_capacity,
            "overtime_units": overtime_units,
            "contract_manufacturing_units": contract_units,
            "total_planned_output": round(total_produced_this_week),
            "shortfall_units": round(shortfall),
            "demand_met_pct": round(min(100, total_produced_this_week / target_weekly_output * 100), 1),
            "inventory_projection": {
                "start_stock": stock_start,
                "end_stock": round(stock_end),
                "above_safety_stock": above_safety,
            },
            "additional_cost": overtime_cost_week,
            "overtime_cost": overtime_cost,
            "contract_cost": contract_cost,
        })

        current_stock = round(stock_end)
        total_produced += total_produced_this_week

    # MPS summary
    result = {
        "master_production_schedule": {
            "planning_horizon_weeks": planning_weeks,
            "target_weekly_output": round(target_weekly_output),
            "schedule": weekly_schedule,
        },
        "mps_summary": {
            "total_planned_units": round(total_produced),
            "total_target_units": round(target_weekly_output * planning_weeks),
            "overall_attainment_pct": round(total_produced / (target_weekly_output * planning_weeks) * 100, 1),
            "total_shortfall_units": round(max(0, target_weekly_output * planning_weeks - total_produced)),
            "weeks_with_shortfall": sum(1 for w in weekly_schedule if w["shortfall_units"] > 0),
            "total_overtime_and_contract_cost": round(total_overtime_cost, 2),
            "total_contract_manufacturing_units": total_contract_units,
        },
        "cross_agent_alert_for_supplier": {
            "message": "Supplier Agent: production schedule requires the following material volumes",
            "total_units_to_produce": round(total_produced),
            "planning_horizon_weeks": planning_weeks,
        },
    }

    return json.dumps(result, indent=2, default=str)


@tool
def analyze_production_bottlenecks() -> str:
    """
    Identify which production line is the system constraint (bottleneck)
    using Theory of Constraints principles. Determines:
    - Which line limits total throughput
    - How much capacity is lost per line
    - Whether re-routing work between lines is feasible
    - Throughput improvement opportunities

    Use this to understand WHERE the production system is constrained and
    what fixing it would be worth financially.
    """
    lines = get_production_lines()
    fleet = get_machine_fleet()
    product = get_product_info()

    unit_margin = product["unit_price"] - product["unit_cost"]
    days_per_week = 5

    line_analysis = []
    total_effective = 0
    total_theoretical = 0

    for line in lines:
        lid = line["line_id"]
        max_daily = line["max_output_per_day"]
        eff_daily = line["effective_output_per_day"]
        eff_pct = line["current_efficiency_pct"]

        # Find machine details
        machine = next((m for m in fleet if m["machine_id"] == line["primary_machine"]), {})

        capacity_lost_daily = max_daily - eff_daily
        capacity_lost_weekly = capacity_lost_daily * days_per_week
        revenue_lost_weekly = round(capacity_lost_weekly * unit_margin, 2)

        # Improvement potential: what if we fixed this line to 97%?
        potential_daily = round(max_daily * 0.97)
        gain_if_fixed = (potential_daily - eff_daily) * days_per_week
        gain_value_weekly = round(gain_if_fixed * unit_margin, 2)

        total_effective += eff_daily
        total_theoretical += max_daily

        line_analysis.append({
            "line_id": lid,
            "machine_id": line["primary_machine"],
            "status": line["status"],
            "max_output_per_day": max_daily,
            "effective_output_per_day": eff_daily,
            "efficiency_pct": eff_pct,
            "capacity_lost_per_day": capacity_lost_daily,
            "capacity_lost_per_week": capacity_lost_weekly,
            "weekly_margin_lost": revenue_lost_weekly,
            "improvement_potential_units_per_week": gain_if_fixed,
            "improvement_value_per_week": gain_value_weekly,
            "machine_health_score": machine.get("health_score", 0),
            "machine_alert_level": machine.get("alert_level", "unknown"),
        })

    # Rank by capacity lost (most impactful bottleneck first)
    line_analysis.sort(key=lambda x: x["capacity_lost_per_week"], reverse=True)

    # Primary bottleneck
    bottleneck = line_analysis[0]

    # System-level metrics
    system_efficiency = round((total_effective / total_theoretical) * 100, 1) if total_theoretical else 0
    total_capacity_lost_weekly = (total_theoretical - total_effective) * days_per_week
    total_margin_lost_weekly = round(total_capacity_lost_weekly * unit_margin, 2)

    # Re-routing feasibility (can work from Line 4 go to Line 5?)
    rerouting_note = (
        "Line 4 (Conveyor) work cannot be directly rerouted — material handling is integral to the line. "
        "However, overtime on Lines 1, 3, 5 can partially compensate."
    )

    result = {
        "bottleneck_analysis": {
            "primary_bottleneck": {
                "line_id": bottleneck["line_id"],
                "reason": f"Largest capacity gap: {bottleneck['capacity_lost_per_week']} units/week lost",
                "weekly_margin_lost": bottleneck["weekly_margin_lost"],
                "machine_health_score": bottleneck["machine_health_score"],
                "alert_level": bottleneck["machine_alert_level"],
            },
            "system_efficiency_pct": system_efficiency,
            "total_capacity_lost_per_week": total_capacity_lost_weekly,
            "total_weekly_margin_lost": total_margin_lost_weekly,
            "rerouting_feasibility": rerouting_note,
        },
        "line_by_line_ranking": line_analysis,
        "improvement_priority": [
            {
                "priority": i + 1,
                "line_id": la["line_id"],
                "action": (
                    "Restore from downtime" if la["status"] == "down" else
                    "Immediate maintenance — HIGH failure risk" if la["machine_alert_level"] == "warning" else
                    "Schedule preventive maintenance" if la["machine_alert_level"] == "caution" else
                    "Maintain current performance"
                ),
                "weekly_gain_if_fixed": la["improvement_potential_units_per_week"],
                "weekly_value": la["improvement_value_per_week"],
            }
            for i, la in enumerate(line_analysis[:4])
        ],
    }

    return json.dumps(result, indent=2, default=str)


@tool
def evaluate_capacity_gap(
    required_weekly_units: float = 1050.0,
    planning_weeks: int = 4,
) -> str:
    """
    Calculate the gap between production demand and available capacity.
    Evaluates three options to close the gap:
    1. Overtime (cheapest, limited capacity)
    2. Contract manufacturing (expensive, up to 500 units/week)
    3. Partial fulfillment (prioritize highest-margin customer segments)

    Ranks options by cost and feasibility. Provides go/no-go recommendation
    for each option with full financial detail.

    Args:
        required_weekly_units: Weekly production target from demand forecast
        planning_weeks: Number of weeks in the planning horizon
    """
    lines = get_production_lines()
    shifts = get_shift_configuration()
    product = get_product_info()

    active_lines = [l for l in lines if l["status"] == "operational"]
    effective_daily = sum(l["effective_output_per_day"] for l in active_lines)
    effective_weekly = effective_daily * 5
    weekly_gap = required_weekly_units - effective_weekly
    total_gap = weekly_gap * planning_weeks

    unit_cost = product["unit_cost"]
    unit_price = product["unit_price"]
    unit_margin = unit_price - unit_cost

    if weekly_gap <= 0:
        return json.dumps({
            "gap_assessment": {
                "required_weekly": required_weekly_units,
                "available_weekly": effective_weekly,
                "gap_units_per_week": 0,
                "status": "NO GAP — capacity exceeds demand",
                "recommendation": "No additional capacity needed. Operate at standard output.",
            }
        }, indent=2)

    # Option 1: Overtime
    ot_units_per_day = shifts["overtime"]["additional_units_per_overtime_hour"] * \
                       shifts["overtime"]["max_overtime_hours_per_day"]
    ot_weekly_max = ot_units_per_day * 5
    ot_units_available = min(weekly_gap, ot_weekly_max)
    ot_cost_per_unit = round(unit_cost * (1 + shifts["overtime"]["cost_premium_pct"] / 100), 2)
    ot_weekly_cost = round(ot_units_available * unit_cost * (shifts["overtime"]["cost_premium_pct"] / 100), 2)
    ot_margin = round(ot_units_available * (unit_price - ot_cost_per_unit), 2)
    ot_gap_remaining = max(0, weekly_gap - ot_units_available)

    # Option 2: Contract Manufacturing
    cm_max = shifts["contract_manufacturing"]["max_capacity_units_per_week"]
    cm_units = min(ot_gap_remaining if ot_gap_remaining > 0 else weekly_gap, cm_max)
    cm_cost_per_unit = round(unit_cost * (1 + shifts["contract_manufacturing"]["cost_premium_pct"] / 100), 2)
    cm_weekly_cost = round(cm_units * unit_cost * (shifts["contract_manufacturing"]["cost_premium_pct"] / 100), 2)
    cm_margin = round(cm_units * (unit_price - cm_cost_per_unit), 2)

    # Can we fully close the gap with OT + CM?
    total_additional = ot_units_available + cm_units
    gap_after_ot_cm = max(0, weekly_gap - total_additional)

    # Option 3: Partial Fulfillment — prioritize enterprise (highest margin, biggest orders)
    customer_segments = product["customer_segments"]
    fulfillment_plan = []
    remaining_capacity = effective_weekly + ot_units_available + cm_units
    for seg_name, seg in customer_segments.items():
        seg_demand = round(required_weekly_units * seg["share_pct"] / 100)
        seg_fulfilled = min(seg_demand, remaining_capacity)
        fulfillment_rate = round(seg_fulfilled / seg_demand * 100, 1)
        revenue_at_risk = round(max(0, seg_demand - seg_fulfilled) * unit_price, 2)
        remaining_capacity = max(0, remaining_capacity - seg_fulfilled)
        fulfillment_plan.append({
            "segment": seg_name,
            "share_pct": seg["share_pct"],
            "demand_units": seg_demand,
            "fulfilled_units": seg_fulfilled,
            "fulfillment_rate_pct": fulfillment_rate,
            "revenue_at_risk": revenue_at_risk,
        })

    result = {
        "gap_assessment": {
            "required_weekly_units": round(required_weekly_units),
            "available_base_capacity_weekly": effective_weekly,
            "weekly_gap_units": round(weekly_gap),
            "total_gap_over_horizon_units": round(total_gap),
            "gap_as_pct_of_demand": round(weekly_gap / required_weekly_units * 100, 1),
        },
        "options": {
            "option_1_overtime": {
                "units_available_per_week": round(ot_units_available),
                "closes_gap_pct": round(ot_units_available / weekly_gap * 100, 1),
                "additional_cost_per_week": ot_weekly_cost,
                "additional_cost_total_horizon": round(ot_weekly_cost * planning_weeks, 2),
                "margin_per_week": ot_margin,
                "cost_per_unit_premium": round(ot_cost_per_unit - unit_cost, 2),
                "activation_lead_time": shifts["overtime"]["activation_lead_time_hours"],
                "feasible": True,
            },
            "option_2_contract_manufacturing": {
                "units_available_per_week": round(cm_units),
                "closes_gap_pct": round((ot_units_available + cm_units) / weekly_gap * 100, 1),
                "additional_cost_per_week": cm_weekly_cost,
                "additional_cost_total_horizon": round(cm_weekly_cost * planning_weeks, 2),
                "margin_per_week": cm_margin,
                "cost_per_unit_premium": round(cm_cost_per_unit - unit_cost, 2),
                "activation_lead_time_days": shifts["contract_manufacturing"]["activation_lead_time_days"],
                "quality_risk": shifts["contract_manufacturing"]["quality_risk"],
                "feasible": cm_units >= min(200, ot_gap_remaining),
            },
            "option_3_partial_fulfillment": {
                "unmet_demand_units_per_week": round(gap_after_ot_cm),
                "fulfillment_by_segment": fulfillment_plan,
                "total_revenue_at_risk_per_week": round(sum(s["revenue_at_risk"] for s in fulfillment_plan), 2),
            },
        },
        "recommendation": (
            "Use overtime only — gap is within overtime capacity" if weekly_gap <= ot_weekly_max else
            "Use overtime + contract manufacturing — gap exceeds overtime limit" if weekly_gap <= ot_weekly_max + cm_max else
            "CRITICAL: Gap exceeds all supplemental capacity — partial fulfillment unavoidable"
        ),
        "recommended_action_cost_per_week": round(ot_weekly_cost + (cm_weekly_cost if ot_gap_remaining > 0 else 0), 2),
    }

    return json.dumps(result, indent=2, default=str)


@tool
def optimize_production_mix(
    planning_weeks: int = 4,
    demand_scenario: str = "base",
) -> str:
    """
    Given machine capacity constraints, optimize the production plan for the
    chosen demand scenario (optimistic / base / pessimistic).

    Calculates the risk-adjusted production target and financial outcome
    for each scenario, then recommends the optimal production level.

    Use this AFTER evaluating the capacity gap to decide which plan to commit to.

    Args:
        planning_weeks: Planning horizon in weeks
        demand_scenario: 'optimistic', 'base', or 'pessimistic'
    """
    lines = get_production_lines()
    shifts = get_shift_configuration()
    product = get_product_info()

    active_lines = [l for l in lines if l["status"] == "operational"]
    base_capacity_weekly = sum(l["effective_output_per_day"] for l in active_lines) * 5

    ot_max_weekly = (
        shifts["overtime"]["additional_units_per_overtime_hour"] *
        shifts["overtime"]["max_overtime_hours_per_day"] * 5
    )
    cm_max_weekly = shifts["contract_manufacturing"]["max_capacity_units_per_week"]
    total_max_weekly = base_capacity_weekly + ot_max_weekly + cm_max_weekly

    unit_cost = product["unit_cost"]
    unit_price = product["unit_price"]
    ot_premium = shifts["overtime"]["cost_premium_pct"] / 100
    cm_premium = shifts["contract_manufacturing"]["cost_premium_pct"] / 100

    # Demand scenarios (aligned with Demand Agent output)
    scenarios = {
        "pessimistic": {"weekly_demand": 875, "probability": 0.25},
        "base":        {"weekly_demand": 1050, "probability": 0.55},
        "optimistic":  {"weekly_demand": 1260, "probability": 0.20},
    }

    scenario_analysis = []
    for name, s in scenarios.items():
        demand = s["weekly_demand"]
        prob = s["probability"]

        # Production plan for this scenario
        base_units = min(demand, base_capacity_weekly)
        ot_units = min(max(0, demand - base_units), ot_max_weekly)
        cm_units = min(max(0, demand - base_units - ot_units), cm_max_weekly)
        produced = base_units + ot_units + cm_units
        unmet = max(0, demand - produced)

        # Weekly cost and revenue
        base_cost = base_units * unit_cost
        ot_cost = ot_units * unit_cost * ot_premium
        cm_cost = cm_units * unit_cost * cm_premium
        revenue = min(produced, demand) * unit_price
        stockout_penalty = unmet * 45.00  # opportunity cost per unit

        weekly_profit = revenue - base_cost - ot_cost - cm_cost - stockout_penalty
        total_profit = weekly_profit * planning_weeks

        scenario_analysis.append({
            "scenario": name,
            "probability": prob,
            "weekly_demand": demand,
            "weekly_production_plan": {
                "base_units": base_units,
                "overtime_units": round(ot_units),
                "contract_units": round(cm_units),
                "total_produced": round(produced),
                "unmet_demand": round(unmet),
                "demand_fill_rate_pct": round(produced / demand * 100, 1),
            },
            "weekly_financials": {
                "revenue": round(revenue, 2),
                "base_production_cost": round(base_cost, 2),
                "overtime_cost": round(ot_cost, 2),
                "contract_mfg_cost": round(cm_cost, 2),
                "stockout_penalty": round(stockout_penalty, 2),
                "net_profit": round(weekly_profit, 2),
            },
            "horizon_profit": round(total_profit, 2),
            "expected_profit_weighted": round(total_profit * prob, 2),
        })

    # Expected value across all scenarios
    expected_profit = sum(s["expected_profit_weighted"] for s in scenario_analysis)

    # Find the optimal production target (base + OT is typical)
    selected = next(s for s in scenario_analysis if s["scenario"] == demand_scenario)

    result = {
        "selected_scenario": demand_scenario,
        "scenario_analysis": scenario_analysis,
        "expected_value_analysis": {
            "expected_horizon_profit": round(expected_profit, 2),
            "max_capacity_per_week": total_max_weekly,
            "base_capacity_per_week": base_capacity_weekly,
        },
        "recommended_production_target": {
            "weekly_units": selected["weekly_production_plan"]["total_produced"],
            "base_capacity_units": selected["weekly_production_plan"]["base_units"],
            "overtime_needed": selected["weekly_production_plan"]["overtime_units"] > 0,
            "contract_mfg_needed": selected["weekly_production_plan"]["contract_units"] > 0,
            "projected_horizon_profit": selected["horizon_profit"],
            "demand_fill_rate_pct": selected["weekly_production_plan"]["demand_fill_rate_pct"],
        },
    }

    return json.dumps(result, indent=2, default=str)


@tool
def generate_production_requirements(
    weekly_units_to_produce: int = 980,
    planning_weeks: int = 4,
) -> str:
    """
    Generate the raw material requirements for the production plan using
    the Bill of Materials (BOM). This is the key output passed to the
    Supplier Agent — it tells suppliers exactly what components to deliver
    and when.

    Flags any components that are below their reorder point or will run
    out before the end of the planning horizon.

    Args:
        weekly_units_to_produce: Confirmed weekly output target from MPS
        planning_weeks: Planning horizon in weeks
    """
    bom = get_bill_of_materials()

    if not bom:
        return json.dumps({"error": "BOM not found"})

    total_units = weekly_units_to_produce * planning_weeks
    weekly_requirements = []
    component_alerts = []
    total_material_cost = 0.0

    for comp in bom["components"]:
        qty_per_unit = comp["qty_per_unit"]
        total_qty_needed = total_units * qty_per_unit
        weekly_qty = weekly_units_to_produce * qty_per_unit

        current_stock = comp["current_stock_units"]
        reorder_point = comp["reorder_point"]
        weeks_of_supply = round(current_stock / weekly_qty, 1) if weekly_qty > 0 else 99
        net_to_order = max(0, total_qty_needed - current_stock)
        total_comp_cost = round(net_to_order * comp["unit_cost"], 2)
        total_material_cost += total_comp_cost

        # Determine alert
        alert = None
        if current_stock <= reorder_point:
            alert = "BELOW REORDER POINT — order immediately"
        elif weeks_of_supply < planning_weeks:
            alert = f"STOCK RUNS OUT in {weeks_of_supply} weeks — order within {max(1, round(weeks_of_supply - comp['lead_time_days']/7, 1))} weeks"

        if alert:
            component_alerts.append({
                "component_id": comp["component_id"],
                "name": comp["component_name"],
                "alert": alert,
                "current_stock": current_stock,
                "weeks_of_supply": weeks_of_supply,
                "lead_time_days": comp["lead_time_days"],
            })

        weekly_requirements.append({
            "component_id": comp["component_id"],
            "component_name": comp["component_name"],
            "supplier": comp["supplier"],
            "qty_per_unit": qty_per_unit,
            "weekly_qty_needed": weekly_qty,
            "total_qty_needed": total_qty_needed,
            "current_stock": current_stock,
            "weeks_of_supply": weeks_of_supply,
            "net_qty_to_order": net_to_order,
            "unit_cost": comp["unit_cost"],
            "total_order_cost": total_comp_cost,
            "lead_time_days": comp["lead_time_days"],
            "reorder_point": reorder_point,
            "below_reorder_point": current_stock <= reorder_point,
            "alert": alert,
        })

    result = {
        "product_id": bom["product_id"],
        "production_plan": {
            "weekly_units": weekly_units_to_produce,
            "planning_weeks": planning_weeks,
            "total_units": total_units,
        },
        "material_requirements": weekly_requirements,
        "procurement_summary": {
            "total_components": len(weekly_requirements),
            "components_needing_order": sum(1 for r in weekly_requirements if r["net_qty_to_order"] > 0),
            "components_below_reorder": sum(1 for r in weekly_requirements if r["below_reorder_point"]),
            "total_material_cost_to_order": round(total_material_cost, 2),
            "component_alerts": component_alerts,
        },
        "cross_agent_output_for_supplier": {
            "source_agent": "production_planning",
            "message": "Supplier Agent: initiate procurement for the following components",
            "urgent_orders": [
                {
                    "component_id": r["component_id"],
                    "name": r["component_name"],
                    "supplier": r["supplier"],
                    "qty_to_order": r["net_qty_to_order"],
                    "lead_time_days": r["lead_time_days"],
                    "urgency": "HIGH" if r["below_reorder_point"] else "STANDARD",
                }
                for r in weekly_requirements if r["net_qty_to_order"] > 0
            ],
        },
    }

    return json.dumps(result, indent=2, default=str)
