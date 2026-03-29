"""
Supplier & Procurement Tools
These are the ALGORITHMS the Supplier & Procurement Agent uses as tools.
The LLM decides WHEN to call them, INTERPRETS the results, and REASONS about them.
"""
import json
import math
import random
from langchain_core.tools import tool
from data.database_queries import (
    get_supplier_performance,
    get_bill_of_materials,
    get_reorder_history,
    get_open_purchase_orders,
    get_supplier_contracts,
    get_supply_chain_risk_factors,
)


@tool
def get_procurement_context(product_id: str = "PROD-A") -> str:
    """
    Consolidate all procurement-relevant data: current component stock levels,
    open purchase orders in transit, supplier performance, contract terms,
    and incoming material pipeline.

    Use this as the FIRST tool call to understand the full procurement picture
    before evaluating suppliers or generating purchase orders.

    Args:
        product_id: The product to assess procurement for (default: PROD-A)
    """
    bom = get_bill_of_materials(product_id)
    suppliers = get_supplier_performance(product_id)
    contracts = get_supplier_contracts()
    open_pos = get_open_purchase_orders(product_id)
    reorder_hist = get_reorder_history(product_id)

    # Pipeline value: what's already ordered and coming
    pipeline_by_component = {}
    for po in open_pos:
        cid = po["component_id"]
        if cid not in pipeline_by_component:
            pipeline_by_component[cid] = {"qty": 0, "pos": []}
        pipeline_by_component[cid]["qty"] += po["quantity_ordered"]
        pipeline_by_component[cid]["pos"].append(po["po_id"])

    # Component health summary
    component_status = []
    if bom:
        for comp in bom.get("components", []):
            cid = comp["component_id"]
            pipeline = pipeline_by_component.get(cid, {}).get("qty", 0)
            effective_stock = comp["current_stock_units"] + pipeline
            weeks_supply = round(effective_stock / max(1, comp["qty_per_unit"] * 980), 2)  # 980 weekly
            below_rop = comp["current_stock_units"] <= comp["reorder_point"]

            component_status.append({
                "component_id": cid,
                "name": comp["component_name"],
                "supplier": comp["supplier"],
                "current_stock": comp["current_stock_units"],
                "open_po_qty": pipeline,
                "effective_stock": effective_stock,
                "reorder_point": comp["reorder_point"],
                "below_reorder_point": below_rop,
                "weeks_of_supply_effective": weeks_supply,
                "unit_cost": comp["unit_cost"],
                "lead_time_days": comp["lead_time_days"],
            })

    # Supplier scorecards
    supplier_summary = []
    for sup in suppliers:
        contract = next((c for c in contracts if c["supplier_id"] == sup["supplier_id"]), {})
        last_orders = [r for r in reorder_hist if r["supplier"] == sup["supplier_name"]]
        avg_actual_lt = round(
            sum(o["lead_time_actual"] for o in last_orders) / len(last_orders), 1
        ) if last_orders else None

        supplier_summary.append({
            "supplier_id": sup["supplier_id"],
            "supplier_name": sup["supplier_name"],
            "on_time_delivery_pct": sup["on_time_delivery_pct"],
            "quality_reject_rate_pct": sup["quality_reject_rate_pct"],
            "avg_lead_time_days": sup["avg_lead_time_days"],
            "lead_time_variability_days": sup["lead_time_std_dev_days"],
            "avg_actual_lead_time_recent": avg_actual_lt,
            "contract_status": contract.get("status", "unknown"),
            "contract_expiry": contract.get("contract_end"),
            "payment_terms": contract.get("payment_terms"),
            "preferred": contract.get("preferred_supplier", False),
            "annual_spend_ytd": contract.get("annual_spend_ytd"),
        })

    # Open PO summary
    open_po_summary = {
        "total_open_pos": len(open_pos),
        "total_open_value": round(sum(po["total_cost"] for po in open_pos), 2),
        "components_on_order": list(set(po["component_id"] for po in open_pos)),
        "pos_detail": open_pos,
    }

    # Reorder performance: how often did we order on time?
    late_orders = sum(1 for o in reorder_hist if o["lead_time_actual"] > (o["lead_time_actual"] + 1))
    result = {
        "product_id": product_id,
        "component_status": component_status,
        "supplier_summary": supplier_summary,
        "open_purchase_orders": open_po_summary,
        "procurement_health": {
            "components_below_reorder": sum(1 for c in component_status if c["below_reorder_point"]),
            "components_with_open_po": len(open_po_summary["components_on_order"]),
            "total_pipeline_value": open_po_summary["total_open_value"],
            "recent_reorder_count": len(reorder_hist),
        },
    }

    return json.dumps(result, indent=2, default=str)


@tool
def evaluate_supplier_options(
    component_id: str = "SH-100",
    quantity_needed: int = 1000,
    required_by_days: int = 7,
) -> str:
    """
    Compare all qualified suppliers for a specific component.
    Scores each supplier on cost, lead time, reliability, and quality.
    Applies volume discounts from contracts and flags feasibility
    based on required delivery date.

    Use this BEFORE placing any order to ensure you select the best supplier
    for the specific situation.

    Args:
        component_id: Component to source (e.g., SH-100, VSA-200)
        quantity_needed: Units to order
        required_by_days: How many days until we need delivery
    """
    bom = get_bill_of_materials()
    contracts = get_supplier_contracts()
    suppliers = get_supplier_performance()
    risk_data = get_supply_chain_risk_factors()

    # Find component in BOM
    comp = None
    if bom:
        for c in bom.get("components", []):
            if c["component_id"] == component_id:
                comp = c
                break

    if not comp:
        return json.dumps({"error": f"Component {component_id} not found in BOM"})

    risk = next((r for r in risk_data if r["component_id"] == component_id), {})
    qualified = risk.get("qualified_suppliers", [comp["supplier"]])

    options = []
    for sup in suppliers:
        # Check if this supplier is qualified for this component
        if sup["supplier_name"] not in qualified and sup["supplier_id"] not in qualified:
            continue

        contract = next((c for c in contracts if c["supplier_id"] == sup["supplier_id"]), None)

        # Get base unit cost for this component from contract
        if contract:
            base_cost = contract["base_unit_cost_by_component"].get(component_id, comp["unit_cost"])
        else:
            base_cost = comp["unit_cost"]

        # Apply volume discount
        discount_pct = 0.0
        if contract:
            for tier in sorted(contract.get("volume_discount_tiers", []), key=lambda x: x["min_units_per_order"], reverse=True):
                if quantity_needed >= tier["min_units_per_order"]:
                    discount_pct = tier["discount_pct"]
                    break
        discounted_cost = round(base_cost * (1 - discount_pct / 100), 4)
        total_cost = round(discounted_cost * quantity_needed, 2)

        # Lead time feasibility
        avg_lt = sup["avg_lead_time_days"]
        lt_std = sup["lead_time_std_dev_days"]
        feasible = avg_lt <= required_by_days
        on_time_prob = max(0.1, sup["on_time_delivery_pct"] / 100)

        # If lead time is tight, on-time probability drops
        if required_by_days < avg_lt + lt_std:
            on_time_prob *= 0.7

        # Composite score (lower is better): cost weight 40%, reliability 40%, quality 20%
        # Normalize: cost on a 0-100 scale relative to cheapest option
        cost_score = discounted_cost  # raw for now; normalized after all options collected
        reliability_score = 100 - sup["on_time_delivery_pct"]   # lower = more reliable
        quality_score = sup["quality_reject_rate_pct"] * 10

        options.append({
            "supplier_id": sup["supplier_id"],
            "supplier_name": sup["supplier_name"],
            "qualified": True,
            "unit_cost_base": base_cost,
            "volume_discount_pct": discount_pct,
            "unit_cost_discounted": discounted_cost,
            "total_order_cost": total_cost,
            "savings_vs_list": round((base_cost - discounted_cost) * quantity_needed, 2),
            "avg_lead_time_days": avg_lt,
            "lead_time_std_dev_days": lt_std,
            "feasible_for_required_date": feasible,
            "on_time_probability_pct": round(on_time_prob * 100, 1),
            "quality_reject_rate_pct": sup["quality_reject_rate_pct"],
            "on_time_delivery_pct": sup["on_time_delivery_pct"],
            "_cost_score": cost_score,
            "_reliability_score": reliability_score,
            "_quality_score": quality_score,
        })

    if not options:
        return json.dumps({"error": f"No qualified suppliers found for {component_id}"})

    # Normalize cost scores (cheapest = 0, most expensive = 100)
    min_cost = min(o["_cost_score"] for o in options)
    max_cost = max(o["_cost_score"] for o in options)
    cost_range = max(0.01, max_cost - min_cost)

    for o in options:
        normalized_cost = (o["_cost_score"] - min_cost) / cost_range * 100
        o["composite_score"] = round(
            normalized_cost * 0.40 +
            o["_reliability_score"] * 0.40 +
            o["_quality_score"] * 0.20, 1
        )
        del o["_cost_score"], o["_reliability_score"], o["_quality_score"]

    # Sort: feasible first, then by composite score
    options.sort(key=lambda x: (not x["feasible_for_required_date"], x["composite_score"]))

    result = {
        "component_id": component_id,
        "component_name": comp["component_name"],
        "quantity_needed": quantity_needed,
        "required_by_days": required_by_days,
        "supply_risk_score": risk.get("risk_score", 0),
        "sourcing_type": risk.get("sourcing_type", "unknown"),
        "risk_flag": risk.get("risk_flag"),
        "supplier_options": options,
        "recommended_supplier": options[0]["supplier_id"] if options else None,
        "recommended_reason": (
            f"Best composite score ({options[0]['composite_score']}) — "
            f"unit cost ${options[0]['unit_cost_discounted']} with "
            f"{options[0]['on_time_delivery_pct']}% on-time delivery"
            if options else "No qualified supplier found"
        ),
    }

    return json.dumps(result, indent=2, default=str)


@tool
def generate_purchase_orders(
    weekly_production_target: int = 980,
    planning_weeks: int = 4,
    urgency_override: str = "standard",
) -> str:
    """
    Generate purchase orders for all components that need replenishment
    to support the production plan. Applies optimal supplier selection
    per component (based on cost, lead time, and contract terms).
    Flags urgent orders separately from standard orders.

    This is the primary output of the Supplier Agent — the actual
    procurement action list.

    Args:
        weekly_production_target: Weekly units to produce (from Production Agent MPS)
        planning_weeks: Horizon to cover
        urgency_override: 'standard' or 'urgent' (urgent = fastest supplier regardless of cost)
    """
    bom = get_bill_of_materials()
    suppliers = get_supplier_performance()
    contracts = get_supplier_contracts()
    open_pos = get_open_purchase_orders()
    risk_data = get_supply_chain_risk_factors()

    if not bom:
        return json.dumps({"error": "BOM not found"})

    total_units = weekly_production_target * planning_weeks
    purchase_orders = []
    urgent_orders = []
    total_po_value = 0.0

    # Pipeline: qty already on order per component
    pipeline = {po["component_id"]: po["quantity_ordered"] for po in open_pos}

    for comp in bom.get("components", []):
        cid = comp["component_id"]
        qty_per_unit = comp["qty_per_unit"]
        total_needed = total_units * qty_per_unit
        on_hand = comp["current_stock_units"]
        in_pipeline = pipeline.get(cid, 0)
        net_to_order = max(0, total_needed - on_hand - in_pipeline)

        # Add safety buffer (10% of planning horizon need)
        safety_buffer = round(total_needed * 0.10)
        net_to_order_with_buffer = net_to_order + safety_buffer

        if net_to_order_with_buffer <= 0:
            continue

        # Select supplier
        risk = next((r for r in risk_data if r["component_id"] == cid), {})
        qualified = risk.get("qualified_suppliers", [comp["supplier"]])

        best_sup = None
        best_cost = float("inf")
        for sup in suppliers:
            if sup["supplier_name"] not in qualified and sup["supplier_id"] not in qualified:
                continue
            if net_to_order_with_buffer < sup["min_order_quantity"]:
                continue
            if net_to_order_with_buffer > sup["max_order_quantity"]:
                continue

            contract = next((c for c in contracts if c["supplier_id"] == sup["supplier_id"]), None)
            base_cost = contract["base_unit_cost_by_component"].get(cid, comp["unit_cost"]) if contract else comp["unit_cost"]

            discount_pct = 0.0
            if contract:
                for tier in sorted(contract.get("volume_discount_tiers", []), key=lambda x: x["min_units_per_order"], reverse=True):
                    if net_to_order_with_buffer >= tier["min_units_per_order"]:
                        discount_pct = tier["discount_pct"]
                        break
            final_cost = base_cost * (1 - discount_pct / 100)

            # If urgent: prefer fastest lead time over cost
            if urgency_override == "urgent":
                score = sup["avg_lead_time_days"]
            else:
                score = final_cost * 0.6 + sup["avg_lead_time_days"] * 0.4

            if score < best_cost or best_sup is None:
                best_cost = score
                best_sup = {
                    "supplier": sup,
                    "unit_cost": round(final_cost, 4),
                    "discount_pct": discount_pct,
                    "lead_time": sup["avg_lead_time_days"],
                }

        if not best_sup:
            # Fallback: use default supplier from BOM
            best_sup = {
                "supplier": {"supplier_name": comp["supplier"], "supplier_id": comp["supplier"], "avg_lead_time_days": comp["lead_time_days"]},
                "unit_cost": comp["unit_cost"],
                "discount_pct": 0.0,
                "lead_time": comp["lead_time_days"],
            }

        total_cost = round(best_sup["unit_cost"] * net_to_order_with_buffer, 2)
        total_po_value += total_cost

        is_urgent = on_hand <= comp["reorder_point"] or urgency_override == "urgent"

        po = {
            "component_id": cid,
            "component_name": comp["component_name"],
            "supplier_id": best_sup["supplier"]["supplier_id"],
            "supplier_name": best_sup["supplier"]["supplier_name"],
            "quantity_to_order": net_to_order_with_buffer,
            "unit_cost": best_sup["unit_cost"],
            "volume_discount_pct": best_sup["discount_pct"],
            "total_cost": total_cost,
            "lead_time_days": best_sup["lead_time"],
            "expected_delivery_days_from_now": best_sup["lead_time"],
            "urgency": "URGENT" if is_urgent else "STANDARD",
            "reason": (
                f"Below reorder point ({on_hand} on hand, ROP={comp['reorder_point']})"
                if on_hand <= comp["reorder_point"] else
                f"Insufficient stock for {planning_weeks}-week plan ({on_hand} on hand + {in_pipeline} in pipeline, need {total_needed})"
            ),
            "open_po_pipeline": in_pipeline,
            "stock_on_hand": on_hand,
        }
        purchase_orders.append(po)
        if is_urgent:
            urgent_orders.append(po["component_id"])

    purchase_orders.sort(key=lambda x: (x["urgency"] != "URGENT", x["component_id"]))

    result = {
        "purchase_order_run": {
            "weekly_production_target": weekly_production_target,
            "planning_weeks": planning_weeks,
            "total_units_to_produce": total_units,
            "urgency_mode": urgency_override,
        },
        "purchase_orders": purchase_orders,
        "po_summary": {
            "total_pos_to_place": len(purchase_orders),
            "urgent_pos": len(urgent_orders),
            "standard_pos": len(purchase_orders) - len(urgent_orders),
            "total_procurement_value": round(total_po_value, 2),
            "urgent_component_ids": urgent_orders,
        },
        "cross_agent_output_for_orchestrator": {
            "source_agent": "supplier_procurement",
            "pos_placed": len(purchase_orders),
            "total_value": round(total_po_value, 2),
            "urgent_items": urgent_orders,
            "earliest_delivery_days": min((po["lead_time_days"] for po in purchase_orders), default=0),
            "latest_delivery_days": max((po["lead_time_days"] for po in purchase_orders), default=0),
        },
    }

    return json.dumps(result, indent=2, default=str)


@tool
def assess_supply_chain_risk() -> str:
    """
    Evaluate the overall supply chain risk across all components.
    Identifies single-source dependencies, geographic concentration,
    supplier financial risk, and contract expiry risks.
    Scores each component and the overall supply chain resilience.

    Use this to flag strategic risks beyond just the current order cycle.
    Critical findings should be escalated to the Orchestrator.

    """
    risk_data = get_supply_chain_risk_factors()
    contracts = get_supplier_contracts()
    suppliers = get_supplier_performance()

    # Contract expiry warnings
    contract_risks = []
    for contract in contracts:
        days_left = contract.get("contract_renewal_due_in_days")
        if days_left and days_left < 180:
            contract_risks.append({
                "supplier_id": contract["supplier_id"],
                "supplier_name": contract["supplier_name"],
                "expiry_date": contract["contract_end"],
                "days_until_expiry": days_left,
                "severity": "HIGH" if days_left < 60 else "MEDIUM",
            })

    # Supplier performance risks
    performance_risks = []
    for sup in suppliers:
        if sup["on_time_delivery_pct"] < 88:
            performance_risks.append({
                "supplier_id": sup["supplier_id"],
                "on_time_pct": sup["on_time_delivery_pct"],
                "quality_reject_pct": sup["quality_reject_rate_pct"],
                "severity": "HIGH" if sup["on_time_delivery_pct"] < 82 else "MEDIUM",
                "note": f"On-time delivery {sup['on_time_delivery_pct']}% — below 88% threshold",
            })

    # Component risk summary
    high_risk = [r for r in risk_data if r["risk_score"] >= 60]
    medium_risk = [r for r in risk_data if 30 <= r["risk_score"] < 60]
    low_risk = [r for r in risk_data if r["risk_score"] < 30]

    # Overall supply chain resilience score (0-100, higher = more resilient)
    avg_risk = sum(r["risk_score"] for r in risk_data) / len(risk_data) if risk_data else 50
    resilience_score = round(100 - avg_risk)

    # Single-source count
    single_source = [r for r in risk_data if r["sourcing_type"] == "single_source"]

    result = {
        "supply_chain_risk_assessment": {
            "overall_resilience_score": resilience_score,
            "resilience_rating": (
                "STRONG" if resilience_score >= 75 else
                "MODERATE" if resilience_score >= 55 else
                "WEAK — action required"
            ),
            "total_components_assessed": len(risk_data),
            "high_risk_components": len(high_risk),
            "medium_risk_components": len(medium_risk),
            "low_risk_components": len(low_risk),
            "single_source_components": len(single_source),
        },
        "high_risk_components": [
            {
                "component_id": r["component_id"],
                "name": r["component_name"],
                "risk_score": r["risk_score"],
                "sourcing_type": r["sourcing_type"],
                "risk_flag": r["risk_flag"],
                "mitigation": r["mitigation"],
                "qualified_suppliers": r["qualified_suppliers"],
                "weeks_to_qualify_alternative": r["alternative_supplier_qualification_weeks"],
            }
            for r in high_risk
        ],
        "medium_risk_components": [
            {
                "component_id": r["component_id"],
                "name": r["component_name"],
                "risk_score": r["risk_score"],
                "sourcing_type": r["sourcing_type"],
                "risk_flag": r["risk_flag"],
            }
            for r in medium_risk
        ],
        "contract_risks": contract_risks,
        "supplier_performance_risks": performance_risks,
        "top_mitigation_actions": [
            {
                "priority": i + 1,
                "component_id": r["component_id"],
                "action": r["mitigation"],
                "risk_score": r["risk_score"],
            }
            for i, r in enumerate(sorted(high_risk, key=lambda x: -x["risk_score"]))
        ],
        "escalation_to_orchestrator": {
            "requires_escalation": len(high_risk) > 0 or len(contract_risks) > 0,
            "reason": (
                f"{len(high_risk)} high-risk components and {len(contract_risks)} contract expiry warnings"
                if high_risk or contract_risks else "No immediate escalation needed"
            ),
        },
    }

    return json.dumps(result, indent=2, default=str)


@tool
def simulate_delivery_risk(
    component_id: str = "SH-100",
    supplier_id: str = "SUP-A",
    order_quantity: int = 600,
    required_by_days: int = 7,
    simulations: int = 1000,
) -> str:
    """
    Run a Monte Carlo simulation of delivery risk for a specific order.
    Simulates lead time variability using the supplier's historical performance
    to calculate the probability of on-time delivery.

    Use this for URGENT orders or high-risk components to quantify the
    probability of a stockout before the delivery arrives.

    Args:
        component_id: Component being ordered
        supplier_id: Supplier to simulate
        order_quantity: Units ordered
        required_by_days: Days until we need the component
        simulations: Monte Carlo runs (default: 1000)
    """
    suppliers = get_supplier_performance()
    bom = get_bill_of_materials()
    risk_data = get_supply_chain_risk_factors()

    sup = next((s for s in suppliers if s["supplier_id"] == supplier_id), None)
    if not sup:
        return json.dumps({"error": f"Supplier {supplier_id} not found"})

    comp = None
    if bom:
        for c in bom.get("components", []):
            if c["component_id"] == component_id:
                comp = c
                break

    if not comp:
        return json.dumps({"error": f"Component {component_id} not found"})

    risk = next((r for r in risk_data if r["component_id"] == component_id), {})

    avg_lt = sup["avg_lead_time_days"]
    lt_std = sup["lead_time_std_dev_days"]
    base_on_time_pct = sup["on_time_delivery_pct"] / 100

    # Monte Carlo simulation
    on_time_count = 0
    early_count = 0
    late_count = 0
    delay_days_list = []
    actual_lts = []

    for _ in range(simulations):
        # Simulate lead time from normal distribution
        actual_lt = max(1.0, random.gauss(avg_lt, lt_std))
        actual_lts.append(actual_lt)

        # On-time delivery check (supplier may still be late even within LT window)
        rand_otd = random.random()
        is_on_time_supplier = rand_otd < base_on_time_pct

        if not is_on_time_supplier:
            # Late: add extra 1-3 days delay
            actual_lt += random.uniform(1, 3)

        if actual_lt <= required_by_days:
            on_time_count += 1
            if actual_lt < required_by_days - 1:
                early_count += 1
        else:
            late_count += 1
            delay_days_list.append(actual_lt - required_by_days)

    on_time_pct = round(on_time_count / simulations * 100, 1)
    late_pct = round(late_count / simulations * 100, 1)
    avg_delay = round(sum(delay_days_list) / len(delay_days_list), 1) if delay_days_list else 0
    max_delay = round(max(delay_days_list), 1) if delay_days_list else 0

    # Financial impact of late delivery
    stockout_cost_per_day = 45.00 * 980 / 7  # 45 per unit stockout * 140 units/day
    expected_stockout_cost = round(avg_delay * stockout_cost_per_day * (late_pct / 100), 2)

    # Percentiles
    sorted_lts = sorted(actual_lts)
    p50 = sorted_lts[int(simulations * 0.50)]
    p90 = sorted_lts[int(simulations * 0.90)]
    p95 = sorted_lts[int(simulations * 0.95)]

    result = {
        "simulation": {
            "component_id": component_id,
            "component_name": comp["component_name"],
            "supplier_id": supplier_id,
            "supplier_name": sup["supplier_name"],
            "order_quantity": order_quantity,
            "required_by_days": required_by_days,
            "simulations_run": simulations,
        },
        "delivery_risk": {
            "on_time_probability_pct": on_time_pct,
            "late_probability_pct": late_pct,
            "early_delivery_pct": round(early_count / simulations * 100, 1),
            "risk_level": (
                "LOW" if late_pct < 10 else
                "MEDIUM" if late_pct < 25 else
                "HIGH" if late_pct < 45 else
                "CRITICAL"
            ),
        },
        "lead_time_distribution": {
            "avg_lead_time_days": round(sum(actual_lts) / simulations, 1),
            "p50_lead_time_days": round(p50, 1),
            "p90_lead_time_days": round(p90, 1),
            "p95_lead_time_days": round(p95, 1),
            "min_simulated_days": round(min(actual_lts), 1),
            "max_simulated_days": round(max(actual_lts), 1),
        },
        "late_delivery_impact": {
            "avg_delay_if_late_days": avg_delay,
            "max_delay_days": max_delay,
            "expected_stockout_cost": expected_stockout_cost,
        },
        "component_risk_context": {
            "sourcing_type": risk.get("sourcing_type", "unknown"),
            "supply_risk_score": risk.get("risk_score", 0),
            "backup_supplier_available": risk.get("sourcing_type") in ("dual_source", "multi_source"),
        },
        "recommendation": (
            "Order immediately with buffer stock as backup" if on_time_pct < 75 else
            "Standard order — low risk, proceed" if on_time_pct >= 90 else
            "Monitor closely — consider placing order early to add buffer"
        ),
    }

    return json.dumps(result, indent=2, default=str)


@tool
def optimize_supplier_allocation(
    component_id: str = "VSA-200",
    total_qty_needed: int = 1500,
    planning_weeks: int = 4,
) -> str:
    """
    Determine the optimal split of an order between qualified suppliers.
    Balances cost savings (cheaper supplier) against reliability risk
    (supplier performance and lead time variability).

    Evaluates multiple allocation splits and recommends the one with
    the best cost-risk tradeoff. Used for dual-source components.

    Args:
        component_id: Component to allocate (must be dual or multi-source)
        total_qty_needed: Total units to order
        planning_weeks: Planning horizon
    """
    suppliers = get_supplier_performance()
    contracts = get_supplier_contracts()
    bom = get_bill_of_materials()
    risk_data = get_supply_chain_risk_factors()

    comp = None
    if bom:
        for c in bom.get("components", []):
            if c["component_id"] == component_id:
                comp = c
                break

    if not comp:
        return json.dumps({"error": f"Component {component_id} not found"})

    risk = next((r for r in risk_data if r["component_id"] == component_id), {})
    qualified = risk.get("qualified_suppliers", [comp["supplier"]])

    qualified_suppliers = [
        s for s in suppliers
        if s["supplier_name"] in qualified or s["supplier_id"] in qualified
    ]

    if len(qualified_suppliers) < 2:
        return json.dumps({
            "component_id": component_id,
            "note": "Only one qualified supplier — no allocation optimization possible",
            "single_supplier": qualified_suppliers[0]["supplier_id"] if qualified_suppliers else None,
        })

    sup_a = qualified_suppliers[0]
    sup_b = qualified_suppliers[1]

    def get_unit_cost(sup, qty):
        contract = next((c for c in contracts if c["supplier_id"] == sup["supplier_id"]), None)
        base = contract["base_unit_cost_by_component"].get(component_id, comp["unit_cost"]) if contract else comp["unit_cost"]
        disc = 0.0
        if contract:
            for tier in sorted(contract.get("volume_discount_tiers", []), key=lambda x: x["min_units_per_order"], reverse=True):
                if qty >= tier["min_units_per_order"]:
                    disc = tier["discount_pct"]
                    break
        return round(base * (1 - disc / 100), 4)

    # Evaluate splits: 100/0, 80/20, 70/30, 60/40, 50/50, 40/60, 30/70
    splits = [
        (1.0, 0.0), (0.80, 0.20), (0.70, 0.30),
        (0.60, 0.40), (0.50, 0.50), (0.40, 0.60), (0.30, 0.70),
    ]

    allocation_analysis = []
    for split_a, split_b in splits:
        qty_a = round(total_qty_needed * split_a)
        qty_b = total_qty_needed - qty_a

        if qty_a > 0 and qty_a < sup_a["min_order_quantity"]:
            continue
        if qty_b > 0 and qty_b < sup_b["min_order_quantity"]:
            continue

        cost_a = get_unit_cost(sup_a, qty_a) * qty_a if qty_a > 0 else 0
        cost_b = get_unit_cost(sup_b, qty_b) * qty_b if qty_b > 0 else 0
        total_cost = round(cost_a + cost_b, 2)

        # Weighted reliability = portion-weighted on-time %
        weighted_otd = (
            (split_a * sup_a["on_time_delivery_pct"] + split_b * sup_b["on_time_delivery_pct"])
            if split_b > 0 else sup_a["on_time_delivery_pct"]
        )

        # Weighted lead time
        weighted_lt = (
            split_a * sup_a["avg_lead_time_days"] + split_b * sup_b["avg_lead_time_days"]
            if split_b > 0 else sup_a["avg_lead_time_days"]
        )

        # Concentration risk penalty (100% single source = high risk)
        concentration_risk = max(split_a, split_b) * 100  # higher = more concentrated

        allocation_analysis.append({
            "split": f"{round(split_a*100)}/{round(split_b*100)}",
            "supplier_a_pct": round(split_a * 100),
            "supplier_b_pct": round(split_b * 100),
            "qty_supplier_a": qty_a,
            "qty_supplier_b": qty_b,
            "total_cost": total_cost,
            "weighted_on_time_pct": round(weighted_otd, 1),
            "weighted_lead_time_days": round(weighted_lt, 1),
            "concentration_risk_pct": round(concentration_risk, 0),
        })

    # Find optimal: minimize cost while keeping reliability >= 90% and concentration <= 80%
    feasible = [a for a in allocation_analysis if a["weighted_on_time_pct"] >= 88 and a["concentration_risk_pct"] <= 80]
    if not feasible:
        feasible = allocation_analysis  # relax constraints

    optimal = min(feasible, key=lambda x: x["total_cost"])

    # Compare vs single-source cost
    single_source_cost = round(get_unit_cost(sup_a, total_qty_needed) * total_qty_needed, 2)
    savings_vs_single = round(single_source_cost - optimal["total_cost"], 2)

    result = {
        "component_id": component_id,
        "component_name": comp["component_name"],
        "total_qty_needed": total_qty_needed,
        "suppliers_compared": [
            {
                "supplier_id": s["supplier_id"],
                "name": s["supplier_name"],
                "on_time_pct": s["on_time_delivery_pct"],
                "lead_time_days": s["avg_lead_time_days"],
                "unit_cost": get_unit_cost(s, total_qty_needed // 2),
            }
            for s in qualified_suppliers
        ],
        "allocation_analysis": allocation_analysis,
        "recommended_allocation": {
            "split": optimal["split"],
            "qty_supplier_a": optimal["qty_supplier_a"],
            "qty_supplier_b": optimal["qty_supplier_b"],
            "total_cost": optimal["total_cost"],
            "weighted_on_time_pct": optimal["weighted_on_time_pct"],
            "savings_vs_single_source": savings_vs_single,
        },
        "recommendation_reason": (
            f"Split {optimal['split']} minimizes cost (${optimal['total_cost']}) "
            f"while maintaining {optimal['weighted_on_time_pct']}% weighted on-time delivery "
            f"and limiting concentration risk to {optimal['concentration_risk_pct']}%"
        ),
    }

    return json.dumps(result, indent=2, default=str)
