"""
Simulated Manufacturing Data
In production, this would connect to your ERP/MES/database.
Here we simulate realistic data for demonstration.
"""
import random
import math
from datetime import datetime, timedelta


def get_historical_demand(product_id: str = "PROD-A", weeks: int = 12) -> list[dict]:
    """
    Returns weekly historical demand data.
    Simulates realistic patterns: trend + seasonality + noise + anomalies.
    """
    base_demand = 950
    trend = 15  # units increase per week
    seasonal_amplitude = 120
    noise_std = 60

    data = []
    today = datetime.now()

    for i in range(weeks, 0, -1):
        week_date = today - timedelta(weeks=i)
        week_num = week_date.isocalendar()[1]

        # Seasonal component (higher demand in Q4)
        seasonal = seasonal_amplitude * math.sin(2 * math.pi * week_num / 52)

        # Trend component
        trend_value = trend * (weeks - i)

        # Random noise
        noise = random.gauss(0, noise_std)

        # Occasional anomaly (spike or dip)
        anomaly = 0
        anomaly_flag = False
        if i == 3:  # Inject a spike 3 weeks ago
            anomaly = 380
            anomaly_flag = True

        demand = int(base_demand + trend_value + seasonal + noise + anomaly)
        demand = max(demand, 200)  # Floor

        data.append({
            "week": week_date.strftime("%Y-W%U"),
            "date": week_date.strftime("%Y-%m-%d"),
            "product_id": product_id,
            "demand_units": demand,
            "anomaly": anomaly_flag,
            "avg_price": round(88.50 + random.uniform(-3, 3), 2),
            "promotions_active": i in [3, 7],  # Promo weeks
            "competitor_price": round(92.00 + random.uniform(-5, 5), 2),
        })

    return data


def get_current_inventory(product_id: str = "PROD-A") -> dict:
    """Returns current inventory status."""
    return {
        "product_id": product_id,
        "current_stock": 1_850,
        "safety_stock": 300,
        "warehouse_capacity": 5_000,
        "warehouse_utilization_pct": 68,
        "avg_daily_consumption": 142,
        "days_of_supply": 13,
        "incoming_orders": [
            {"supplier": "Supplier A", "quantity": 500, "eta_days": 4},
            {"supplier": "Supplier B", "quantity": 300, "eta_days": 7},
        ],
        "unit_holding_cost": 2.30,
        "unit_stockout_cost": 45.00,
    }


def get_market_context() -> dict:
    """Returns external market context that affects demand."""
    return {
        "season": "Q1",
        "economic_indicator": "stable",  # stable, growing, contracting
        "industry_trend": "growing at 4.2% YoY",
        "raw_material_price_trend": "up 6% last quarter",
        "competitor_activity": "Competitor X launched a new product line last week",
        "social_media_mentions": {
            "volume": "2,400 mentions this week (up 180% from last week)",
            "sentiment": "78% positive",
            "top_topic": "viral TikTok video featuring our product",
        },
        "weather_forecast": "Normal conditions expected",
        "upcoming_events": [
            "Industry trade show in 3 weeks",
            "Major client contract renewal in 2 weeks",
        ],
    }


def get_production_capacity() -> dict:
    """Returns current production capacity info."""
    return {
        "max_daily_output": 220,
        "current_utilization_pct": 76,
        "available_lines": ["Line 1", "Line 2", "Line 3", "Line 5"],
        "lines_under_maintenance": ["Line 4"],
        "overtime_available": True,
        "overtime_cost_premium_pct": 35,
        "contract_manufacturer_available": True,
        "contract_manufacturer_cost_premium_pct": 42,
    }


def get_product_info(product_id: str = "PROD-A") -> dict:
    """Returns product-specific information."""
    return {
        "product_id": product_id,
        "product_name": "Industrial Valve Assembly - Type A",
        "unit_cost": 52.00,
        "unit_price": 89.50,
        "margin_pct": 41.9,
        "lead_time_days": 5,
        "shelf_life_days": None,  # Non-perishable
        "min_order_quantity": 100,
        "customer_segments": {
            "enterprise": {"share_pct": 55, "avg_order_size": 500},
            "mid_market": {"share_pct": 30, "avg_order_size": 150},
            "small_business": {"share_pct": 15, "avg_order_size": 40},
        },
    }


# ══════════════════════════════════════════════════════════════════
# Phase 2: Inventory Management Data
# ══════════════════════════════════════════════════════════════════

def get_warehouse_details(product_id: str = "PROD-A") -> dict:
    """Returns detailed warehouse zone information."""
    return {
        "product_id": product_id,
        "warehouse_id": "WH-MAIN",
        "total_capacity_units": 5000,
        "zones": [
            {
                "zone_id": "A",
                "zone_name": "Primary Storage",
                "capacity": 2500,
                "current_units": 1200,
                "utilization_pct": 48.0,
                "temperature_controlled": False,
                "zone_type": "bulk",
            },
            {
                "zone_id": "B",
                "zone_name": "Fast-Pick Area",
                "capacity": 1000,
                "current_units": 450,
                "utilization_pct": 45.0,
                "temperature_controlled": False,
                "zone_type": "pick_pack",
            },
            {
                "zone_id": "C",
                "zone_name": "Overflow / Seasonal",
                "capacity": 1500,
                "current_units": 200,
                "utilization_pct": 13.3,
                "temperature_controlled": False,
                "zone_type": "overflow",
            },
        ],
        "total_current_units": 1850,
        "total_utilization_pct": 37.0,
        "cost_per_zone_per_unit_per_day": {
            "A": 0.08,
            "B": 0.12,
            "C": 0.06,
        },
    }


def get_supplier_performance(product_id: str = "PROD-A") -> list[dict]:
    """Returns supplier reliability and lead time data."""
    return [
        {
            "supplier_id": "SUP-A",
            "supplier_name": "Supplier A",
            "product_id": product_id,
            "avg_lead_time_days": 4.2,
            "lead_time_std_dev_days": 0.8,
            "on_time_delivery_pct": 92.5,
            "quality_reject_rate_pct": 1.2,
            "unit_cost": 52.00,
            "min_order_quantity": 100,
            "max_order_quantity": 2000,
            "last_10_deliveries": [
                {"order_qty": 500, "delivered_qty": 500, "promised_days": 4, "actual_days": 4},
                {"order_qty": 600, "delivered_qty": 595, "promised_days": 4, "actual_days": 5},
                {"order_qty": 500, "delivered_qty": 500, "promised_days": 4, "actual_days": 4},
                {"order_qty": 700, "delivered_qty": 700, "promised_days": 5, "actual_days": 5},
                {"order_qty": 500, "delivered_qty": 498, "promised_days": 4, "actual_days": 3},
                {"order_qty": 800, "delivered_qty": 800, "promised_days": 5, "actual_days": 6},
                {"order_qty": 500, "delivered_qty": 500, "promised_days": 4, "actual_days": 4},
                {"order_qty": 600, "delivered_qty": 600, "promised_days": 4, "actual_days": 4},
                {"order_qty": 500, "delivered_qty": 500, "promised_days": 4, "actual_days": 5},
                {"order_qty": 700, "delivered_qty": 695, "promised_days": 5, "actual_days": 5},
            ],
        },
        {
            "supplier_id": "SUP-B",
            "supplier_name": "Supplier B",
            "product_id": product_id,
            "avg_lead_time_days": 6.8,
            "lead_time_std_dev_days": 1.5,
            "on_time_delivery_pct": 85.0,
            "quality_reject_rate_pct": 2.1,
            "unit_cost": 49.50,
            "min_order_quantity": 200,
            "max_order_quantity": 3000,
            "last_10_deliveries": [
                {"order_qty": 300, "delivered_qty": 300, "promised_days": 7, "actual_days": 7},
                {"order_qty": 400, "delivered_qty": 390, "promised_days": 7, "actual_days": 8},
                {"order_qty": 300, "delivered_qty": 300, "promised_days": 7, "actual_days": 7},
                {"order_qty": 500, "delivered_qty": 500, "promised_days": 7, "actual_days": 9},
                {"order_qty": 300, "delivered_qty": 300, "promised_days": 7, "actual_days": 7},
                {"order_qty": 600, "delivered_qty": 588, "promised_days": 8, "actual_days": 8},
                {"order_qty": 300, "delivered_qty": 300, "promised_days": 7, "actual_days": 6},
                {"order_qty": 400, "delivered_qty": 400, "promised_days": 7, "actual_days": 7},
                {"order_qty": 300, "delivered_qty": 300, "promised_days": 7, "actual_days": 8},
                {"order_qty": 500, "delivered_qty": 495, "promised_days": 7, "actual_days": 7},
            ],
        },
    ]


def get_historical_stockouts(product_id: str = "PROD-A") -> list[dict]:
    """Returns historical stockout events for analysis."""
    return [
        {
            "event_id": "SO-001",
            "product_id": product_id,
            "date": "2025-10-15",
            "duration_days": 3,
            "units_short": 420,
            "root_cause": "Supplier A delayed shipment by 4 days",
            "revenue_lost": 37590.00,
            "customers_affected": 8,
            "recovery_time_days": 5,
        },
        {
            "event_id": "SO-002",
            "product_id": product_id,
            "date": "2025-08-22",
            "duration_days": 1,
            "units_short": 180,
            "root_cause": "Unexpected demand spike from enterprise client",
            "revenue_lost": 16110.00,
            "customers_affected": 3,
            "recovery_time_days": 2,
        },
        {
            "event_id": "SO-003",
            "product_id": product_id,
            "date": "2025-06-03",
            "duration_days": 5,
            "units_short": 650,
            "root_cause": "Quality issue forced batch recall, depleted safety stock",
            "revenue_lost": 58175.00,
            "customers_affected": 12,
            "recovery_time_days": 8,
        },
    ]


def get_reorder_history(product_id: str = "PROD-A") -> list[dict]:
    """Returns last 8 reorder events with outcomes."""
    return [
        {"order_date": "2026-01-27", "supplier": "SUP-A", "qty": 500, "unit_cost": 52.00, "received_date": "2026-01-31", "lead_time_actual": 4, "status": "delivered"},
        {"order_date": "2026-01-20", "supplier": "SUP-B", "qty": 300, "unit_cost": 49.50, "received_date": "2026-01-27", "lead_time_actual": 7, "status": "delivered"},
        {"order_date": "2026-01-13", "supplier": "SUP-A", "qty": 600, "unit_cost": 52.00, "received_date": "2026-01-18", "lead_time_actual": 5, "status": "delivered"},
        {"order_date": "2026-01-06", "supplier": "SUP-A", "qty": 500, "unit_cost": 52.00, "received_date": "2026-01-10", "lead_time_actual": 4, "status": "delivered"},
        {"order_date": "2025-12-30", "supplier": "SUP-B", "qty": 400, "unit_cost": 49.50, "received_date": "2026-01-06", "lead_time_actual": 7, "status": "delivered"},
        {"order_date": "2025-12-23", "supplier": "SUP-A", "qty": 700, "unit_cost": 52.00, "received_date": "2025-12-29", "lead_time_actual": 6, "status": "delivered"},
        {"order_date": "2025-12-16", "supplier": "SUP-A", "qty": 500, "unit_cost": 52.00, "received_date": "2025-12-20", "lead_time_actual": 4, "status": "delivered"},
        {"order_date": "2025-12-09", "supplier": "SUP-B", "qty": 300, "unit_cost": 49.50, "received_date": "2025-12-17", "lead_time_actual": 8, "status": "delivered"},
    ]


# ══════════════════════════════════════════════════════════════════
# Phase 3: Machine Health Agent Data
# ══════════════════════════════════════════════════════════════════

def get_machine_fleet(plant_id: str = "PLANT-01") -> list[dict]:
    """
    Returns the full machine fleet for the plant.
    Each machine maps to a production line and has specs, age, and current status.
    """
    return [
        {
            "machine_id": "MCH-001",
            "machine_name": "Assembly Robot - Line 1",
            "production_line": "Line 1",
            "machine_type": "robotic_assembly",
            "manufacturer": "KUKA Systems",
            "model": "KR-210 R2700",
            "age_years": 3.1,
            "install_date": "2022-12-01",
            "max_output_units_per_day": 55,
            "status": "operational",
            "health_score": 91,          # 0-100
            "alert_level": "normal",     # normal / caution / warning / critical / down
            "mtbf_days": 180,
            "mttr_days": 1.5,
            "last_maintenance_date": "2026-01-10",
            "next_scheduled_maintenance": "2026-03-10",
            "maintenance_cost_per_event": 1_200,
            "unplanned_failure_cost_per_day": 8_500,
        },
        {
            "machine_id": "MCH-002",
            "machine_name": "CNC Machining Center - Line 2",
            "production_line": "Line 2",
            "machine_type": "cnc_machining",
            "manufacturer": "Haas Automation",
            "model": "VF-4SS",
            "age_years": 6.4,
            "install_date": "2019-09-15",
            "max_output_units_per_day": 60,
            "status": "operational",
            "health_score": 58,
            "alert_level": "warning",
            "mtbf_days": 90,
            "mttr_days": 3.0,
            "last_maintenance_date": "2025-11-20",
            "next_scheduled_maintenance": "2026-02-28",
            "maintenance_cost_per_event": 3_500,
            "unplanned_failure_cost_per_day": 12_000,
        },
        {
            "machine_id": "MCH-003",
            "machine_name": "Hydraulic Press - Line 3",
            "production_line": "Line 3",
            "machine_type": "hydraulic_press",
            "manufacturer": "Schuler AG",
            "model": "MSP-400",
            "age_years": 4.2,
            "install_date": "2021-11-05",
            "max_output_units_per_day": 50,
            "status": "operational",
            "health_score": 74,
            "alert_level": "caution",
            "mtbf_days": 120,
            "mttr_days": 2.0,
            "last_maintenance_date": "2025-12-15",
            "next_scheduled_maintenance": "2026-03-01",
            "maintenance_cost_per_event": 2_200,
            "unplanned_failure_cost_per_day": 9_800,
        },
        {
            "machine_id": "MCH-004",
            "machine_name": "Conveyor & Material Handling - Line 4",
            "production_line": "Line 4",
            "machine_type": "conveyor_system",
            "manufacturer": "Dorner Mfg",
            "model": "AquaPruf 7400",
            "age_years": 7.8,
            "install_date": "2018-05-22",
            "max_output_units_per_day": 45,
            "status": "down",
            "health_score": 0,
            "alert_level": "down",
            "mtbf_days": 45,
            "mttr_days": 5.0,
            "last_maintenance_date": "2026-02-18",
            "next_scheduled_maintenance": "2026-02-23",   # expected return-to-service
            "maintenance_cost_per_event": 5_800,
            "unplanned_failure_cost_per_day": 7_200,
            "downtime_reason": "Bearing seizure on main drive shaft — corrective maintenance in progress",
            "downtime_start": "2026-02-18",
            "estimated_return": "2026-02-23",
        },
        {
            "machine_id": "MCH-005",
            "machine_name": "Welding Station - Line 5",
            "production_line": "Line 5",
            "machine_type": "welding_station",
            "manufacturer": "Lincoln Electric",
            "model": "Power Wave S500",
            "age_years": 2.0,
            "install_date": "2024-02-01",
            "max_output_units_per_day": 58,
            "status": "operational",
            "health_score": 96,
            "alert_level": "normal",
            "mtbf_days": 240,
            "mttr_days": 1.0,
            "last_maintenance_date": "2026-01-25",
            "next_scheduled_maintenance": "2026-04-25",
            "maintenance_cost_per_event": 900,
            "unplanned_failure_cost_per_day": 8_000,
        },
        {
            "machine_id": "MCH-006",
            "machine_name": "Automated Quality Inspection System",
            "production_line": "All Lines",
            "machine_type": "quality_inspection",
            "manufacturer": "Cognex",
            "model": "In-Sight 9000",
            "age_years": 1.2,
            "install_date": "2025-01-10",
            "max_output_units_per_day": None,   # Support role, not a bottleneck
            "status": "operational",
            "health_score": 98,
            "alert_level": "normal",
            "mtbf_days": 365,
            "mttr_days": 0.5,
            "last_maintenance_date": "2026-02-01",
            "next_scheduled_maintenance": "2026-08-01",
            "maintenance_cost_per_event": 600,
            "unplanned_failure_cost_per_day": 15_000,   # Stops all QC if down
        },
    ]


def get_sensor_readings(machine_id: str) -> dict:
    """
    Returns the latest sensor readings for a machine, baselines, and a 7-day trend.
    In production this would pull from SCADA/IoT platforms.
    """
    sensor_profiles = {
        "MCH-001": {
            "machine_id": "MCH-001",
            "timestamp": "2026-02-21T08:00:00",
            "sensors": {
                "vibration_mm_s2":    {"baseline": 2.1, "current": 2.3,  "unit": "mm/s²",  "high_threshold": 3.5, "critical_threshold": 5.0},
                "temperature_c":      {"baseline": 45,  "current": 47,   "unit": "°C",     "high_threshold": 65,  "critical_threshold": 80},
                "current_draw_a":     {"baseline": 18,  "current": 18.5, "unit": "A",      "high_threshold": 24,  "critical_threshold": 28},
                "cycle_time_sec":     {"baseline": 8.2, "current": 8.4,  "unit": "s",      "high_threshold": 9.5, "critical_threshold": 11.0},
            },
            "trend_7_day": {
                "vibration_mm_s2": [2.0, 2.1, 2.2, 2.1, 2.3, 2.2, 2.3],
                "temperature_c":   [44,  45,  45,  46,  46,  47,  47],
            },
        },
        "MCH-002": {
            "machine_id": "MCH-002",
            "timestamp": "2026-02-21T08:00:00",
            "sensors": {
                "vibration_mm_s2":    {"baseline": 1.8, "current": 4.2,  "unit": "mm/s²",  "high_threshold": 3.0, "critical_threshold": 5.5},
                "temperature_c":      {"baseline": 72,  "current": 81,   "unit": "°C",     "high_threshold": 85,  "critical_threshold": 95},
                "spindle_rpm":        {"baseline": 3000,"current": 2850, "unit": "RPM",    "high_threshold": None,"critical_threshold": 2500},
                "current_draw_a":     {"baseline": 42,  "current": 47,   "unit": "A",      "high_threshold": 52,  "critical_threshold": 60},
                "noise_db":           {"baseline": 68,  "current": 79,   "unit": "dB",     "high_threshold": 80,  "critical_threshold": 90},
            },
            "trend_7_day": {
                "vibration_mm_s2": [2.0, 2.4, 2.8, 3.1, 3.5, 3.9, 4.2],
                "temperature_c":   [73,  74,  75,  77,  78,  80,  81],
            },
        },
        "MCH-003": {
            "machine_id": "MCH-003",
            "timestamp": "2026-02-21T08:00:00",
            "sensors": {
                "vibration_mm_s2":    {"baseline": 3.5, "current": 3.8,  "unit": "mm/s²",  "high_threshold": 5.5, "critical_threshold": 8.0},
                "temperature_c":      {"baseline": 68,  "current": 78,   "unit": "°C",     "high_threshold": 85,  "critical_threshold": 100},
                "hydraulic_pressure_bar": {"baseline": 180, "current": 174, "unit": "bar", "high_threshold": None, "critical_threshold": 150},
                "current_draw_a":     {"baseline": 35,  "current": 37,   "unit": "A",      "high_threshold": 44,  "critical_threshold": 50},
            },
            "trend_7_day": {
                "temperature_c":   [69, 70, 72, 73, 75, 77, 78],
                "hydraulic_pressure_bar": [180, 179, 178, 177, 176, 175, 174],
            },
        },
        "MCH-004": {
            "machine_id": "MCH-004",
            "timestamp": "2026-02-21T08:00:00",
            "sensors": {},  # Machine is down, no live sensor data
            "trend_7_day": {
                "vibration_mm_s2": [3.2, 4.1, 5.8, 7.9, 11.2, None, None],  # Spike before failure
                "temperature_c":   [55,  58,  62,  68,  74,   None, None],
            },
            "failure_event": {
                "date": "2026-02-18",
                "sensor_at_failure": {"vibration_mm_s2": 11.2, "temperature_c": 74},
                "root_cause": "Bearing seizure — vibration exceeded critical threshold",
            },
        },
        "MCH-005": {
            "machine_id": "MCH-005",
            "timestamp": "2026-02-21T08:00:00",
            "sensors": {
                "vibration_mm_s2":    {"baseline": 1.2, "current": 1.3,  "unit": "mm/s²",  "high_threshold": 2.5, "critical_threshold": 4.0},
                "temperature_c":      {"baseline": 38,  "current": 39,   "unit": "°C",     "high_threshold": 55,  "critical_threshold": 70},
                "wire_feed_speed_m_min": {"baseline": 8.5, "current": 8.5, "unit": "m/min", "high_threshold": None, "critical_threshold": None},
                "current_draw_a":     {"baseline": 28,  "current": 28,   "unit": "A",      "high_threshold": 36,  "critical_threshold": 42},
            },
            "trend_7_day": {
                "vibration_mm_s2": [1.2, 1.2, 1.3, 1.2, 1.3, 1.2, 1.3],
                "temperature_c":   [38,  38,  39,  38,  39,  39,  39],
            },
        },
        "MCH-006": {
            "machine_id": "MCH-006",
            "timestamp": "2026-02-21T08:00:00",
            "sensors": {
                "temperature_c":      {"baseline": 32, "current": 33, "unit": "°C", "high_threshold": 45, "critical_threshold": 55},
                "processing_latency_ms": {"baseline": 120, "current": 122, "unit": "ms", "high_threshold": 200, "critical_threshold": 500},
            },
            "trend_7_day": {
                "temperature_c": [32, 32, 33, 32, 33, 33, 33],
            },
        },
    }
    return sensor_profiles.get(machine_id, {"error": f"Machine {machine_id} not found"})


def get_maintenance_history(machine_id: str = None) -> list[dict]:
    """
    Returns historical maintenance events (planned and unplanned) for all machines
    or a specific machine.
    """
    history = [
        {"event_id": "MNT-001", "machine_id": "MCH-002", "type": "unplanned", "date": "2025-08-14",
         "description": "Spindle bearing replacement after vibration alarm", "duration_days": 2.5,
         "cost": 4_200, "production_lost_units": 150, "root_cause": "Worn bearing — missed PM window"},
        {"event_id": "MNT-002", "machine_id": "MCH-001", "type": "planned", "date": "2026-01-10",
         "description": "Scheduled 3-month preventive maintenance", "duration_days": 1.0,
         "cost": 1_100, "production_lost_units": 55, "root_cause": None},
        {"event_id": "MNT-003", "machine_id": "MCH-003", "type": "unplanned", "date": "2025-09-28",
         "description": "Hydraulic seal replacement — oil leak detected", "duration_days": 1.5,
         "cost": 1_800, "production_lost_units": 75, "root_cause": "Seal age degradation"},
        {"event_id": "MNT-004", "machine_id": "MCH-005", "type": "planned", "date": "2026-01-25",
         "description": "Scheduled 6-month preventive maintenance + torch inspection", "duration_days": 0.5,
         "cost": 850, "production_lost_units": 29, "root_cause": None},
        {"event_id": "MNT-005", "machine_id": "MCH-004", "type": "unplanned", "date": "2026-02-18",
         "description": "Bearing seizure — conveyor drive shaft failure", "duration_days": 5.0,
         "cost": 5_800, "production_lost_units": 225, "root_cause": "Bearing fatigue — age 7.8 years"},
        {"event_id": "MNT-006", "machine_id": "MCH-003", "type": "planned", "date": "2025-12-15",
         "description": "Hydraulic fluid change + filter replacement", "duration_days": 0.5,
         "cost": 650, "production_lost_units": 25, "root_cause": None},
        {"event_id": "MNT-007", "machine_id": "MCH-002", "type": "planned", "date": "2025-11-20",
         "description": "Quarterly PM — lubrication, tool changer inspection", "duration_days": 1.0,
         "cost": 2_800, "production_lost_units": 60, "root_cause": None},
    ]
    if machine_id:
        return [e for e in history if e["machine_id"] == machine_id]
    return history


def get_oee_history(machine_id: str, periods: int = 6) -> list[dict]:
    """
    Returns monthly OEE (Overall Equipment Effectiveness) history.
    OEE = Availability × Performance × Quality Rate
    """
    oee_data = {
        "MCH-001": [
            {"period": "2025-09", "availability": 0.97, "performance": 0.93, "quality": 0.993, "oee": 0.896},
            {"period": "2025-10", "availability": 0.96, "performance": 0.92, "quality": 0.991, "oee": 0.875},
            {"period": "2025-11", "availability": 0.97, "performance": 0.93, "quality": 0.994, "oee": 0.896},
            {"period": "2025-12", "availability": 0.96, "performance": 0.91, "quality": 0.992, "oee": 0.866},
            {"period": "2026-01", "availability": 0.94, "performance": 0.92, "quality": 0.993, "oee": 0.859},  # PM event
            {"period": "2026-02", "availability": 0.96, "performance": 0.92, "quality": 0.992, "oee": 0.876},
        ],
        "MCH-002": [
            {"period": "2025-09", "availability": 0.93, "performance": 0.88, "quality": 0.979, "oee": 0.801},
            {"period": "2025-10", "availability": 0.91, "performance": 0.85, "quality": 0.975, "oee": 0.754},
            {"period": "2025-11", "availability": 0.89, "performance": 0.83, "quality": 0.972, "oee": 0.718},  # PM event
            {"period": "2025-12", "availability": 0.90, "performance": 0.82, "quality": 0.974, "oee": 0.719},
            {"period": "2026-01", "availability": 0.88, "performance": 0.80, "quality": 0.971, "oee": 0.683},
            {"period": "2026-02", "availability": 0.85, "performance": 0.77, "quality": 0.968, "oee": 0.634},  # Declining
        ],
        "MCH-003": [
            {"period": "2025-09", "availability": 0.93, "performance": 0.90, "quality": 0.987, "oee": 0.826},
            {"period": "2025-10", "availability": 0.92, "performance": 0.89, "quality": 0.985, "oee": 0.806},  # Unplanned repair
            {"period": "2025-11", "availability": 0.94, "performance": 0.91, "quality": 0.988, "oee": 0.845},
            {"period": "2025-12", "availability": 0.93, "performance": 0.90, "quality": 0.986, "oee": 0.826},  # PM event
            {"period": "2026-01", "availability": 0.93, "performance": 0.89, "quality": 0.985, "oee": 0.815},
            {"period": "2026-02", "availability": 0.91, "performance": 0.88, "quality": 0.984, "oee": 0.789},  # Slight decline
        ],
        "MCH-004": [
            {"period": "2025-09", "availability": 0.88, "performance": 0.84, "quality": 0.981, "oee": 0.725},
            {"period": "2025-10", "availability": 0.85, "performance": 0.82, "quality": 0.979, "oee": 0.683},
            {"period": "2025-11", "availability": 0.83, "performance": 0.80, "quality": 0.977, "oee": 0.648},
            {"period": "2025-12", "availability": 0.81, "performance": 0.79, "quality": 0.975, "oee": 0.624},
            {"period": "2026-01", "availability": 0.78, "performance": 0.76, "quality": 0.972, "oee": 0.577},
            {"period": "2026-02", "availability": 0.30, "performance": 0.0,  "quality": 0.0,   "oee": 0.0},   # Down
        ],
        "MCH-005": [
            {"period": "2025-09", "availability": 0.98, "performance": 0.96, "quality": 0.996, "oee": 0.937},
            {"period": "2025-10", "availability": 0.99, "performance": 0.96, "quality": 0.995, "oee": 0.946},
            {"period": "2025-11", "availability": 0.98, "performance": 0.95, "quality": 0.995, "oee": 0.926},
            {"period": "2025-12", "availability": 0.99, "performance": 0.96, "quality": 0.996, "oee": 0.946},
            {"period": "2026-01", "availability": 0.97, "performance": 0.95, "quality": 0.995, "oee": 0.917},  # PM event
            {"period": "2026-02", "availability": 0.98, "performance": 0.96, "quality": 0.996, "oee": 0.937},
        ],
        "MCH-006": [
            {"period": "2025-09", "availability": 0.99, "performance": 0.98, "quality": 0.999, "oee": 0.969},
            {"period": "2025-10", "availability": 0.99, "performance": 0.97, "quality": 0.998, "oee": 0.959},
            {"period": "2025-11", "availability": 1.0,  "performance": 0.98, "quality": 0.999, "oee": 0.979},
            {"period": "2025-12", "availability": 0.99, "performance": 0.97, "quality": 0.998, "oee": 0.959},
            {"period": "2026-01", "availability": 0.99, "performance": 0.98, "quality": 0.999, "oee": 0.969},
            {"period": "2026-02", "availability": 0.99, "performance": 0.97, "quality": 0.998, "oee": 0.959},
        ],
    }
    data = oee_data.get(machine_id, [])
    return data[-periods:]


# ══════════════════════════════════════════════════════════════════
# Phase 4: Production Planning Agent Data
# ══════════════════════════════════════════════════════════════════

def get_production_lines() -> list[dict]:
    """
    Returns each production line definition, its assigned machines,
    current capacity status, and shift configuration.
    """
    return [
        {
            "line_id": "Line 1",
            "line_name": "Assembly Line 1",
            "primary_machine": "MCH-001",
            "machine_name": "Assembly Robot - Line 1",
            "max_output_per_shift": 28,       # units per 8-hour shift
            "shifts_per_day": 2,
            "max_output_per_day": 55,
            "status": "operational",
            "current_efficiency_pct": 92,     # relative to max, based on OEE
            "effective_output_per_day": 51,   # max * efficiency
        },
        {
            "line_id": "Line 2",
            "line_name": "CNC Machining Line 2",
            "primary_machine": "MCH-002",
            "machine_name": "CNC Machining Center - Line 2",
            "max_output_per_shift": 30,
            "shifts_per_day": 2,
            "max_output_per_day": 60,
            "status": "operational",
            "current_efficiency_pct": 75,     # Degraded — warning-level health
            "effective_output_per_day": 45,
        },
        {
            "line_id": "Line 3",
            "line_name": "Hydraulic Press Line 3",
            "primary_machine": "MCH-003",
            "machine_name": "Hydraulic Press - Line 3",
            "max_output_per_shift": 25,
            "shifts_per_day": 2,
            "max_output_per_day": 50,
            "status": "operational",
            "current_efficiency_pct": 88,     # Slightly degraded — caution
            "effective_output_per_day": 44,
        },
        {
            "line_id": "Line 4",
            "line_name": "Conveyor Line 4",
            "primary_machine": "MCH-004",
            "machine_name": "Conveyor & Material Handling - Line 4",
            "max_output_per_shift": 23,
            "shifts_per_day": 2,
            "max_output_per_day": 45,
            "status": "down",
            "current_efficiency_pct": 0,
            "effective_output_per_day": 0,
            "estimated_return_date": "2026-02-23",
        },
        {
            "line_id": "Line 5",
            "line_name": "Welding Line 5",
            "primary_machine": "MCH-005",
            "machine_name": "Welding Station - Line 5",
            "max_output_per_shift": 29,
            "shifts_per_day": 2,
            "max_output_per_day": 58,
            "status": "operational",
            "current_efficiency_pct": 96,
            "effective_output_per_day": 56,
        },
    ]


def get_bill_of_materials(product_id: str = "PROD-A") -> dict:
    """
    Returns the Bill of Materials (BOM) for a product.
    Defines which raw materials/components are needed to produce one unit.
    In production this would connect to ERP/PLM systems.
    """
    bom = {
        "PROD-A": {
            "product_id": "PROD-A",
            "product_name": "Industrial Valve Assembly - Type A",
            "unit_cost_total": 52.00,
            "components": [
                {
                    "component_id": "SH-100",
                    "component_name": "Steel Housing",
                    "qty_per_unit": 1,
                    "unit_cost": 25.00,
                    "supplier": "SUP-A",
                    "lead_time_days": 4,
                    "current_stock_units": 2100,
                    "reorder_point": 600,
                },
                {
                    "component_id": "VSA-200",
                    "component_name": "Valve Seat Assembly",
                    "qty_per_unit": 1,
                    "unit_cost": 14.00,
                    "supplier": "SUP-B",
                    "lead_time_days": 7,
                    "current_stock_units": 1650,
                    "reorder_point": 500,
                },
                {
                    "component_id": "AM-300",
                    "component_name": "Actuator Motor",
                    "qty_per_unit": 1,
                    "unit_cost": 8.50,
                    "supplier": "SUP-A",
                    "lead_time_days": 4,
                    "current_stock_units": 1900,
                    "reorder_point": 550,
                },
                {
                    "component_id": "SOR-400",
                    "component_name": "Seals & O-rings Kit",
                    "qty_per_unit": 1,
                    "unit_cost": 2.50,
                    "supplier": "SUP-A",
                    "lead_time_days": 3,
                    "current_stock_units": 3200,
                    "reorder_point": 800,
                },
                {
                    "component_id": "FS-500",
                    "component_name": "Fastener Set",
                    "qty_per_unit": 1,
                    "unit_cost": 1.50,
                    "supplier": "SUP-A",
                    "lead_time_days": 3,
                    "current_stock_units": 4100,
                    "reorder_point": 1000,
                },
                {
                    "component_id": "IL-600",
                    "component_name": "Inspection Labels & Packaging",
                    "qty_per_unit": 1,
                    "unit_cost": 0.50,
                    "supplier": "SUP-A",
                    "lead_time_days": 2,
                    "current_stock_units": 5000,
                    "reorder_point": 1200,
                },
            ],
        }
    }
    return bom.get(product_id, {})


def get_production_history(product_id: str = "PROD-A", weeks: int = 8) -> list[dict]:
    """
    Returns weekly production history: planned vs actual output,
    with reasons for any shortfall.
    """
    return [
        {
            "week": "2025-W46", "planned_units": 1050, "actual_units": 1048,
            "attainment_pct": 99.8, "lines_active": ["Line 1","Line 2","Line 3","Line 4","Line 5"],
            "shortfall_reason": None, "overtime_hours": 0,
        },
        {
            "week": "2025-W47", "planned_units": 1050, "actual_units": 1035,
            "attainment_pct": 98.6, "lines_active": ["Line 1","Line 2","Line 3","Line 4","Line 5"],
            "shortfall_reason": "Minor CNC tool change delay", "overtime_hours": 2,
        },
        {
            "week": "2025-W48", "planned_units": 1050, "actual_units": 1050,
            "attainment_pct": 100.0, "lines_active": ["Line 1","Line 2","Line 3","Line 4","Line 5"],
            "shortfall_reason": None, "overtime_hours": 0,
        },
        {
            "week": "2025-W49", "planned_units": 1050, "actual_units": 972,
            "attainment_pct": 92.6, "lines_active": ["Line 1","Line 2","Line 3","Line 4","Line 5"],
            "shortfall_reason": "MCH-002 spindle bearing unplanned repair (2.5 days down)", "overtime_hours": 8,
        },
        {
            "week": "2025-W50", "planned_units": 1050, "actual_units": 1044,
            "attainment_pct": 99.4, "lines_active": ["Line 1","Line 2","Line 3","Line 4","Line 5"],
            "shortfall_reason": "MCH-002 recovery — still running at 85% speed", "overtime_hours": 4,
        },
        {
            "week": "2026-W03", "planned_units": 1050, "actual_units": 1038,
            "attainment_pct": 98.9, "lines_active": ["Line 1","Line 2","Line 3","Line 4","Line 5"],
            "shortfall_reason": "MCH-001 scheduled PM (1 day offline)", "overtime_hours": 2,
        },
        {
            "week": "2026-W06", "planned_units": 1050, "actual_units": 987,
            "attainment_pct": 94.0, "lines_active": ["Line 1","Line 2","Line 3","Line 5"],
            "shortfall_reason": "MCH-004 bearing failure — Line 4 down since Feb 18", "overtime_hours": 12,
        },
        {
            "week": "2026-W07", "planned_units": 945, "actual_units": None,
            "attainment_pct": None, "lines_active": ["Line 1","Line 2","Line 3","Line 5"],
            "shortfall_reason": "Current week — Line 4 still down, MCH-002 on warning", "overtime_hours": None,
        },
    ]


def get_shift_configuration() -> dict:
    """
    Returns the plant's shift schedule and overtime/contract manufacturing options.
    """
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
            "additional_units_per_overtime_hour": 13,  # across all active lines
        },
        "contract_manufacturing": {
            "available": True,
            "cost_premium_pct": 42,
            "activation_lead_time_days": 3,
            "min_order_units": 200,
            "max_capacity_units_per_week": 500,
            "quality_risk": "medium",   # lower process control than in-house
        },
        "current_base_capacity": {
            "effective_units_per_day": 196,   # sum of all active line effective outputs
            "effective_units_per_week": 980,  # 5 days
            "note": "Reduced from normal 1,050/week due to Line 4 down + MCH-002 degradation",
        },
    }


# ══════════════════════════════════════════════════════════════════
# Phase 5: Supplier & Procurement Agent Data
# ══════════════════════════════════════════════════════════════════

def get_open_purchase_orders(product_id: str = "PROD-A") -> list[dict]:
    """
    Returns all currently open (undelivered) purchase orders.
    In production this would connect to the ERP purchasing module.
    """
    return [
        {
            "po_id": "PO-2026-018",
            "component_id": "SH-100",
            "component_name": "Steel Housing",
            "supplier_id": "SUP-A",
            "quantity_ordered": 600,
            "unit_cost": 25.00,
            "total_cost": 15000.00,
            "order_date": "2026-02-17",
            "promised_delivery": "2026-02-21",
            "status": "in_transit",
            "tracking_note": "Shipment confirmed, on time",
        },
        {
            "po_id": "PO-2026-019",
            "component_id": "VSA-200",
            "component_name": "Valve Seat Assembly",
            "supplier_id": "SUP-B",
            "quantity_ordered": 400,
            "unit_cost": 14.00,
            "total_cost": 5600.00,
            "order_date": "2026-02-14",
            "promised_delivery": "2026-02-21",
            "status": "in_transit",
            "tracking_note": "Shipment confirmed, on time",
        },
        {
            "po_id": "PO-2026-020",
            "component_id": "AM-300",
            "component_name": "Actuator Motor",
            "supplier_id": "SUP-A",
            "quantity_ordered": 500,
            "unit_cost": 8.50,
            "total_cost": 4250.00,
            "order_date": "2026-02-18",
            "promised_delivery": "2026-02-22",
            "status": "processing",
            "tracking_note": "Awaiting dispatch from supplier warehouse",
        },
        {
            "po_id": "PO-2026-021",
            "component_id": "SOR-400",
            "component_name": "Seals & O-rings Kit",
            "supplier_id": "SUP-A",
            "quantity_ordered": 800,
            "unit_cost": 2.50,
            "total_cost": 2000.00,
            "order_date": "2026-02-19",
            "promised_delivery": "2026-02-22",
            "status": "processing",
            "tracking_note": "Awaiting dispatch",
        },
    ]


def get_supplier_contracts() -> list[dict]:
    """
    Returns active supplier contracts with pricing tiers, payment terms, and constraints.
    """
    return [
        {
            "contract_id": "CTR-SUP-A-2026",
            "supplier_id": "SUP-A",
            "supplier_name": "Supplier A",
            "contract_start": "2026-01-01",
            "contract_end": "2026-12-31",
            "status": "active",
            "payment_terms": "NET-30",
            "base_unit_cost_by_component": {
                "SH-100": 25.00,
                "AM-300": 8.50,
                "SOR-400": 2.50,
                "FS-500": 1.50,
                "IL-600": 0.50,
            },
            "volume_discount_tiers": [
                {"min_units_per_order": 500,  "discount_pct": 2.0},
                {"min_units_per_order": 1000, "discount_pct": 3.5},
                {"min_units_per_order": 2000, "discount_pct": 5.0},
            ],
            "min_order_value": 1000.00,
            "annual_spend_ytd": 86400.00,
            "annual_spend_target": 420000.00,
            "preferred_supplier": True,
            "penalty_for_late_delivery_pct": 2.0,
        },
        {
            "contract_id": "CTR-SUP-B-2026",
            "supplier_id": "SUP-B",
            "supplier_name": "Supplier B",
            "contract_start": "2026-01-01",
            "contract_end": "2026-06-30",
            "status": "active",
            "payment_terms": "NET-45",
            "base_unit_cost_by_component": {
                "VSA-200": 14.00,
                "SH-100": 26.50,    # Slightly higher than SUP-A for same component
                "AM-300": 9.20,
            },
            "volume_discount_tiers": [
                {"min_units_per_order": 300,  "discount_pct": 1.5},
                {"min_units_per_order": 800,  "discount_pct": 3.0},
            ],
            "min_order_value": 500.00,
            "annual_spend_ytd": 22400.00,
            "annual_spend_target": 120000.00,
            "preferred_supplier": False,
            "penalty_for_late_delivery_pct": 1.5,
            "contract_renewal_due_in_days": 128,
        },
    ]


def get_supply_chain_risk_factors() -> list[dict]:
    """
    Returns supply chain risk assessment per component.
    Covers sourcing concentration, geographic risk, and supplier stability.
    """
    return [
        {
            "component_id": "SH-100",
            "component_name": "Steel Housing",
            "sourcing_type": "single_source",       # Only SUP-A qualifies
            "qualified_suppliers": ["SUP-A"],
            "geographic_risk": "low",               # Domestic supplier
            "lead_time_risk": "medium",             # 4 day LT with 0.8 day std dev
            "supplier_financial_health": "stable",
            "alternative_supplier_qualification_weeks": 12,
            "risk_score": 65,                       # 0-100, higher = more risk
            "risk_flag": "SINGLE SOURCE — no backup if SUP-A fails",
            "mitigation": "Qualify SUP-B for Steel Housing; maintain 3-week safety stock",
        },
        {
            "component_id": "VSA-200",
            "component_name": "Valve Seat Assembly",
            "sourcing_type": "dual_source",
            "qualified_suppliers": ["SUP-B", "SUP-A"],
            "geographic_risk": "low",
            "lead_time_risk": "medium",             # 7 day LT with 1.5 day std dev
            "supplier_financial_health": "stable",
            "alternative_supplier_qualification_weeks": 0,  # SUP-A already qualified
            "risk_score": 35,
            "risk_flag": None,
            "mitigation": "Maintain dual sourcing; increase SUP-A share if SUP-B contract lapses",
        },
        {
            "component_id": "AM-300",
            "component_name": "Actuator Motor",
            "sourcing_type": "single_source",
            "qualified_suppliers": ["SUP-A"],
            "geographic_risk": "medium",            # Regional — some tariff exposure
            "lead_time_risk": "low",
            "supplier_financial_health": "stable",
            "alternative_supplier_qualification_weeks": 16,
            "risk_score": 72,
            "risk_flag": "SINGLE SOURCE + GEOGRAPHIC RISK — tariff exposure on regional imports",
            "mitigation": "Identify domestic alternative; increase safety stock to 4 weeks",
        },
        {
            "component_id": "SOR-400",
            "component_name": "Seals & O-rings Kit",
            "sourcing_type": "multi_source",
            "qualified_suppliers": ["SUP-A", "SUP-B", "Spot market"],
            "geographic_risk": "low",
            "lead_time_risk": "low",
            "supplier_financial_health": "stable",
            "alternative_supplier_qualification_weeks": 0,
            "risk_score": 15,
            "risk_flag": None,
            "mitigation": "Commodity item — no action required",
        },
        {
            "component_id": "FS-500",
            "component_name": "Fastener Set",
            "sourcing_type": "multi_source",
            "qualified_suppliers": ["SUP-A", "SUP-B", "Spot market"],
            "geographic_risk": "low",
            "lead_time_risk": "low",
            "supplier_financial_health": "stable",
            "alternative_supplier_qualification_weeks": 0,
            "risk_score": 10,
            "risk_flag": None,
            "mitigation": "Commodity item — no action required",
        },
        {
            "component_id": "IL-600",
            "component_name": "Inspection Labels & Packaging",
            "sourcing_type": "multi_source",
            "qualified_suppliers": ["SUP-A", "Local printers"],
            "geographic_risk": "low",
            "lead_time_risk": "low",
            "supplier_financial_health": "stable",
            "alternative_supplier_qualification_weeks": 1,
            "risk_score": 8,
            "risk_flag": None,
            "mitigation": "Commodity item — no action required",
        },
    ]
