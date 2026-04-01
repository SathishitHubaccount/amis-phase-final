"""
Machine Health Tools
These are the ALGORITHMS the Machine Health Agent uses as tools.
The LLM decides WHEN to call them, INTERPRETS the results, and REASONS about them.
"""
import json
import math
import random
from langchain_core.tools import tool
from data.database_queries import (
    get_machine_fleet,
    get_sensor_readings,
    get_maintenance_history,
    get_oee_history,
)


@tool
def get_machine_fleet_status(plant_id: str = "PLANT-01") -> str:
    """
    Get the full machine fleet health overview for the plant.
    Returns each machine's status, health score, alert level, and a summary
    of critical alerts and current production capacity.

    Use this as the FIRST tool call to understand the full equipment picture
    before diving into individual machine analysis.

    Args:
        plant_id: The plant identifier (default: PLANT-01)
    """
    fleet = get_machine_fleet(plant_id)

    operational = [m for m in fleet if m["status"] == "operational"]
    down = [m for m in fleet if m["status"] == "down"]
    warning = [m for m in fleet if m["alert_level"] in ("warning", "critical")]
    caution = [m for m in fleet if m["alert_level"] == "caution"]

    # Production capacity accounting
    max_capacity = sum(m["max_output_units_per_day"] or 0 for m in fleet)
    current_capacity = sum(m["max_output_units_per_day"] or 0 for m in operational)

    # Capacity reduction from degraded machines
    capacity_reduction = 0
    for m in warning:
        # Warning machines run at ~75% efficiency
        capacity_reduction += (m["max_output_units_per_day"] or 0) * 0.25
    for m in caution:
        # Caution machines run at ~90% efficiency
        capacity_reduction += (m["max_output_units_per_day"] or 0) * 0.10

    effective_capacity = round(current_capacity - capacity_reduction)

    # Critical alerts
    alerts = []
    for m in fleet:
        if m["alert_level"] == "down":
            alerts.append({
                "severity": "CRITICAL",
                "machine_id": m["machine_id"],
                "machine_name": m["machine_name"],
                "message": m.get("downtime_reason", "Machine is down"),
                "estimated_return": m.get("estimated_return", "Unknown"),
            })
        elif m["alert_level"] == "warning":
            alerts.append({
                "severity": "WARNING",
                "machine_id": m["machine_id"],
                "machine_name": m["machine_name"],
                "message": f"Health score {m['health_score']}/100 — sensor anomalies detected, failure risk elevated",
                "next_maintenance": m["next_scheduled_maintenance"],
            })
        elif m["alert_level"] == "caution":
            alerts.append({
                "severity": "CAUTION",
                "machine_id": m["machine_id"],
                "machine_name": m["machine_name"],
                "message": f"Health score {m['health_score']}/100 — trending toward degradation, monitor closely",
                "next_maintenance": m["next_scheduled_maintenance"],
            })

    machine_summary = []
    for m in fleet:
        machine_summary.append({
            "machine_id": m["machine_id"],
            "name": m["machine_name"],
            "line": m["production_line"],
            "status": m["status"],
            "health_score": m["health_score"],
            "alert_level": m["alert_level"],
            "max_output_per_day": m["max_output_units_per_day"],
            "age_years": m["age_years"],
            "last_maintenance": m["last_maintenance_date"],
            "next_maintenance": m["next_scheduled_maintenance"],
        })

    result = {
        "plant_id": plant_id,
        "fleet_summary": {
            "total_machines": len(fleet),
            "operational": len(operational),
            "down": len(down),
            "on_warning": len(warning),
            "on_caution": len(caution),
            "fleet_health_avg_score": round(sum(m["health_score"] for m in fleet) / len(fleet), 1) if fleet else 0,
        },
        "production_capacity": {
            "theoretical_max_units_per_day": max_capacity,
            "current_operational_max_units_per_day": current_capacity,
            "effective_capacity_after_degradation_units_per_day": effective_capacity,
            "capacity_lost_to_downtime_units_per_day": max_capacity - current_capacity,
            "capacity_lost_to_degradation_units_per_day": round(capacity_reduction),
            "total_capacity_loss_pct": round((1 - effective_capacity / max_capacity) * 100, 1) if max_capacity else 0,
        },
        "active_alerts": alerts,
        "machines": machine_summary,
    }

    return json.dumps(result, indent=2, default=str)


@tool
def analyze_sensor_readings(machine_id: str, hours_back: int = 24) -> str:
    """
    Analyze the latest sensor readings for a specific machine.
    Compares current readings against baselines and thresholds,
    flags anomalies, calculates deviation percentages, and shows the
    7-day trend to detect whether conditions are worsening or stable.

    Use this AFTER get_machine_fleet_status to investigate machines
    with warning or caution alerts.

    Args:
        machine_id: Machine to analyze (e.g., MCH-001, MCH-002)
        hours_back: Lookback window in hours (default: 24)
    """
    data = get_sensor_readings(machine_id)
    fleet = get_machine_fleet()
    machine = next((m for m in fleet if m["machine_id"] == machine_id), None)

    if not machine:
        return json.dumps({"error": f"Machine {machine_id} not found"})

    if machine["status"] == "down":
        failure = data.get("failure_event", {})
        trend = data.get("trend_7_day", {})
        return json.dumps({
            "machine_id": machine_id,
            "machine_name": machine["machine_name"],
            "status": "DOWN",
            "failure_event": failure,
            "pre_failure_trend": trend,
            "note": "Machine is offline. Sensor data shows pre-failure escalation pattern.",
        }, indent=2)

    sensors = data.get("sensors", {})
    trend = data.get("trend_7_day", {})

    sensor_analysis = []
    anomalies = []

    for sensor_name, reading in sensors.items():
        baseline = reading["baseline"]
        current = reading["current"]
        high_thresh = reading.get("high_threshold")
        crit_thresh = reading.get("critical_threshold")
        unit = reading["unit"]

        deviation_pct = round(((current - baseline) / baseline) * 100, 1) if baseline else 0
        deviation_abs = round(current - baseline, 2)

        # Determine status
        status = "normal"
        if crit_thresh and current >= crit_thresh:
            status = "critical"
        elif high_thresh and current >= high_thresh:
            status = "warning"
        elif abs(deviation_pct) > 15:
            status = "caution"

        # Trend direction from 7-day data
        trend_values = trend.get(sensor_name, [])
        trend_filtered = [v for v in trend_values if v is not None]
        if len(trend_filtered) >= 3:
            recent_avg = sum(trend_filtered[-3:]) / 3
            earlier_avg = sum(trend_filtered[:3]) / 3
            if recent_avg > earlier_avg * 1.05:
                trend_direction = "rising"
            elif recent_avg < earlier_avg * 0.95:
                trend_direction = "falling"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "insufficient_data"

        entry = {
            "sensor": sensor_name,
            "unit": unit,
            "baseline": baseline,
            "current": current,
            "deviation_pct": deviation_pct,
            "deviation_abs": deviation_abs,
            "high_threshold": high_thresh,
            "critical_threshold": crit_thresh,
            "status": status,
            "trend_direction": trend_direction,
            "7_day_values": trend.get(sensor_name, []),
        }
        sensor_analysis.append(entry)

        if status in ("warning", "critical", "caution"):
            anomalies.append({
                "sensor": sensor_name,
                "status": status,
                "current_value": f"{current} {unit}",
                "baseline_value": f"{baseline} {unit}",
                "deviation": f"{'+' if deviation_pct > 0 else ''}{deviation_pct}%",
                "trend": trend_direction,
            })

    result = {
        "machine_id": machine_id,
        "machine_name": machine["machine_name"],
        "alert_level": machine["alert_level"],
        "health_score": machine["health_score"],
        "analysis_timestamp": data.get("timestamp"),
        "sensor_analysis": sensor_analysis,
        "anomalies_detected": anomalies,
        "anomaly_count": len(anomalies),
        "overall_sensor_status": (
            "critical" if any(a["status"] == "critical" for a in anomalies) else
            "warning" if any(a["status"] == "warning" for a in anomalies) else
            "caution" if anomalies else
            "normal"
        ),
    }

    return json.dumps(result, indent=2, default=str)


@tool
def predict_failure_risk(machine_id: str, horizon_days: int = 7) -> str:
    """
    Predict the probability of machine failure within the next N days using
    exponential failure distribution (MTBF-based) adjusted by current sensor
    degradation. Compares the cost of planned maintenance vs unplanned failure.

    Use this for any machine with caution/warning status to quantify WHEN
    and HOW LIKELY a failure is, and to justify maintenance decisions.

    Args:
        machine_id: Machine to assess (e.g., MCH-002)
        horizon_days: Forecast window in days (default: 7)
    """
    fleet = get_machine_fleet()
    machine = next((m for m in fleet if m["machine_id"] == machine_id), None)

    if not machine:
        return json.dumps({"error": f"Machine {machine_id} not found"})

    if machine["status"] == "down":
        return json.dumps({
            "machine_id": machine_id,
            "machine_name": machine["machine_name"],
            "status": "DOWN — already failed",
            "failure_probability_pct": 100.0,
            "note": "Machine is currently in corrective maintenance.",
            "estimated_return": machine.get("estimated_return"),
            "repair_cost": machine["maintenance_cost_per_event"],
            "production_lost_per_day": machine["unplanned_failure_cost_per_day"],
        }, indent=2)

    mtbf = machine["mtbf_days"]
    sensor_data = get_sensor_readings(machine_id)
    sensors = sensor_data.get("sensors", {})

    # Calculate sensor degradation factor
    # Each anomalous sensor shrinks the effective MTBF
    degradation_factor = 1.0
    sensor_flags = []

    for sensor_name, reading in sensors.items():
        baseline = reading["baseline"]
        current = reading["current"]
        high_thresh = reading.get("high_threshold")
        crit_thresh = reading.get("critical_threshold")

        if baseline and baseline > 0:
            dev_pct = abs((current - baseline) / baseline)

            if crit_thresh and current >= crit_thresh:
                degradation_factor *= 0.35
                sensor_flags.append(f"{sensor_name}: CRITICAL (reducing MTBF by 65%)")
            elif high_thresh and current >= high_thresh:
                degradation_factor *= 0.55
                sensor_flags.append(f"{sensor_name}: WARNING (reducing MTBF by 45%)")
            elif dev_pct > 0.20:
                degradation_factor *= 0.75
                sensor_flags.append(f"{sensor_name}: CAUTION +{round(dev_pct*100)}% above baseline (reducing MTBF by 25%)")

    effective_mtbf = max(1.0, mtbf * degradation_factor)

    # P(failure in next t days) = 1 - e^(-t / MTBF)  [exponential distribution]
    prob_failure = (1 - math.exp(-horizon_days / effective_mtbf)) * 100

    # Confidence intervals (using ±20% MTBF uncertainty)
    prob_low = (1 - math.exp(-horizon_days / (effective_mtbf * 1.20))) * 100
    prob_high = (1 - math.exp(-horizon_days / (effective_mtbf * 0.80))) * 100

    # Expected days to failure from now
    expected_days_to_failure = round(effective_mtbf * math.log(2), 1)  # median = MTBF * ln(2)

    # Risk category
    if prob_failure >= 40:
        risk_category = "CRITICAL"
    elif prob_failure >= 20:
        risk_category = "HIGH"
    elif prob_failure >= 8:
        risk_category = "MEDIUM"
    else:
        risk_category = "LOW"

    # Financial comparison
    planned_cost = machine["maintenance_cost_per_event"]
    unplanned_daily_cost = machine["unplanned_failure_cost_per_day"]
    avg_mttr = machine["mttr_days"]
    unplanned_total_cost = round(unplanned_daily_cost * avg_mttr + planned_cost * 1.5)  # repair + premium parts
    maintenance_history = get_maintenance_history(machine_id)
    unplanned_events = [e for e in maintenance_history if e["type"] == "unplanned"]

    result = {
        "machine_id": machine_id,
        "machine_name": machine["machine_name"],
        "current_health_score": machine["health_score"],
        "alert_level": machine["alert_level"],
        "failure_prediction": {
            "horizon_days": horizon_days,
            "failure_probability_pct": round(prob_failure, 1),
            "confidence_interval_pct": {
                "low": round(prob_low, 1),
                "high": round(prob_high, 1),
            },
            "risk_category": risk_category,
            "expected_median_days_to_failure": expected_days_to_failure,
            "original_mtbf_days": mtbf,
            "effective_mtbf_days": round(effective_mtbf, 1),
            "sensor_degradation_factor": round(degradation_factor, 3),
            "sensor_flags_applied": sensor_flags,
        },
        "financial_impact": {
            "planned_maintenance_cost": planned_cost,
            "unplanned_failure_total_cost": unplanned_total_cost,
            "cost_of_inaction": unplanned_total_cost - planned_cost,
            "expected_downtime_if_fails": f"{avg_mttr} days",
            "production_loss_per_day_down": unplanned_daily_cost,
            "total_production_loss_if_fails": round(unplanned_daily_cost * avg_mttr),
        },
        "historical_context": {
            "unplanned_failures_in_history": len(unplanned_events),
            "last_unplanned_failure": unplanned_events[-1]["date"] if unplanned_events else "None on record",
        },
        "recommendation": (
            "IMMEDIATE maintenance required — failure imminent" if risk_category == "CRITICAL" else
            "Schedule maintenance within 48 hours" if risk_category == "HIGH" else
            "Schedule maintenance within this week" if risk_category == "MEDIUM" else
            "Monitor closely — maintenance at next scheduled window"
        ),
    }

    return json.dumps(result, indent=2, default=str)


@tool
def calculate_oee(machine_id: str, period_months: int = 1) -> str:
    """
    Calculate the Overall Equipment Effectiveness (OEE) for a machine.
    OEE = Availability × Performance × Quality Rate.
    World-class OEE = 85%. Below 65% is considered poor.

    Includes trend vs previous period and the top contributors to OEE loss.
    Use this to quantify how well a machine is running and identify the
    biggest improvement opportunity.

    Args:
        machine_id: Machine to evaluate (e.g., MCH-001)
        period_months: Number of recent months to analyze (default: 1 = last month)
    """
    fleet = get_machine_fleet()
    machine = next((m for m in fleet if m["machine_id"] == machine_id), None)

    if not machine:
        return json.dumps({"error": f"Machine {machine_id} not found"})

    oee_history = get_oee_history(machine_id, periods=6)
    maintenance_history = get_maintenance_history(machine_id)

    if not oee_history:
        return json.dumps({"error": f"No OEE data for {machine_id}"})

    # Current period OEE (last entry in history)
    current = oee_history[-1]
    availability = current["availability"]
    performance = current["performance"]
    quality = current["quality"]
    oee = current["oee"]

    # Previous period for trend
    previous = oee_history[-2] if len(oee_history) >= 2 else None
    oee_trend = round((oee - previous["oee"]) * 100, 2) if previous else None

    # 6-month OEE trend
    oee_values = [round(p["oee"] * 100, 1) for p in oee_history]
    avg_oee_6m = round(sum(oee_values) / len(oee_values), 1)

    # OEE loss breakdown (Six Big Losses framework)
    availability_loss = round((1 - availability) * 100, 1)
    performance_loss = round((1 - performance) * 100, 1)
    quality_loss = round((1 - quality) * 100, 1)

    # Convert to % of total possible output lost
    total_loss_pct = round((1 - oee) * 100, 1)
    avail_contrib = round(availability_loss / total_loss_pct * 100, 1) if total_loss_pct > 0 else 0
    perf_contrib = round(performance_loss / total_loss_pct * 100, 1) if total_loss_pct > 0 else 0
    qual_contrib = round(quality_loss / total_loss_pct * 100, 1) if total_loss_pct > 0 else 0

    # Maintenance events impact
    unplanned = [e for e in maintenance_history if e["type"] == "unplanned"]
    planned = [e for e in maintenance_history if e["type"] == "planned"]

    # Benchmark classification
    if oee >= 0.85:
        benchmark = "World Class (≥85%)"
    elif oee >= 0.75:
        benchmark = "Good (75-85%)"
    elif oee >= 0.65:
        benchmark = "Average (65-75%)"
    else:
        benchmark = "Poor (<65%) — significant improvement opportunity"

    # Projected output loss per day
    max_output = machine["max_output_units_per_day"] or 0
    actual_output = round(max_output * oee)
    lost_output = max_output - actual_output

    result = {
        "machine_id": machine_id,
        "machine_name": machine["machine_name"],
        "period": current["period"],
        "oee_current": {
            "oee_pct": round(oee * 100, 1),
            "availability_pct": round(availability * 100, 1),
            "performance_pct": round(performance * 100, 1),
            "quality_pct": round(quality * 100, 1),
            "benchmark_classification": benchmark,
        },
        "oee_trend": {
            "vs_previous_month_pct_points": oee_trend,
            "direction": "improving" if oee_trend and oee_trend > 0 else "declining" if oee_trend and oee_trend < 0 else "stable",
            "6_month_average_oee_pct": avg_oee_6m,
            "6_month_oee_history": [{"period": p["period"], "oee_pct": round(p["oee"]*100,1)} for p in oee_history],
        },
        "loss_analysis": {
            "total_oee_loss_pct": total_loss_pct,
            "availability_loss_pct": availability_loss,
            "performance_loss_pct": performance_loss,
            "quality_loss_pct": quality_loss,
            "biggest_loss_driver": (
                "Availability (downtime)" if avail_contrib >= perf_contrib and avail_contrib >= qual_contrib else
                "Performance (speed loss)" if perf_contrib >= qual_contrib else
                "Quality (defects/rework)"
            ),
        },
        "production_impact": {
            "max_possible_units_per_day": max_output,
            "actual_units_per_day_at_current_oee": actual_output,
            "units_lost_per_day_to_oee": lost_output,
            "units_lost_per_week": lost_output * 7,
        },
        "maintenance_context": {
            "unplanned_events_in_history": len(unplanned),
            "planned_events_in_history": len(planned),
            "total_unplanned_downtime_days": sum(e["duration_days"] for e in unplanned),
        },
    }

    return json.dumps(result, indent=2, default=str)


@tool
def generate_maintenance_schedule(
    planning_horizon_days: int = 14,
    production_demand_weekly: float = 1050.0,
) -> str:
    """
    Generate an optimized maintenance schedule for all machines that need attention.
    Balances maintenance urgency against production demand, minimizing production impact
    by scheduling maintenance during low-demand windows where possible.

    Compares cost of planned maintenance vs projected cost of failure for each machine.
    Use this to create an actionable maintenance plan and communicate windows to
    the Production Planning Agent.

    Args:
        planning_horizon_days: Number of days to plan ahead (default: 14)
        production_demand_weekly: Expected weekly production demand in units
    """
    fleet = get_machine_fleet()
    daily_demand = production_demand_weekly / 7

    schedule = []
    total_planned_cost = 0
    total_avoided_failure_cost = 0

    for machine in fleet:
        mid = machine["machine_id"]

        if machine["status"] == "down":
            # Already being repaired — include in schedule as-is
            schedule.append({
                "machine_id": mid,
                "machine_name": machine["machine_name"],
                "action": "CORRECTIVE MAINTENANCE IN PROGRESS",
                "urgency": "immediate",
                "recommended_window": f"Ongoing — est. return {machine.get('estimated_return', 'TBD')}",
                "maintenance_duration_days": machine["mttr_days"],
                "estimated_cost": machine["maintenance_cost_per_event"],
                "production_impact_units": round(machine["max_output_units_per_day"] * machine["mttr_days"]),
                "failure_already_occurred": True,
            })
            total_planned_cost += machine["maintenance_cost_per_event"]
            continue

        alert = machine["alert_level"]
        health = machine["health_score"]
        mtbf = machine["mtbf_days"]
        max_output = machine["max_output_units_per_day"] or 0

        # Determine urgency and window
        if alert == "warning":
            urgency = "high"
            days_until_maintenance = 2
            window = f"Within 2 days (by Day {days_until_maintenance})"
        elif alert == "caution":
            urgency = "medium"
            days_until_maintenance = 7
            window = f"Within 7 days (by Day {days_until_maintenance})"
        elif health < 85:
            urgency = "low"
            days_until_maintenance = min(planning_horizon_days, 14)
            window = f"Within {days_until_maintenance} days — as scheduled"
        else:
            urgency = "none"
            days_until_maintenance = None
            window = "No maintenance needed within planning horizon"

        if urgency == "none":
            schedule.append({
                "machine_id": mid,
                "machine_name": machine["machine_name"],
                "action": "NO ACTION REQUIRED",
                "urgency": "none",
                "recommended_window": window,
                "next_scheduled_maintenance": machine["next_scheduled_maintenance"],
            })
            continue

        # Production impact of taking machine offline for maintenance
        maintenance_duration = machine["mttr_days"] * 0.6   # Planned = faster than unplanned
        production_lost = round(max_output * maintenance_duration)
        can_compensate = (daily_demand - max_output) < 0  # Other lines have headroom

        # Financial case
        planned_cost = machine["maintenance_cost_per_event"]
        unplanned_cost = round(machine["unplanned_failure_cost_per_day"] * machine["mttr_days"] + planned_cost * 1.5)
        failure_prob_7d = round((1 - math.exp(-7 / max(1.0, mtbf * (health / 100)))) * 100, 1)
        expected_failure_cost = round(unplanned_cost * failure_prob_7d / 100)

        total_planned_cost += planned_cost
        total_avoided_failure_cost += max(0, expected_failure_cost - planned_cost)

        schedule.append({
            "machine_id": mid,
            "machine_name": machine["machine_name"],
            "action": "SCHEDULE PREVENTIVE MAINTENANCE",
            "urgency": urgency,
            "recommended_window": window,
            "maintenance_duration_days": round(maintenance_duration, 1),
            "estimated_cost": planned_cost,
            "production_impact_units": production_lost,
            "production_line_impact": machine["production_line"],
            "other_lines_can_compensate": can_compensate,
            "financial_case": {
                "planned_maintenance_cost": planned_cost,
                "estimated_unplanned_failure_cost": unplanned_cost,
                "failure_probability_7d_pct": failure_prob_7d,
                "expected_cost_of_inaction": expected_failure_cost,
                "net_savings_from_acting_now": max(0, expected_failure_cost - planned_cost),
            },
        })

    # Sort by urgency
    urgency_order = {"immediate": 0, "high": 1, "medium": 2, "low": 3, "none": 4}
    schedule.sort(key=lambda x: urgency_order.get(x["urgency"], 5))

    result = {
        "planning_horizon_days": planning_horizon_days,
        "production_demand_weekly": production_demand_weekly,
        "maintenance_schedule": schedule,
        "schedule_summary": {
            "machines_needing_attention": sum(1 for s in schedule if s["urgency"] not in ("none",)),
            "immediate_actions": sum(1 for s in schedule if s["urgency"] == "immediate"),
            "high_priority_actions": sum(1 for s in schedule if s["urgency"] == "high"),
            "medium_priority_actions": sum(1 for s in schedule if s["urgency"] == "medium"),
            "total_planned_maintenance_cost": total_planned_cost,
            "total_expected_failure_cost_avoided": total_avoided_failure_cost,
            "net_financial_benefit_of_plan": total_avoided_failure_cost,
        },
        "cross_agent_alert_for_production": {
            "message": "Production Planning Agent must account for the following maintenance windows",
            "windows": [
                {
                    "machine_id": s["machine_id"],
                    "line": s.get("production_line_impact", "N/A"),
                    "window": s["recommended_window"],
                    "duration_days": s.get("maintenance_duration_days"),
                }
                for s in schedule if s["urgency"] not in ("none",)
            ],
        },
    }

    return json.dumps(result, indent=2, default=str)


@tool
def assess_production_capacity_impact(include_risk_buffer: bool = True) -> str:
    """
    Assess the real-world production capacity available right now, accounting for:
    - Machines that are down (zero contribution)
    - Machines with degraded performance (reduced contribution)
    - Machines at high failure risk (probabilistic capacity reduction)

    This is the key output the Production Planning Agent consumes to determine
    the maximum safe production ceiling. Also generates cross-agent output.

    Args:
        include_risk_buffer: Whether to apply a risk buffer for at-risk machines (default: True)
    """
    fleet = get_machine_fleet()

    lines_detail = []
    total_theoretical = 0
    total_effective = 0
    total_risk_adjusted = 0
    at_risk_machines = []

    for machine in fleet:
        if machine["max_output_units_per_day"] is None:
            # Quality scanner — not a bottleneck, skip from capacity calc
            continue

        mid = machine["machine_id"]
        max_output = machine["max_output_units_per_day"]
        total_theoretical += max_output
        health = machine["health_score"]
        alert = machine["alert_level"]
        status = machine["status"]

        # Effective capacity based on current health
        if status == "down":
            effective = 0
            efficiency_factor = 0.0
            capacity_note = "Machine is down — zero contribution"
        elif alert == "warning":
            efficiency_factor = 0.75
            effective = round(max_output * efficiency_factor)
            capacity_note = f"Running at ~75% efficiency due to sensor warnings"
        elif alert == "caution":
            efficiency_factor = 0.90
            effective = round(max_output * efficiency_factor)
            capacity_note = f"Running at ~90% efficiency — caution-level degradation"
        else:
            efficiency_factor = 0.97   # Small overhead for normal wear
            effective = round(max_output * efficiency_factor)
            capacity_note = "Fully operational"

        total_effective += effective

        # Risk-adjusted capacity (account for probability of failure this week)
        sensor_data = get_sensor_readings(mid)
        sensors = sensor_data.get("sensors", {})
        degradation_factor = 1.0
        for s_name, s_reading in sensors.items():
            baseline = s_reading.get("baseline", 1)
            current = s_reading.get("current", baseline)
            high_thresh = s_reading.get("high_threshold")
            crit_thresh = s_reading.get("critical_threshold")
            if crit_thresh and current >= crit_thresh:
                degradation_factor *= 0.35
            elif high_thresh and current >= high_thresh:
                degradation_factor *= 0.55

        effective_mtbf = max(1.0, machine["mtbf_days"] * degradation_factor)
        failure_prob_7d = (1 - math.exp(-7 / effective_mtbf)) if status != "down" else 1.0

        if include_risk_buffer and failure_prob_7d > 0.15:
            risk_adjusted = round(effective * (1 - failure_prob_7d * 0.5))
            at_risk_machines.append({
                "machine_id": mid,
                "name": machine["machine_name"],
                "failure_probability_7d_pct": round(failure_prob_7d * 100, 1),
                "capacity_at_risk_units_per_day": effective - risk_adjusted,
            })
        else:
            risk_adjusted = effective

        total_risk_adjusted += risk_adjusted

        lines_detail.append({
            "machine_id": mid,
            "machine_name": machine["machine_name"],
            "production_line": machine["production_line"],
            "max_output_per_day": max_output,
            "effective_output_per_day": effective,
            "risk_adjusted_output_per_day": risk_adjusted,
            "efficiency_factor_pct": round(efficiency_factor * 100, 1),
            "failure_probability_7d_pct": round(failure_prob_7d * 100, 1),
            "capacity_note": capacity_note,
        })

    # Weekly figures
    eff_weekly = total_effective * 7
    risk_weekly = total_risk_adjusted * 7
    theoretical_weekly = total_theoretical * 7

    result = {
        "capacity_assessment": {
            "theoretical_max_units_per_day": total_theoretical,
            "effective_capacity_units_per_day": total_effective,
            "risk_adjusted_capacity_units_per_day": total_risk_adjusted,
            "theoretical_max_units_per_week": theoretical_weekly,
            "effective_capacity_units_per_week": eff_weekly,
            "risk_adjusted_capacity_units_per_week": risk_weekly,
            "overall_capacity_utilization_pct": round((total_effective / total_theoretical) * 100, 1) if total_theoretical else 0,
            "capacity_loss_from_downtime_pct": round(((total_theoretical - total_effective) / total_theoretical) * 100, 1) if total_theoretical else 0,
        },
        "machines_at_risk": at_risk_machines,
        "line_by_line_detail": lines_detail,
        "cross_agent_output_for_production_planning": {
            "source_agent": "machine_health",
            "recommended_production_ceiling_units_per_day": total_risk_adjusted,
            "recommended_production_ceiling_units_per_week": risk_weekly,
            "max_safe_if_no_failures_units_per_day": total_effective,
            "machines_at_high_risk": [m["machine_id"] for m in at_risk_machines if m["failure_probability_7d_pct"] >= 20],
            "production_lines_at_risk": list(set(
                next((m["production_line"] for m in fleet if m["machine_id"] == r["machine_id"]), "Unknown")
                for r in at_risk_machines
            )),
            "capacity_risk_flag": len(at_risk_machines) > 0,
            "alert": (
                "CAPACITY RISK: One or more machines have >15% failure probability this week. "
                "Do NOT commit to production targets above the risk-adjusted ceiling."
                if at_risk_machines else
                "Capacity is stable. Production targets up to the effective ceiling are achievable."
            ),
        },
    }

    return json.dumps(result, indent=2, default=str)
