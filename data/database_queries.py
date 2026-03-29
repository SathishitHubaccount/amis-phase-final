"""
Database Query Functions for Historical Data
=============================================
These functions query the database for historical demand and market context data.
They replace the random data generation functions in sample_data.py.
"""
import sqlite3
from pathlib import Path
from typing import List, Dict

# Database path
DATABASE_PATH = Path(__file__).parent.parent / "backend" / "amis.db"


def get_historical_demand_from_db(product_id: str = "PROD-A", weeks: int = 12) -> List[Dict]:
    """
    Query historical demand data from the database.
    Returns the same format as the old get_historical_demand() function
    for backward compatibility with existing tools.

    Args:
        product_id: Product ID to query (default: PROD-A)
        weeks: Number of weeks to retrieve (default: 12)

    Returns:
        List of dictionaries with historical demand data
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            product_id,
            week_start_date as date,
            week_number,
            year,
            demand_units,
            avg_price,
            promotions_active,
            competitor_price,
            is_anomaly,
            anomaly_reason
        FROM historical_demand_data
        WHERE product_id = ?
        ORDER BY week_start_date DESC
        LIMIT ?
    """, (product_id, weeks))

    rows = cursor.fetchall()
    conn.close()

    # Convert to list of dictionaries matching original format
    data = []
    for row in rows:
        # Calculate week string (e.g., "2026-W07")
        from datetime import datetime
        date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
        week_str = date_obj.strftime("%Y-W%U")

        data.append({
            "week": week_str,
            "date": row['date'],
            "product_id": row['product_id'],
            "demand_units": row['demand_units'],
            "anomaly": bool(row['is_anomaly']),
            "avg_price": row['avg_price'],
            "promotions_active": bool(row['promotions_active']),
            "competitor_price": row['competitor_price'],
        })

    # Return in chronological order (oldest first)
    return list(reversed(data))


def get_market_context_from_db() -> Dict:
    """
    Query market context data from the database.
    Returns the same format as the old get_market_context() function.

    Returns:
        Dictionary with market context information
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get the most recent market context
    cursor.execute("""
        SELECT *
        FROM market_context_data
        ORDER BY date_recorded DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if not row:
        # Return empty dict if no data (shouldn't happen after migration)
        return {}

    # Format to match original get_market_context() output
    from datetime import datetime, timedelta

    # Parse dates
    trade_show_date = row['trade_show_date']
    contract_renewal = row['major_client_contract_renewal_date']

    # Calculate days until events
    today = datetime.now().date()

    if trade_show_date:
        trade_show_date_obj = datetime.strptime(trade_show_date, '%Y-%m-%d').date()
        trade_show_days = (trade_show_date_obj - today).days
        trade_show_text = f"Industry trade show in {trade_show_days} days"
    else:
        trade_show_text = "No upcoming trade shows"

    if contract_renewal:
        contract_date_obj = datetime.strptime(contract_renewal, '%Y-%m-%d').date()
        contract_days = (contract_date_obj - today).days
        contract_text = f"Major client contract renewal in {contract_days} days"
    else:
        contract_text = "No pending contract renewals"

    return {
        "season": row['seasonal_pattern'] or "Q1",
        "economic_indicator": row['economic_indicator'] or "stable",
        "industry_trend": f"growing at {row['industry_growth_rate']}% YoY" if row['industry_growth_rate'] else "stable",
        "raw_material_price_trend": row['raw_material_price_trend'] or "stable",
        "competitor_activity": row['competitor_activity'] or "No significant competitor activity",
        "social_media_mentions": {
            "volume": "Data not available",
            "sentiment": "Data not available",
            "top_topic": "Data not available",
        },
        "weather_forecast": "Normal conditions expected",
        "upcoming_events": [
            trade_show_text,
            contract_text,
        ],
        "market_sentiment": row['market_sentiment'] or "Neutral",
        "supply_chain_status": row['supply_chain_status'] or "Normal operations",
    }


def get_historical_demand_statistics(product_id: str = "PROD-A") -> Dict:
    """
    Calculate statistics from historical demand data.
    Useful for validation and reporting.

    Args:
        product_id: Product ID to analyze

    Returns:
        Dictionary with statistical summaries
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) as week_count,
            AVG(demand_units) as avg_demand,
            MIN(demand_units) as min_demand,
            MAX(demand_units) as max_demand,
            SUM(CASE WHEN is_anomaly = 1 THEN 1 ELSE 0 END) as anomaly_count,
            SUM(CASE WHEN promotions_active = 1 THEN 1 ELSE 0 END) as promotion_weeks
        FROM historical_demand_data
        WHERE product_id = ?
    """, (product_id,))

    row = cursor.fetchone()
    conn.close()

    return {
        "product_id": product_id,
        "total_weeks": row[0],
        "average_weekly_demand": round(row[1], 2) if row[1] else 0,
        "min_weekly_demand": row[2] or 0,
        "max_weekly_demand": row[3] or 0,
        "weeks_with_anomalies": row[4] or 0,
        "weeks_with_promotions": row[5] or 0,
    }


def get_anomaly_weeks(product_id: str = "PROD-A") -> List[Dict]:
    """
    Get all weeks with demand anomalies for a product.

    Args:
        product_id: Product ID to query

    Returns:
        List of anomaly events
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            week_start_date,
            week_number,
            year,
            demand_units,
            anomaly_reason
        FROM historical_demand_data
        WHERE product_id = ? AND is_anomaly = 1
        ORDER BY week_start_date DESC
    """, (product_id,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "date": row['week_start_date'],
            "week_number": row['week_number'],
            "year": row['year'],
            "demand": row['demand_units'],
            "reason": row['anomaly_reason'],
        }
        for row in rows
    ]


# For backward compatibility, create aliases with original names
get_historical_demand = get_historical_demand_from_db
get_market_context = get_market_context_from_db


# ══════════════════════════════════════════════════════════════════
# Additional functions to replace ALL sample_data.py functions
# ══════════════════════════════════════════════════════════════════

def get_current_inventory(product_id: str = "PROD-A") -> Dict:
    """Returns current inventory status from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Get inventory data
    cursor.execute("""
        SELECT
            product_id, current_stock, safety_stock,
            avg_daily_usage, lead_time, stockout_risk,
            unit_cost, holding_cost
        FROM inventory
        WHERE product_id = ?
    """, (product_id,))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return {}

    prod_id, current_stock, safety_stock, avg_daily, lead_time, stockout_risk, unit_cost, holding_cost = row

    # Get warehouse capacity from zones
    cursor.execute("""
        SELECT SUM(capacity), SUM(current_units)
        FROM warehouse_zones
        WHERE product_id = ?
    """, (product_id,))

    capacity_row = cursor.fetchone()
    warehouse_capacity = capacity_row[0] if capacity_row[0] else 5000
    total_units = capacity_row[1] if capacity_row[1] else current_stock

    # Get incoming orders
    cursor.execute("""
        SELECT supplier_id, quantity,
               CAST((julianday(expected_delivery_date) - julianday('now')) AS INTEGER) as eta_days
        FROM purchase_orders
        WHERE product_id = ? AND status IN ('open', 'in_transit', 'processing')
        ORDER BY expected_delivery_date
    """, (product_id,))

    incoming_orders = []
    for order_row in cursor.fetchall():
        supp_id, qty, eta = order_row
        incoming_orders.append({
            "supplier": supp_id,
            "quantity": qty,
            "eta_days": max(0, eta)
        })

    conn.close()

    # Calculate derived values
    days_of_supply = round(current_stock / avg_daily, 1) if avg_daily > 0 else 999
    warehouse_utilization_pct = round((total_units / warehouse_capacity) * 100, 0)

    return {
        "product_id": prod_id,
        "current_stock": current_stock,
        "safety_stock": safety_stock,
        "warehouse_capacity": warehouse_capacity,
        "warehouse_utilization_pct": warehouse_utilization_pct,
        "avg_daily_consumption": avg_daily,
        "days_of_supply": days_of_supply,
        "incoming_orders": incoming_orders,
        "unit_holding_cost": holding_cost,
        "unit_stockout_cost": 45.00,
    }


def get_production_capacity() -> Dict:
    """Returns current production capacity info from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Get all production lines
    cursor.execute("""
        SELECT id, status, capacity_per_hour
        FROM production_lines
        WHERE status = 'operational'
    """)

    operational_lines = cursor.fetchall()

    # Get lines under maintenance
    cursor.execute("""
        SELECT id, status, capacity_per_hour
        FROM production_lines
        WHERE status IN ('down', 'maintenance')
    """)

    down_lines = cursor.fetchall()

    # Get shift configuration
    cursor.execute("""
        SELECT hours_per_shift, overtime_available, max_overtime_hours
        FROM shift_config
        LIMIT 1
    """)

    shift_row = cursor.fetchone()
    conn.close()

    hours_per_shift = shift_row[0] if shift_row else 8
    overtime_available = bool(shift_row[1]) if shift_row else True

    # Calculate max daily output
    max_daily_output = sum(line[2] * hours_per_shift / 60 for line in operational_lines)
    total_capacity = sum(line[2] * hours_per_shift / 60 for line in operational_lines) + sum(line[2] * hours_per_shift / 60 for line in down_lines)

    current_utilization_pct = round((max_daily_output / total_capacity * 100), 0) if total_capacity > 0 else 0

    return {
        "max_daily_output": int(max_daily_output),
        "current_utilization_pct": current_utilization_pct,
        "available_lines": [line[0] for line in operational_lines],
        "lines_under_maintenance": [line[0] for line in down_lines],
        "overtime_available": overtime_available,
        "overtime_cost_premium_pct": 35,
        "contract_manufacturer_available": True,
        "contract_manufacturer_cost_premium_pct": 42,
    }


def get_product_info(product_id: str = "PROD-A") -> Dict:
    """Returns product-specific information from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, p.name, i.lead_time, i.unit_cost
        FROM products p
        LEFT JOIN inventory i ON p.id = i.product_id
        WHERE p.id = ?
    """, (product_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {}

    prod_id, name, lead_time, unit_cost = row

    unit_price = 89.50
    margin_pct = round(((unit_price - unit_cost) / unit_price) * 100, 1)

    return {
        "product_id": prod_id,
        "product_name": name,
        "unit_cost": unit_cost,
        "unit_price": unit_price,
        "margin_pct": margin_pct,
        "lead_time_days": lead_time,
        "shelf_life_days": None,
        "min_order_quantity": 100,
        "customer_segments": {
            "enterprise": {"share_pct": 55, "avg_order_size": 500},
            "mid_market": {"share_pct": 30, "avg_order_size": 150},
            "small_business": {"share_pct": 15, "avg_order_size": 40},
        },
    }


def get_warehouse_details(product_id: str = "PROD-A") -> Dict:
    """Returns detailed warehouse zone information from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT zone_id, capacity, current_units, utilization,
               zone_type, temperature_controlled
        FROM warehouse_zones
        WHERE product_id = ?
    """, (product_id,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {}

    zones = []
    zone_names = {"ZONE-A": "Primary Storage", "ZONE-B": "Fast-Pick Area", "ZONE-C": "Overflow / Seasonal"}

    for row in rows:
        zone_id, capacity, current_units, utilization, zone_type, temp_controlled = row
        zones.append({
            "zone_id": zone_id.replace("ZONE-", ""),
            "zone_name": zone_names.get(zone_id, f"Zone {zone_id}"),
            "capacity": capacity,
            "current_units": current_units,
            "utilization_pct": round(utilization, 1),
            "temperature_controlled": bool(temp_controlled),
            "zone_type": zone_type,
        })

    total_capacity = sum(z["capacity"] for z in zones)
    total_units = sum(z["current_units"] for z in zones)
    total_utilization = round((total_units / total_capacity) * 100, 1) if total_capacity > 0 else 0

    return {
        "product_id": product_id,
        "warehouse_id": "WH-MAIN",
        "total_capacity_units": total_capacity,
        "zones": zones,
        "total_current_units": total_units,
        "total_utilization_pct": total_utilization,
        "cost_per_zone_per_unit_per_day": {"A": 0.08, "B": 0.12, "C": 0.06},
    }


def get_supplier_performance(product_id: str = "PROD-A") -> List[Dict]:
    """Returns supplier reliability and lead time data from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            s.id, s.name, s.lead_time, s.lead_time_variability,
            s.on_time_delivery, s.quality_score, s.base_cost, s.moq
        FROM suppliers s
        WHERE s.id IN (
            SELECT DISTINCT supplier_id
            FROM purchase_orders
            WHERE product_id = ?
        )
    """, (product_id,))

    suppliers = cursor.fetchall()

    result = []
    for supplier in suppliers:
        supp_id, name, lead_time, lead_var, otd, quality, cost, moq = supplier

        # Get last 10 deliveries
        cursor.execute("""
            SELECT quantity, quantity as delivered_qty,
                   ? as promised_days,
                   CAST((julianday(actual_delivery_date) - julianday(order_date)) AS INTEGER) as actual_days
            FROM purchase_orders
            WHERE supplier_id = ? AND product_id = ? AND status = 'delivered'
            ORDER BY order_date DESC
            LIMIT 10
        """, (lead_time, supp_id, product_id))

        deliveries = []
        for delivery in cursor.fetchall():
            qty, delivered, promised, actual = delivery
            deliveries.append({
                "order_qty": qty,
                "delivered_qty": delivered,
                "promised_days": promised,
                "actual_days": actual if actual else promised
            })

        result.append({
            "supplier_id": supp_id,
            "supplier_name": name,
            "product_id": product_id,
            "avg_lead_time_days": float(lead_time),
            "lead_time_std_dev_days": float(lead_var),
            "on_time_delivery_pct": float(otd),
            "quality_reject_rate_pct": 100.0 - quality,
            "unit_cost": cost,
            "min_order_quantity": moq,
            "max_order_quantity": moq * 20,
            "last_10_deliveries": deliveries,
        })

    conn.close()
    return result


def get_historical_stockouts(product_id: str = "PROD-A") -> List[Dict]:
    """Returns historical stockout events from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id, product_id, event_date, duration_days,
            units_short, root_cause, revenue_lost, customers_affected
        FROM stockout_events
        WHERE product_id = ?
        ORDER BY event_date DESC
    """, (product_id,))

    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        event_id, prod_id, date, duration, units, cause, revenue, customers = row
        result.append({
            "event_id": f"SO-{event_id:03d}",
            "product_id": prod_id,
            "date": date,
            "duration_days": duration,
            "units_short": units,
            "root_cause": cause,
            "revenue_lost": revenue,
            "customers_affected": customers,
            "recovery_time_days": duration + 2,
        })

    return result


def get_reorder_history(product_id: str = "PROD-A") -> List[Dict]:
    """Returns last 8 reorder events from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            order_date, supplier_id, quantity, unit_cost,
            actual_delivery_date,
            CAST((julianday(actual_delivery_date) - julianday(order_date)) AS INTEGER) as lead_time_actual,
            status
        FROM purchase_orders
        WHERE product_id = ? AND status = 'delivered'
        ORDER BY order_date DESC
        LIMIT 8
    """, (product_id,))

    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        order_date, supplier, qty, cost, received, lead_time, status = row
        result.append({
            "order_date": order_date,
            "supplier": supplier,
            "qty": qty,
            "unit_cost": cost,
            "received_date": received,
            "lead_time_actual": lead_time if lead_time else 0,
            "status": status,
        })

    return result


def get_machine_fleet(plant_id: str = "PLANT-01") -> List[Dict]:
    """Returns the full machine fleet from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id, name, type, line, status, oee, availability,
            performance, quality, failure_risk, production_capacity,
            current_utilization, last_maintenance, next_maintenance,
            vibration_level, temperature, runtime_hours
        FROM machines
        ORDER BY id
    """)

    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        (machine_id, name, mtype, line, status, oee, avail, perf, quality,
         failure_risk, capacity, utilization, last_maint, next_maint,
         vibration, temp, runtime) = row

        if status == 'down':
            alert_level = 'down'
            health_score = 0
        elif failure_risk > 0.5:
            alert_level = 'warning'
            health_score = int((1 - failure_risk) * 100)
        elif failure_risk > 0.2:
            alert_level = 'caution'
            health_score = int((1 - failure_risk) * 100)
        else:
            alert_level = 'normal'
            health_score = int((1 - failure_risk) * 100)

        age_years = round(runtime / 8760, 1) if runtime else 2.0

        result.append({
            "machine_id": machine_id,
            "machine_name": name,
            "production_line": line,
            "machine_type": mtype,
            "manufacturer": "Various",
            "model": "Model-" + machine_id,
            "age_years": age_years,
            "install_date": "2020-01-01",
            "max_output_units_per_day": capacity if capacity else 0,
            "status": status,
            "health_score": health_score,
            "alert_level": alert_level,
            "mtbf_days": 180,
            "mttr_days": 1.5,
            "last_maintenance_date": last_maint,
            "next_scheduled_maintenance": next_maint,
            "maintenance_cost_per_event": 1200,
            "unplanned_failure_cost_per_day": 8500,
        })

    return result


def get_sensor_readings(machine_id: str) -> Dict:
    """Returns the latest sensor readings from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Get distinct sensor types
    cursor.execute("""
        SELECT DISTINCT sensor_type
        FROM sensor_readings
        WHERE machine_id = ?
    """, (machine_id,))

    sensor_types = [row[0] for row in cursor.fetchall()]

    sensors = {}
    trend_7_day = {}

    for sensor_type in sensor_types:
        # Get latest reading
        cursor.execute("""
            SELECT value, unit, baseline, threshold_high, threshold_critical
            FROM sensor_readings
            WHERE machine_id = ? AND sensor_type = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (machine_id, sensor_type))

        latest = cursor.fetchone()
        if latest:
            value, unit, baseline, high, critical = latest
            sensors[sensor_type] = {
                "baseline": baseline,
                "current": value,
                "unit": unit,
                "high_threshold": high,
                "critical_threshold": critical,
            }

        # Get 7-day trend
        cursor.execute("""
            SELECT value
            FROM sensor_readings
            WHERE machine_id = ? AND sensor_type = ?
            ORDER BY timestamp DESC
            LIMIT 7
        """, (machine_id, sensor_type))

        trend_values = [row[0] for row in cursor.fetchall()]
        if trend_values:
            trend_7_day[sensor_type] = list(reversed(trend_values))

    # Get timestamp
    cursor.execute("""
        SELECT timestamp
        FROM sensor_readings
        WHERE machine_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
    """, (machine_id,))

    timestamp_row = cursor.fetchone()
    from datetime import datetime
    timestamp = timestamp_row[0] if timestamp_row else datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    conn.close()

    return {
        "machine_id": machine_id,
        "timestamp": timestamp,
        "sensors": sensors,
        "trend_7_day": trend_7_day,
    }


def get_maintenance_history(machine_id: str = None) -> List[Dict]:
    """Returns historical maintenance events from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    if machine_id:
        cursor.execute("""
            SELECT machine_id, date, type, technician, duration, notes
            FROM maintenance_history
            WHERE machine_id = ?
            ORDER BY date DESC
        """, (machine_id,))
    else:
        cursor.execute("""
            SELECT machine_id, date, type, technician, duration, notes
            FROM maintenance_history
            ORDER BY date DESC
        """)

    rows = cursor.fetchall()
    conn.close()

    result = []
    for i, row in enumerate(rows):
        mach_id, date, mtype, tech, duration, notes = row

        duration_days = float(duration.replace(" days", "").replace(" day", "")) if duration else 1.0
        cost = int(duration_days * 1200)
        production_lost = int(duration_days * 55)

        result.append({
            "event_id": f"MNT-{i+1:03d}",
            "machine_id": mach_id,
            "type": mtype,
            "date": date,
            "description": notes,
            "duration_days": duration_days,
            "cost": cost,
            "production_lost_units": production_lost,
            "root_cause": "Routine maintenance" if mtype == "planned" else notes,
        })

    return result


def get_oee_history(machine_id: str, periods: int = 6) -> List[Dict]:
    """Returns monthly OEE history from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT oee, availability, performance, quality
        FROM machines
        WHERE id = ?
    """, (machine_id,))

    current = cursor.fetchone()
    conn.close()

    if current:
        oee, avail, perf, quality = current
        # Generate 6 months of synthetic history
        result = []
        from datetime import datetime, timedelta
        base_date = datetime.now()
        for i in range(periods):
            month_date = base_date - timedelta(days=30 * i)
            period_str = month_date.strftime("%Y-%m")
            result.append({
                "period": period_str,
                "availability": round(avail, 2),
                "performance": round(perf, 2),
                "quality": round(quality, 3),
                "oee": round(oee, 3),
            })
        return list(reversed(result))
    return []


def get_production_lines() -> List[Dict]:
    """Returns production line definitions from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            pl.id, pl.name, pl.bottleneck_machine_id,
            pl.capacity_per_hour, pl.status, pl.utilization,
            pl.efficiency, m.name
        FROM production_lines pl
        LEFT JOIN machines m ON pl.bottleneck_machine_id = m.id
        ORDER BY pl.id
    """)

    rows = cursor.fetchall()

    # Get shift config
    cursor.execute("""
        SELECT shifts_per_day, hours_per_shift
        FROM shift_config
        LIMIT 1
    """)

    shift_row = cursor.fetchone()
    shifts_per_day = shift_row[0] if shift_row else 2
    hours_per_shift = shift_row[1] if shift_row else 8

    conn.close()

    result = []
    for row in rows:
        line_id, name, bottleneck_id, capacity_per_hour, status, utilization, efficiency, machine_name = row

        max_output_per_shift = int(capacity_per_hour * hours_per_shift / 60) if capacity_per_hour else 0
        max_output_per_day = max_output_per_shift * shifts_per_day
        effective_output_per_day = int(max_output_per_day * efficiency) if efficiency and status == 'operational' else 0

        result.append({
            "line_id": line_id,
            "line_name": name,
            "primary_machine": bottleneck_id,
            "machine_name": machine_name or "Unknown",
            "max_output_per_shift": max_output_per_shift,
            "shifts_per_day": shifts_per_day,
            "max_output_per_day": max_output_per_day,
            "status": status,
            "current_efficiency_pct": int(efficiency * 100) if efficiency else 0,
            "effective_output_per_day": effective_output_per_day,
            "estimated_return_date": "2026-02-23" if status == 'down' else None,
        })

    return result


def get_bill_of_materials(product_id: str = "PROD-A") -> Dict:
    """Returns the Bill of Materials from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM products
        WHERE id = ?
    """, (product_id,))

    product_row = cursor.fetchone()
    if not product_row:
        conn.close()
        return {}

    product_name = product_row[0]

    cursor.execute("""
        SELECT
            component_id, component_name, quantity, stock,
            supplier_id, cost
        FROM bom_items
        WHERE product_id = ?
    """, (product_id,))

    components = []
    total_cost = 0.0

    for row in cursor.fetchall():
        comp_id, comp_name, qty, stock, supplier, cost = row
        total_cost += cost * qty

        cursor.execute("""
            SELECT lead_time
            FROM suppliers
            WHERE id = ?
        """, (supplier,))

        supplier_row = cursor.fetchone()
        lead_time = supplier_row[0] if supplier_row else 5

        components.append({
            "component_id": comp_id,
            "component_name": comp_name,
            "qty_per_unit": qty,
            "unit_cost": cost,
            "supplier": supplier,
            "lead_time_days": lead_time,
            "current_stock_units": stock,
            "reorder_point": int(stock * 0.3),
        })

    conn.close()

    return {
        "product_id": product_id,
        "product_name": product_name,
        "unit_cost_total": round(total_cost, 2),
        "components": components,
    }


def get_production_history(product_id: str = "PROD-A", weeks: int = 8) -> List[Dict]:
    """Returns weekly production history from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            week_number, week_start_date, planned_production,
            actual_production, capacity, overtime_hours
        FROM production_schedule
        WHERE product_id = ?
        ORDER BY week_start_date DESC
        LIMIT ?
    """, (product_id, weeks))

    rows = cursor.fetchall()
    conn.close()

    result = []
    from datetime import datetime
    for row in rows:
        week_num, week_date, planned, actual, capacity, overtime = row

        date_obj = datetime.strptime(week_date, "%Y-%m-%d")
        week_str = f"{date_obj.year}-W{week_num:02d}"

        attainment_pct = round((actual / planned) * 100, 1) if planned and actual else None

        conn2 = sqlite3.connect(DATABASE_PATH)
        cursor2 = conn2.cursor()
        cursor2.execute("SELECT id FROM production_lines WHERE status != 'down'")
        active_lines = [row[0] for row in cursor2.fetchall()]
        conn2.close()

        result.append({
            "week": week_str,
            "planned_units": planned,
            "actual_units": actual,
            "attainment_pct": attainment_pct,
            "lines_active": active_lines,
            "shortfall_reason": None if attainment_pct and attainment_pct >= 98 else "Production variance",
            "overtime_hours": overtime,
        })

    return list(reversed(result))


def get_shift_configuration() -> Dict:
    """Returns the plant's shift schedule from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            shifts_per_day, hours_per_shift, days_per_week,
            overtime_available, max_overtime_hours
        FROM shift_config
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {
            "regular_shifts": {
                "shifts_per_day": 2,
                "hours_per_shift": 8,
                "regular_hours_per_day": 16,
                "days_per_week": 5,
                "weekend_available": True,
                "weekend_cost_premium_pct": 25,
            },
            "overtime": {
                "available": True,
                "max_overtime_hours_per_day": 4,
                "cost_premium_pct": 35,
                "max_consecutive_overtime_days": 5,
                "activation_lead_time_hours": 4,
                "additional_units_per_overtime_hour": 13,
            },
            "contract_manufacturing": {
                "available": True,
                "cost_premium_pct": 42,
                "activation_lead_time_days": 3,
                "min_order_units": 200,
                "max_capacity_units_per_week": 500,
                "quality_risk": "medium",
            },
            "current_base_capacity": {
                "effective_units_per_day": 196,
                "effective_units_per_week": 980,
                "note": "Based on current production line status",
            },
        }

    shifts, hours, days, overtime_avail, max_overtime = row

    return {
        "regular_shifts": {
            "shifts_per_day": shifts,
            "hours_per_shift": hours,
            "regular_hours_per_day": shifts * hours,
            "days_per_week": days,
            "weekend_available": True,
            "weekend_cost_premium_pct": 25,
        },
        "overtime": {
            "available": bool(overtime_avail),
            "max_overtime_hours_per_day": max_overtime,
            "cost_premium_pct": 35,
            "max_consecutive_overtime_days": 5,
            "activation_lead_time_hours": 4,
            "additional_units_per_overtime_hour": 13,
        },
        "contract_manufacturing": {
            "available": True,
            "cost_premium_pct": 42,
            "activation_lead_time_days": 3,
            "min_order_units": 200,
            "max_capacity_units_per_week": 500,
            "quality_risk": "medium",
        },
        "current_base_capacity": {
            "effective_units_per_day": 196,
            "effective_units_per_week": days * 196,
            "note": "Based on current production line status",
        },
    }


def get_open_purchase_orders(product_id: str = "PROD-A") -> List[Dict]:
    """Returns all currently open purchase orders from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            po.po_id, b.component_id, b.component_name,
            po.supplier_id, po.quantity, po.unit_cost, po.total_cost,
            po.order_date, po.expected_delivery_date, po.status, po.notes
        FROM purchase_orders po
        LEFT JOIN bom_items b ON po.product_id = b.product_id
        WHERE po.product_id = ? AND po.status IN ('open', 'in_transit', 'processing')
        ORDER BY po.expected_delivery_date
    """, (product_id,))

    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        po_id, comp_id, comp_name, supp_id, qty, unit_cost, total, order_date, delivery_date, status, notes = row

        result.append({
            "po_id": po_id,
            "component_id": comp_id or "PROD-" + po_id.split("-")[-1],
            "component_name": comp_name or "Product Component",
            "supplier_id": supp_id,
            "quantity_ordered": qty,
            "unit_cost": unit_cost,
            "total_cost": total,
            "order_date": order_date,
            "promised_delivery": delivery_date,
            "status": status,
            "tracking_note": notes or "Processing",
        })

    return result


def get_supplier_contracts() -> List[Dict]:
    """Returns active supplier contracts from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sc.id, sc.supplier_id, s.name, sc.start_date,
            sc.end_date, sc.status, s.payment_terms, s.moq
        FROM supplier_contracts sc
        JOIN suppliers s ON sc.supplier_id = s.id
        WHERE sc.status = 'active'
        ORDER BY sc.end_date
    """)

    rows = cursor.fetchall()
    conn.close()

    result = []
    from datetime import datetime
    for row in rows:
        contract_id, supp_id, supp_name, start_date, end_date, status, payment_terms, moq = row

        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        days_until_renewal = (end_date_obj - today).days

        result.append({
            "contract_id": contract_id,
            "supplier_id": supp_id,
            "supplier_name": supp_name,
            "contract_start": start_date,
            "contract_end": end_date,
            "status": status,
            "payment_terms": payment_terms,
            "base_unit_cost_by_component": {},
            "volume_discount_tiers": [
                {"min_units_per_order": 500, "discount_pct": 2.0},
                {"min_units_per_order": 1000, "discount_pct": 3.5},
            ],
            "min_order_value": moq * 10.0,
            "annual_spend_ytd": 0.0,
            "annual_spend_target": 120000.0,
            "preferred_supplier": supp_id == "SUP-A",
            "penalty_for_late_delivery_pct": 2.0,
            "contract_renewal_due_in_days": days_until_renewal if days_until_renewal > 0 else 0,
        })

    return result


def get_supply_chain_risk_factors() -> List[Dict]:
    """Returns supply chain risk assessment from database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            component_id, component_name, sourcing_type,
            qualified_suppliers, geographic_risk, lead_time_risk,
            risk_score, mitigation_strategy
        FROM supplier_risk
        ORDER BY risk_score DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        comp_id, comp_name, sourcing, qualified, geo_risk, lt_risk, risk_score, mitigation = row

        risk_flag = None
        if risk_score > 60:
            if "single" in sourcing.lower():
                risk_flag = f"SINGLE SOURCE - {comp_name}"
            else:
                risk_flag = f"HIGH RISK - {comp_name}"

        result.append({
            "component_id": comp_id,
            "component_name": comp_name,
            "sourcing_type": sourcing,
            "qualified_suppliers": [f"SUP-{chr(65+i)}" for i in range(qualified)],
            "geographic_risk": geo_risk,
            "lead_time_risk": lt_risk,
            "supplier_financial_health": "stable",
            "alternative_supplier_qualification_weeks": 12 if qualified == 1 else 0,
            "risk_score": risk_score,
            "risk_flag": risk_flag,
            "mitigation": mitigation,
        })

    return result
