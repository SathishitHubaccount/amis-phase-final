"""
Format structured pipeline results into markdown for frontend rendering.
"""


def format_pipeline_result(structured_result: dict) -> str:
    product_id = structured_result.get("product_id", "Unknown")
    planning_weeks = structured_result.get("planning_horizon_weeks", 4)
    generated_at = structured_result.get("generated_at", "N/A")
    outputs = structured_result.get("pipeline_outputs", {})
    report = structured_result.get("manufacturing_intelligence_report", {})

    demand = outputs.get("demand", {})
    inventory = outputs.get("inventory", {})
    production = outputs.get("production", {})
    machine = outputs.get("machine_health", {})

    system_health = report.get("system_health", {})
    overall_score = system_health.get("overall_score", "N/A")
    overall_status = str(system_health.get("overall_status", "N/A")).upper()
    domain_scores = system_health.get("domain_scores", {})

    actions = report.get("priority_actions", [])
    alerts = report.get("cross_domain_alerts", [])

    # ── Header ──────────────────────────────────────────────────────
    lines = [
        f"# Manufacturing Intelligence Report",
        f"**Product:** {product_id} &nbsp;·&nbsp; **Planning Horizon:** {planning_weeks} weeks &nbsp;·&nbsp; **Generated:** {generated_at}",
        "",
        "---",
        "",
    ]

    # ── System Health Score ──────────────────────────────────────────
    status_emoji = {"HEALTHY": "🟢", "WATCH": "🟡", "AT RISK": "🟠", "CRITICAL": "🔴"}.get(overall_status, "⚪")
    lines += [
        f"## {status_emoji} System Health Score: {overall_score}/100 — {overall_status}",
        "",
    ]

    if domain_scores:
        lines.append("| Domain | Score | Status |")
        lines.append("|---|---|---|")
        domain_labels = {
            "demand": "📊 Demand",
            "inventory": "📦 Inventory",
            "machine_health": "🔧 Machine Health",
            "production": "🏭 Production",
            "supply_chain": "🚚 Supply Chain",
        }
        for key, label in domain_labels.items():
            d = domain_scores.get(key, {})
            score = d.get("score", "N/A")
            status = str(d.get("status", "N/A")).upper()
            s_emoji = {"HEALTHY": "🟢", "WATCH": "🟡", "AT RISK": "🟠", "AT_RISK": "🟠", "CRITICAL": "🔴", "ALERT": "🔴"}.get(status, "⚪")
            lines.append(f"| {label} | {score}/100 | {s_emoji} {status} |")
        lines += ["", "---", ""]

    # ── Demand ──────────────────────────────────────────────────────
    lines += [
        "## 📊 Demand Forecast Analysis",
        "",
        f"**Expected Weekly Demand:** {demand.get('expected_weekly_demand', 'N/A')} units",
        f"**Trend:** {str(demand.get('trend_direction', 'N/A')).title()} ({demand.get('growth_rate_pct_per_week', 0):+.1f}%/week)",
    ]

    ci = demand.get("confidence_interval_95pct", {})
    if ci:
        lines.append(f"**Confidence Interval (95%):** {ci.get('lower', 'N/A')} – {ci.get('upper', 'N/A')} units")

    anomaly = demand.get("anomaly_detected")
    lines.append(f"**Anomaly Detected:** {'⚠️ Yes' if anomaly else '✅ No'}")
    lines.append("")

    scenarios = demand.get("scenarios", {})
    if scenarios:
        lines.append("**Demand Scenarios:**")
        lines.append("")
        lines.append("| Scenario | Probability | Weekly Avg |")
        lines.append("|---|---|---|")
        scenario_map = [
            ("optimistic", "Optimistic", "20%"),
            ("base", "Base Case", "55%"),
            ("pessimistic", "Pessimistic", "25%"),
        ]
        for key, label, prob in scenario_map:
            s = scenarios.get(key, scenarios.get(key.title(), {}))
            val = s.get("weekly_avg", "N/A")
            lines.append(f"| {label} | {prob} | {val} units/week |")
        lines.append("")

    lines += ["---", ""]

    # ── Inventory ───────────────────────────────────────────────────
    lines += [
        "## 📦 Inventory Position",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Current Stock | {inventory.get('current_stock', 'N/A')} units |",
        f"| Safety Stock | {inventory.get('safety_stock', 'N/A')} units |",
        f"| Days of Supply | {inventory.get('days_of_supply', 'N/A')} days (Effective: {inventory.get('effective_days_of_supply', 'N/A')} days) |",
        f"| Stockout Probability | {inventory.get('stockout_probability_pct', 'N/A')}% over {planning_weeks} weeks |",
        f"| Reorder Point | {inventory.get('reorder_point_units', 'N/A')} units |",
        f"| Days Until ROP | {inventory.get('days_until_rop', 'N/A')} days |",
        f"| Reorder Needed Now | {'⚠️ **YES — URGENT**' if inventory.get('reorder_needed_now') else '✅ No'} |",
        f"| Warehouse Utilization | {inventory.get('warehouse_utilization_pct', 'N/A')}% |",
        "",
        "---",
        "",
    ]

    # ── Production ──────────────────────────────────────────────────
    mps = production.get("mps_summary", {})
    lines += [
        "## 🏭 Production Capacity & Scheduling",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Weekly Production Target | {production.get('weekly_production_target', 'N/A')} units |",
        f"| Effective Capacity | {production.get('effective_capacity_weekly', 'N/A')} units/week |",
        f"| Active Lines | {production.get('lines_active', 'N/A')} |",
        f"| Down Lines | {production.get('lines_down', 'N/A')} |",
        f"| Overtime Required | {'⚠️ **YES**' if production.get('overtime_required') else '✅ No'} |",
    ]
    if mps:
        lines += [
            f"| Total Planned (MPS) | {mps.get('total_planned_units', 'N/A')} units |",
            f"| MPS Attainment | {mps.get('overall_attainment_pct', 'N/A')}% |",
            f"| Overtime Cost | ${mps.get('total_overtime_and_contract_cost', 0):,.2f} |",
        ]
    lines += ["", "---", ""]

    # ── Machine Health ───────────────────────────────────────────────
    at_risk = machine.get("machines_at_high_risk", [])
    lines += [
        "## 🔧 Machine Health Status",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Fleet Avg OEE | {machine.get('fleet_summary', {}).get('average_oee_pct', 'N/A')}% |",
        f"| Capacity Ceiling | {machine.get('recommended_production_ceiling_units_per_week', 'N/A')} units/week |",
        f"| High-Risk Machines | {', '.join(at_risk) if at_risk else '✅ None'} |",
        f"| Maintenance Actions | {len(at_risk)} machine(s) require attention |",
        "",
        "---",
        "",
    ]

    # ── Priority Actions ────────────────────────────────────────────
    lines += ["## 💡 Priority Actions", ""]
    if actions:
        urgency_emoji = {"IMMEDIATE": "🔴", "THIS WEEK": "🟠", "THIS MONTH": "🟡"}
        for action in actions[:5]:
            urgency = action.get("urgency", "N/A")
            owner = action.get("owner", "N/A")
            priority = action.get("priority", "")
            u_emoji = urgency_emoji.get(urgency, "⚪")
            lines.append(f"### {u_emoji} {priority}. {urgency} — {owner}")
            lines.append("")
            lines.append(action.get("action", ""))
            impact = action.get("impact", "")
            if impact:
                lines.append("")
                lines.append(f"> **Impact:** {impact}")
            lines.append("")
    else:
        lines += ["✅ No specific actions required at this time.", ""]

    lines += ["---", ""]

    # ── Cross-Domain Alerts ─────────────────────────────────────────
    lines += ["## ⚠️ Cross-Domain Alerts", ""]
    if alerts:
        severity_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
        for i, alert in enumerate(alerts, 1):
            severity = alert.get("severity", "N/A").upper()
            domains = ", ".join(d.replace("_", " ").title() for d in alert.get("domains", []))
            s_emoji = severity_emoji.get(severity, "⚪")
            lines.append(f"**{s_emoji} [{severity}]** _{domains}_")
            lines.append("")
            lines.append(alert.get("alert", ""))
            lines.append("")
    else:
        lines += ["✅ No cross-domain alerts detected.", ""]

    lines += ["---", ""]
    lines.append(f"_Report generated: {generated_at} · Product: {product_id} · Horizon: {planning_weeks} weeks_")

    return "\n".join(lines)
