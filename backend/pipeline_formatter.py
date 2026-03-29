"""
Format structured pipeline results into human-readable text
"""

def format_pipeline_result(structured_result: dict) -> str:
    """
    Convert structured pipeline output to readable text report

    Args:
        structured_result: Output from OrchestratorAgent.run_full_pipeline()

    Returns:
        Formatted text report
    """
    product_id = structured_result.get("product_id", "Unknown")
    planning_weeks = structured_result.get("planning_horizon_weeks", 4)
    outputs = structured_result.get("pipeline_outputs", {})
    report = structured_result.get("manufacturing_intelligence_report", {})

    # Extract key metrics
    demand = outputs.get("demand", {})
    inventory = outputs.get("inventory", {})
    production = outputs.get("production", {})
    machine = outputs.get("machine_health", {})

    text = f"""
╔══════════════════════════════════════════════════════════════════╗
║          MANUFACTURING INTELLIGENCE REPORT                        ║
║          Product: {product_id:<50} ║
║          Planning Horizon: {planning_weeks} weeks{' ' * 38}║
╚══════════════════════════════════════════════════════════════════╝

📊 DEMAND FORECAST ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Expected Weekly Demand: {demand.get('expected_weekly_demand', 'N/A')} units

Scenarios:
  • Optimistic (20%): {demand.get('scenarios', {}).get('optimistic', {}).get('weekly_avg', 'N/A')} units/week
  • Base Case (55%): {demand.get('scenarios', {}).get('base', {}).get('weekly_avg', 'N/A')} units/week
  • Pessimistic (25%): {demand.get('scenarios', {}).get('pessimistic', {}).get('weekly_avg', 'N/A')} units/week

Trend: {demand.get('trend_direction', 'N/A')} ({demand.get('growth_rate_pct_per_week', 0):+.1f}% per week)
Confidence Interval (95%): {demand.get('confidence_interval_95pct', {}).get('lower', 'N/A')} - {demand.get('confidence_interval_95pct', {}).get('upper', 'N/A')} units

📦 INVENTORY POSITION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current Stock: {inventory.get('current_stock', 'N/A')} units
Safety Stock: {inventory.get('safety_stock', 'N/A')} units
Days of Supply: {inventory.get('days_of_supply', 'N/A')} days (Effective: {inventory.get('effective_days_of_supply', 'N/A')} days)

Risk Assessment:
  • Stockout Probability: {inventory.get('stockout_probability_pct', 'N/A')}% over {planning_weeks} weeks
  • Reorder Point: {inventory.get('reorder_point_units', 'N/A')} units
  • Reorder Needed: {'YES - URGENT!' if inventory.get('reorder_needed_now') else 'No'}
  • Days Until ROP: {inventory.get('days_until_rop', 'N/A')} days

Warehouse: {inventory.get('warehouse_utilization_pct', 'N/A')}% utilized

🏭 PRODUCTION CAPACITY & SCHEDULING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Weekly Production Target: {production.get('weekly_production_target', 'N/A')} units
Effective Capacity: {production.get('effective_capacity_weekly', 'N/A')} units/week

Lines Status:
  • Active Lines: {production.get('lines_active', 'N/A')}
  • Down Lines: {production.get('lines_down', 'N/A')}
  • Overtime Required: {'YES' if production.get('overtime_required') else 'No'}

Master Production Schedule:
{format_mps_summary(production.get('mps_summary', {}))}

🔧 MACHINE HEALTH STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Plant OEE: {machine.get('plant_oee_pct', 'N/A')}%
Critical Machines: {', '.join(machine.get('critical_machines', [])) or 'None'}
Bottleneck: {machine.get('bottleneck_machine_id', 'N/A')}

Maintenance Actions Required: {len(machine.get('critical_machines', []))} machines

🎯 SYSTEM HEALTH SCORE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Score: {report.get('system_health_score', 'N/A')}/100
Status: {report.get('status', 'N/A').upper()}

💡 KEY RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{format_recommendations(report.get('recommendations', []))}

⚠️  CRITICAL ISSUES DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{format_critical_issues(report.get('critical_issues', []))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {structured_result.get('timestamp', 'N/A')}
Report ID: {structured_result.get('run_id', 'N/A')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    return text


def format_mps_summary(mps_summary: dict) -> str:
    """Format Master Production Schedule summary"""
    if not mps_summary:
        return "  No schedule data available"

    lines = []
    lines.append(f"  Total Planned: {mps_summary.get('total_planned_units', 'N/A')} units over {mps_summary.get('weeks', 'N/A')} weeks")
    lines.append(f"  Overtime Cost: ${mps_summary.get('total_overtime_and_contract_cost', 0):,.2f}")

    return "\n".join(lines)


def format_recommendations(recommendations: list) -> str:
    """Format recommendations list"""
    if not recommendations:
        return "  No specific recommendations at this time"

    lines = []
    for i, rec in enumerate(recommendations[:5], 1):  # Top 5
        priority = rec.get('priority', 'medium').upper()
        lines.append(f"  {i}. [{priority}] {rec.get('recommendation', 'N/A')}")

    return "\n".join(lines) if lines else "  No recommendations"


def format_critical_issues(issues: list) -> str:
    """Format critical issues list"""
    if not issues:
        return "  ✅ No critical issues detected"

    lines = []
    for i, issue in enumerate(issues, 1):
        severity = issue.get('severity', 'medium').upper()
        lines.append(f"  {i}. [{severity}] {issue.get('issue', 'N/A')}")

    return "\n".join(lines)
