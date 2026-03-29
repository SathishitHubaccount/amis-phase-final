"""
Helper methods for creating approval decisions
"""
from approval_system import get_approval_system, RiskLevel


def create_forecast_decision(product_id: str, demand_output: dict, weeks: int):
    """Create decision for demand forecast updates"""
    approval_system = get_approval_system()

    base_weekly = demand_output.get("scenarios", {}).get("base", {}).get("weekly_avg", 0)

    return approval_system.create_decision(
        decision_type="demand_forecast_update",
        action=f"Update demand forecast for {product_id}",
        description=f"AI recommends updating forecast to {base_weekly} units/week for next {weeks} weeks",
        impact_analysis={
            "financial_impact": 0,  # Forecasts don't directly cost money
            "affects_production": False,
            "affects_safety": False,
            "data_type": "forecast",
            "product_id": product_id,
            "base_case": base_weekly
        },
        payload=demand_output
    )


def create_inventory_decision(product_id: str, inventory_output: dict):
    """Create decision for inventory parameter updates"""
    approval_system = get_approval_system()

    stockout_risk = inventory_output.get("stockout_probability_pct", 0)
    reorder_point = inventory_output.get("reorder_point_units", 0)
    total_to_order = inventory_output.get("total_units_to_order", 0)
    cost = inventory_output.get("total_procurement_cost", 0)

    return approval_system.create_decision(
        decision_type="inventory_adjustment",
        action=f"Update inventory parameters for {product_id}",
        description=f"AI recommends: Stockout risk {stockout_risk}%, Reorder point {reorder_point} units, Order {total_to_order} units (${cost:,.2f})",
        impact_analysis={
            "financial_impact": cost,
            "affects_production": stockout_risk > 15,  # High stockout risk affects production
            "affects_safety": False,
            "product_id": product_id,
            "stockout_risk": stockout_risk,
            "order_cost": cost
        },
        payload=inventory_output
    )


def create_production_decision(product_id: str, production_output: dict, weeks: int):
    """Create decision for production schedule changes"""
    approval_system = get_approval_system()

    weekly_target = production_output.get("weekly_production_target", 0)
    mps_summary = production_output.get("mps_summary", {})
    overtime_cost = mps_summary.get("total_overtime_and_contract_cost", 0)

    return approval_system.create_decision(
        decision_type="production_schedule_change",
        action=f"Update production schedule for {product_id}",
        description=f"AI recommends producing {weekly_target} units/week for next {weeks} weeks (Overtime cost: ${overtime_cost:,.2f})",
        impact_analysis={
            "financial_impact": overtime_cost,
            "affects_production": True,  # Always affects production
            "affects_safety": False,
            "product_id": product_id,
            "weekly_target": weekly_target,
            "overtime_required": overtime_cost > 0
        },
        payload=production_output
    )


def create_maintenance_decision(machine_output: dict):
    """Create decision for machine maintenance work orders"""
    approval_system = get_approval_system()

    critical_machines = machine_output.get("critical_machines", [])

    if not critical_machines:
        # No critical machines, return a no-op decision
        return approval_system.create_decision(
            decision_type="machine_maintenance",
            action="No maintenance required",
            description="AI detected no critical machine issues",
            impact_analysis={
                "financial_impact": 0,
                "affects_production": False,
                "affects_safety": False
            },
            payload=machine_output
        )

    # Estimate maintenance cost ($5K per machine)
    estimated_cost = len(critical_machines) * 5000

    return approval_system.create_decision(
        decision_type="machine_maintenance",
        action=f"Create maintenance work orders for {len(critical_machines)} machines",
        description=f"AI recommends immediate maintenance for: {', '.join(critical_machines)} (Est. cost: ${estimated_cost:,.2f})",
        impact_analysis={
            "financial_impact": estimated_cost,
            "affects_production": True,  # Maintenance causes downtime
            "affects_safety": True,  # High failure risk is a safety concern
            "critical_machines": critical_machines,
            "machine_count": len(critical_machines)
        },
        payload=machine_output
    )
