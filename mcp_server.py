"""
AMIS MCP Server
Exposes the AMIS manufacturing database as MCP tools so Claude can query
live plant data directly during Ask AMIS conversations.
"""

import sqlite3
import os
import sys
import json
from mcp.server.fastmcp import FastMCP

# Redirect stdout warnings/prints to stderr so they don't corrupt the stdio JSON-RPC stream
import warnings
warnings.filterwarnings("ignore")

DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "amis.db")

mcp = FastMCP("AMIS Manufacturing Database")


def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Tool 1: Inventory ────────────────────────────────────────────────────────

@mcp.tool()
def get_inventory_status() -> str:
    """
    Get current inventory levels, safety stock, reorder points and stockout risk
    for all products in the AMIS plant.
    """
    conn = _db()
    cur = conn.cursor()
    cur.execute("""
        SELECT i.product_id, p.name as product_name,
               i.current_stock, i.safety_stock, i.reorder_point,
               i.avg_daily_usage, i.stockout_risk,
               i.last_replenishment_date, i.unit_cost
        FROM inventory i
        JOIN products p ON i.product_id = p.id
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    for r in rows:
        r["days_of_supply"] = round(r["current_stock"] / max(r["avg_daily_usage"], 1), 1)
        r["below_reorder_point"] = r["current_stock"] < r["reorder_point"]
    return json.dumps(rows, indent=2)


# ── Tool 2: Machine Health ───────────────────────────────────────────────────

@mcp.tool()
def get_machine_health() -> str:
    """
    Get OEE, failure risk, status and sensor readings for all machines in the plant.
    Includes vibration, temperature, and maintenance schedule.
    """
    conn = _db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, type, line, status,
               round(oee * 100, 1) as oee_pct,
               round(failure_risk * 100, 1) as failure_risk_pct,
               round(current_utilization * 100, 1) as utilization_pct,
               vibration_level, temperature, runtime_hours,
               last_maintenance, next_maintenance
        FROM machines
        ORDER BY failure_risk DESC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json.dumps(rows, indent=2)


# ── Tool 3: Demand Forecast ──────────────────────────────────────────────────

@mcp.tool()
def get_demand_data(product_id: str = "PROD-A", weeks: int = 8) -> str:
    """
    Get historical weekly demand data and recent trend for a product.
    Args:
        product_id: Product ID (default PROD-A)
        weeks: Number of recent weeks to return (default 8)
    """
    conn = _db()
    cur = conn.cursor()
    cur.execute("""
        SELECT h.week_number, h.year, h.demand_units, h.actual_units,
               h.forecast_units, h.variance_pct
        FROM historical_demand_data h
        WHERE h.product_id = ?
        ORDER BY h.year DESC, h.week_number DESC
        LIMIT ?
    """, (product_id, weeks))
    rows = [dict(r) for r in cur.fetchall()]

    # Also get market context
    cur.execute("SELECT * FROM market_context_data WHERE product_id = ?", (product_id,))
    ctx = cur.fetchone()
    conn.close()

    return json.dumps({
        "product_id": product_id,
        "recent_weeks": rows,
        "market_context": dict(ctx) if ctx else {}
    }, indent=2)


# ── Tool 4: Production Status ────────────────────────────────────────────────

@mcp.tool()
def get_production_status() -> str:
    """
    Get production line status, capacity, utilization and current week's schedule.
    """
    conn = _db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, status,
               capacity_per_hour,
               round(utilization * 100, 1) as utilization_pct,
               shift_hours_per_day, days_per_week,
               round(capacity_per_hour * utilization * shift_hours_per_day * days_per_week, 0) as weekly_output
        FROM production_lines
    """)
    lines = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT ps.week_number, ps.planned_units, ps.actual_units,
               ps.attainment_pct, ps.status
        FROM production_schedule ps
        ORDER BY ps.week_number DESC LIMIT 4
    """)
    schedule = [dict(r) for r in cur.fetchall()]
    conn.close()

    return json.dumps({
        "production_lines": lines,
        "recent_schedule": schedule
    }, indent=2)


# ── Tool 5: Supplier & Purchase Orders ──────────────────────────────────────

@mcp.tool()
def get_supplier_status() -> str:
    """
    Get supplier scorecards, performance metrics and open purchase orders.
    """
    conn = _db()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id, s.name, s.location,
               s.quality_score, s.on_time_delivery, s.score,
               s.lead_time, s.payment_terms, s.risk, s.rating
        FROM suppliers s
        ORDER BY s.score DESC
    """)
    suppliers = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT po.id, po.supplier_id, s.name as supplier_name,
               po.component_id, po.quantity, po.unit_price,
               po.total_value, po.status, po.expected_delivery,
               po.created_at
        FROM purchase_orders po
        JOIN suppliers s ON po.supplier_id = s.id
        WHERE po.status != 'delivered'
        ORDER BY po.expected_delivery ASC
    """)
    open_pos = [dict(r) for r in cur.fetchall()]
    conn.close()

    return json.dumps({
        "suppliers": suppliers,
        "open_purchase_orders": open_pos
    }, indent=2)


# ── Tool 6: Pipeline Decisions / Audit Log ───────────────────────────────────

@mcp.tool()
def get_pipeline_decisions(limit: int = 10) -> str:
    """
    Get recent AI pipeline decisions from the audit log — approved and rejected.
    Args:
        limit: Number of recent decisions to return (default 10)
    """
    conn = _db()
    cur = conn.cursor()
    cur.execute("""
        SELECT agent_type, decision_type, status, confidence_score,
               reasoning, reviewed_by, created_at
        FROM ai_decisions
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json.dumps(rows, indent=2)


# ── Tool 7: System Health Summary ────────────────────────────────────────────

@mcp.tool()
def get_system_health_summary() -> str:
    """
    Get a quick summary of overall plant health — machines, inventory, production,
    and any active alerts or critical issues.
    """
    conn = _db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) as total, SUM(CASE WHEN status='down' THEN 1 ELSE 0 END) as down, AVG(oee) as avg_oee, AVG(failure_risk) as avg_risk FROM machines")
    machines = dict(cur.fetchone())

    cur.execute("SELECT COUNT(*) as total, SUM(CASE WHEN current_stock < reorder_point THEN 1 ELSE 0 END) as below_rop FROM inventory")
    inv = dict(cur.fetchone())

    cur.execute("SELECT COUNT(*) as total, SUM(CASE WHEN status='down' THEN 1 ELSE 0 END) as down FROM production_lines")
    prod = dict(cur.fetchone())

    cur.execute("SELECT id, name, status, round(failure_risk*100,1) as risk_pct FROM machines WHERE failure_risk > 0.4 ORDER BY failure_risk DESC")
    critical_machines = [dict(r) for r in cur.fetchall()]

    conn.close()

    return json.dumps({
        "machines": {
            "total": machines["total"],
            "down": machines["down"],
            "avg_oee_pct": round(machines["avg_oee"] * 100, 1) if machines["avg_oee"] else 0,
            "avg_failure_risk_pct": round(machines["avg_risk"] * 100, 1) if machines["avg_risk"] else 0,
            "critical": critical_machines
        },
        "inventory": {
            "total_products": inv["total"],
            "below_reorder_point": inv["below_rop"]
        },
        "production": {
            "total_lines": prod["total"],
            "lines_down": prod["down"]
        }
    }, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
