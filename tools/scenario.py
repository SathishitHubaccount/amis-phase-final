"""
AMIS Scenario Test Data
========================
Pre-defined controlled datasets injected into agents for validation testing.

Each scenario defines:
  - description     : Human-readable summary of the factory state
  - tool_overrides  : Exact JSON each tool returns (bypasses real simulation)
  - expected_checks : What the agent MUST identify from this data

Two scenarios are provided:
  CRISIS  — Everything going wrong: stockout in 2 days, +72% demand spike,
             91.5% stockout probability, capacity exceeded, trend at +9.2%/week
  HEALTHY — All systems nominal: 57 days of supply, no anomalies,
             stable demand, 2.1% stockout probability
"""

# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO A: CRITICAL FACTORY STATE
# The agent must identify all five crisis signals from the injected data.
# ══════════════════════════════════════════════════════════════════════════════

CRISIS_SCENARIO = {
    "name": "CRITICAL FACTORY STATE",
    "description": (
        "All systems under stress: stockout in 2 days, "
        "+72% demand spike in 2026-W06 (severity HIGH), "
        "demand trend +9.2%/week, "
        "Monte Carlo stockout probability 91.5%, "
        "demand 1,750/week vs capacity ceiling 1,400/week."
    ),
    "injected_values_summary": [
        "current_stock: 380 units  |  days_of_supply: 2  (below safety_stock: 400)",
        "anomaly: SPIKE +72.3% in 2026-W06  |  severity: HIGH",
        "trend: Upward  |  growth_rate_pct_per_week: 9.2",
        "monte_carlo: stockout_probability_pct = 91.5",
        "capacity: demand 1,750/week  vs  max_daily_output 200 → 1,400/week",
    ],

    # ── Tool overrides: exact data the agent will receive ──────────────────
    "tool_overrides": {

        "get_demand_data_summary": {
            "product_info": {
                "product_id": "TEST-CRISIS",
                "product_name": "Industrial Valve Assembly - Type A",
                "unit_cost": 52.0,
                "unit_price": 89.5,
                "margin_pct": 41.9,
                "lead_time_days": 5,
                "shelf_life_days": None,
                "min_order_quantity": 100,
                "customer_segments": {
                    "industrial": {"share_pct": 55, "avg_order_size": 40},
                    "commercial": {"share_pct": 30, "avg_order_size": 18},
                    "retail":     {"share_pct": 15, "avg_order_size": 8},
                },
            },
            "historical_demand_last_12_weeks": [
                {"week": "2025-W48", "demand_units": 940,  "avg_price": 90.1,  "promotions_active": False, "competitor_price": 91.0},
                {"week": "2025-W49", "demand_units": 960,  "avg_price": 89.9,  "promotions_active": False, "competitor_price": 90.8},
                {"week": "2025-W50", "demand_units": 985,  "avg_price": 89.7,  "promotions_active": False, "competitor_price": 90.5},
                {"week": "2025-W51", "demand_units": 1010, "avg_price": 89.5,  "promotions_active": True,  "competitor_price": 90.2},
                {"week": "2025-W52", "demand_units": 1025, "avg_price": 89.3,  "promotions_active": False, "competitor_price": 90.0},
                {"week": "2026-W01", "demand_units": 1040, "avg_price": 89.1,  "promotions_active": False, "competitor_price": 89.9},
                {"week": "2026-W02", "demand_units": 1060, "avg_price": 89.0,  "promotions_active": False, "competitor_price": 89.7},
                {"week": "2026-W03", "demand_units": 1080, "avg_price": 89.0,  "promotions_active": False, "competitor_price": 89.5},
                {"week": "2026-W04", "demand_units": 1095, "avg_price": 88.9,  "promotions_active": False, "competitor_price": 89.3},
                {"week": "2026-W05", "demand_units": 1100, "avg_price": 88.8,  "promotions_active": False, "competitor_price": 89.2},
                {"week": "2026-W06", "demand_units": 1895, "avg_price": 88.5,  "promotions_active": False, "competitor_price": 89.0},
                {"week": "2026-W07", "demand_units": 1750, "avg_price": 88.4,  "promotions_active": False, "competitor_price": 88.9},
            ],
            "current_inventory": {
                "product_id": "TEST-CRISIS",
                "current_stock": 380,
                "safety_stock": 400,
                "warehouse_capacity": 5000,
                "warehouse_utilization_pct": 8,
                "avg_daily_consumption": 190,
                "days_of_supply": 2,
                "incoming_orders": [],
                "unit_holding_cost": 2.3,
                "unit_stockout_cost": 45.0,
            },
            "market_context": {
                "season": "Q1",
                "economic_indicator": "stable",
                "industry_trend": "growing at 4.2% YoY",
                "raw_material_price_trend": "up 6% last quarter",
                "competitor_activity": "Competitor X launched a new product line last week",
                "social_media_mentions": {
                    "count_last_7_days": 4820,
                    "sentiment": "78% positive",
                    "week_over_week_change_pct": 180,
                },
                "weather_forecast": "Normal conditions expected",
                "upcoming_events": [
                    {"event": "Q1 Procurement Summit", "date": "2026-03-10", "impact": "HIGH"},
                    {"event": "Industrial Trade Show", "date": "2026-03-22", "impact": "MEDIUM"},
                ],
            },
            "production_capacity": {
                "max_daily_output": 200,
                "current_utilization_pct": 95,
                "available_lines": ["Line-1", "Line-3"],
                "lines_under_maintenance": ["Line-2", "Line-4"],
                "overtime_available": True,
                "overtime_cost_premium_pct": 35,
                "contract_manufacturer_available": True,
                "contract_manufacturer_cost_premium_pct": 42,
            },
        },

        "detect_demand_anomalies": {
            "product_id": "TEST-CRISIS",
            "analysis_period": "2025-W48 to 2026-W07",
            "baseline_demand": 1035,
            "demand_std_dev": 278,
            "sensitivity_threshold": 1.5,
            "anomalies_found": 2,
            "anomalies": [
                {
                    "week": "2026-W06",
                    "date": "2026-02-02",
                    "demand": 1895,
                    "expected_demand": 1035,
                    "deviation_units": 860,
                    "deviation_pct": 72.3,
                    "z_score": 3.09,
                    "week_over_week_change_pct": 72.3,
                    "type": "SPIKE",
                    "severity": "HIGH",
                    "context": {
                        "had_promotion": False,
                        "price_that_week": 88.5,
                        "competitor_price": 89.0,
                    },
                },
                {
                    "week": "2026-W07",
                    "date": "2026-02-09",
                    "demand": 1750,
                    "expected_demand": 1035,
                    "deviation_units": 715,
                    "deviation_pct": 59.2,
                    "z_score": 2.57,
                    "week_over_week_change_pct": -7.6,
                    "type": "SPIKE",
                    "severity": "HIGH",
                    "context": {
                        "had_promotion": False,
                        "price_that_week": 88.4,
                        "competitor_price": 88.9,
                    },
                },
            ],
            "context_clues_for_diagnosis": {
                "social_media": {"count_last_7_days": 4820, "sentiment": "78% positive", "week_over_week_change_pct": 180},
                "competitor_activity": "Competitor X launched a new product line last week",
                "upcoming_events": [{"event": "Q1 Procurement Summit", "date": "2026-03-10", "impact": "HIGH"}],
                "economic_indicator": "stable",
            },
            "note": "The LLM should cross-reference anomalies with context clues to generate root cause hypotheses.",
        },

        "analyze_demand_trends": {
            "product_id": "TEST-CRISIS",
            "trend_analysis": {
                "direction": "Upward",
                "slope_units_per_week": 94.8,
                "growth_rate_pct_per_week": 9.2,
            },
            "demand_statistics": {
                "mean": 1035,
                "std_deviation": 278,
                "min": 940,
                "max": 1895,
                "coefficient_of_variation": 26.9,
            },
            "week_over_week_changes_pct": [2.1, 2.6, 2.5, 1.5, 1.5, 1.9, 1.9, 1.4, 0.5, 72.3, -7.6],
            "anomalies_detected": [
                {"week": "2026-W06", "demand": 1895, "deviation_from_avg": 860, "z_score": 3.09, "had_promotion": False},
                {"week": "2026-W07", "demand": 1750, "deviation_from_avg": 715, "z_score": 2.57, "had_promotion": False},
            ],
            "price_demand_correlation": {
                "correlation_coefficient": -0.18,
                "interpretation": "Weak/no correlation",
            },
            "market_context": {
                "season": "Q1",
                "economic_indicator": "stable",
                "industry_trend": "growing at 4.2% YoY",
                "raw_material_price_trend": "up 6% last quarter",
                "competitor_activity": "Competitor X launched a new product line last week",
            },
        },

        "simulate_demand_scenarios": {
            "product_id": "TEST-CRISIS",
            "forecast_horizon_weeks": 4,
            "historical_summary": {
                "weeks_analyzed": 12,
                "average_weekly_demand": 1035,
                "recent_4week_average": 1710,
                "trend": "Upward (+9.2%)",
                "volatility": "26.9%",
                "spike_detected": True,
                "spike_week_demand": 1895,
            },
            "scenarios": {
                "optimistic": {
                    "probability_weight": 0.20,
                    "description": "Sustained viral demand plus new enterprise contracts",
                    "weekly_forecast": [1960, 2050, 2110, 2200],
                    "total_units": 8320,
                    "assumptions": ["Viral momentum continues", "Trade show generates contracts"],
                },
                "base": {
                    "probability_weight": 0.55,
                    "description": "Demand stabilises near recent elevated levels",
                    "weekly_forecast": [1750, 1760, 1770, 1780],
                    "total_units": 7060,
                    "assumptions": ["Demand holds near recent spike level", "No major disruptions"],
                },
                "pessimistic": {
                    "probability_weight": 0.25,
                    "description": "Spike partially corrects but remains above historical average",
                    "weekly_forecast": [1420, 1380, 1350, 1310],
                    "total_units": 5460,
                    "assumptions": ["Spike was one-off event", "Competitor product captures share"],
                },
            },
            "confidence_interval_95pct": {
                "lower": 1280,
                "upper": 2250,
            },
            "expected_weighted_demand": 7009,
        },

        "compare_production_strategies": {
            "strategies": {
                "conservative": {
                    "production_quantity": 1190,
                    "description": "Produce 85% of recent demand. CAUTION: far below current demand level.",
                    "expected_profit": -8420.50,
                    "profit_std_dev": 12340.00,
                    "worst_case_5pct": -42100.00,
                    "best_case_95pct": 15300.00,
                    "stockout_probability_pct": 96.2,
                    "risk_adjusted_return": -0.682,
                },
                "balanced": {
                    "production_quantity": 1400,
                    "description": "Produce at maximum capacity (1,400 units/week — hard ceiling).",
                    "expected_profit": 12450.30,
                    "profit_std_dev": 9870.00,
                    "worst_case_5pct": -18500.00,
                    "best_case_95pct": 38200.00,
                    "stockout_probability_pct": 88.5,
                    "risk_adjusted_return": 1.261,
                },
                "aggressive": {
                    "production_quantity": 1400,
                    "description": "Cannot exceed 1,400/week — capacity ceiling is the binding constraint.",
                    "expected_profit": 12450.30,
                    "profit_std_dev": 9870.00,
                    "worst_case_5pct": -18500.00,
                    "best_case_95pct": 38200.00,
                    "stockout_probability_pct": 88.5,
                    "risk_adjusted_return": 1.261,
                },
            },
            "highest_expected_profit": "balanced",
            "best_risk_adjusted": "balanced",
            "expected_demand": 1750,
            "demand_uncertainty": 278.0,
            "note": "Production is capacity-constrained at 1,400 units/week. Demand of 1,750/week creates a 350-unit/week shortfall.",
        },

        "monte_carlo_profit_simulation": {
            "simulation_parameters": {
                "expected_demand": 1750,
                "production_quantity": 1400,
                "unit_price": 89.5,
                "unit_cost": 52.0,
                "simulations_run": 10000,
            },
            "profit_analysis": {
                "expected_profit": 12450.30,
                "profit_std_dev": 9870.00,
                "worst_case_5pct": -18500.00,
                "worst_case_10pct": -9200.00,
                "best_case_95pct": 38200.00,
                "min_profit": -52400.00,
                "max_profit": 52780.00,
            },
            "risk_metrics": {
                "stockout_probability_pct": 91.5,
                "overstock_probability_pct": 1.2,
                "profit_at_risk_5pct": 30950.30,
                "sharpe_ratio": 1.261,
            },
            "recommendation_data": {
                "break_even_demand": 813,
                "margin_per_unit": 37.5,
                "margin_pct": 41.9,
            },
        },
    },

    # ── What the agent MUST conclude from this data ────────────────────────
    "expected_checks": [
        {
            "id": "critical_inventory",
            "category": "Inventory Crisis",
            "description": "Agent identifies stock will run out in 2 days (380 units, 2 days of supply)",
            "search_terms": ["2 day", "2-day", "380", "days of supply", "stockout", "run out", "critical"],
            "match_mode": "any",
            "required": True,
        },
        {
            "id": "demand_spike_w06",
            "category": "Anomaly Detection",
            "description": "Agent identifies the +72% demand spike in week 2026-W06",
            "search_terms": ["72", "spike", "W06", "2026-W06", "anomal"],
            "match_mode": "any",
            "required": True,
        },
        {
            "id": "upward_trend",
            "category": "Trend Analysis",
            "description": "Agent identifies upward demand trend",
            "search_terms": ["upward", "increasing", "growing", "9.2", "growth"],
            "match_mode": "any",
            "required": True,
        },
        {
            "id": "stockout_probability",
            "category": "Risk Quantification",
            "description": "Agent reports ~91.5% stockout probability from Monte Carlo",
            "search_terms": ["91", "91.5", "stockout probab", "91%"],
            "match_mode": "any",
            "required": True,
        },
        {
            "id": "capacity_gap",
            "category": "Capacity Constraint",
            "description": "Agent identifies demand (1,750/week) exceeds production capacity (1,400/week)",
            "search_terms": ["1,400", "1400", "1,750", "1750", "capacity", "ceiling", "constraint"],
            "match_mode": "any",
            "required": True,
        },
        {
            "id": "escalation_urgency",
            "category": "Escalation / Urgency",
            "description": "Agent recommends immediate action / escalation",
            "search_terms": ["immediate", "urgent", "escalat", "critical", "emergency", "today", "now"],
            "match_mode": "any",
            "required": False,
        },
        {
            "id": "exact_spike_pct",
            "category": "Precision Check",
            "description": "Agent cites the exact +72.3% spike deviation",
            "search_terms": ["72.3"],
            "match_mode": "any",
            "required": False,
        },
    ],
}


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO B: HEALTHY FACTORY STATE
# The agent must correctly report a healthy status — no false alarms.
# ══════════════════════════════════════════════════════════════════════════════

HEALTHY_SCENARIO = {
    "name": "HEALTHY FACTORY STATE",
    "description": (
        "All systems nominal: 8,500 units in stock (57 days supply), "
        "no demand anomalies, stable trend +0.3%/week, "
        "Monte Carlo stockout probability 2.1%, "
        "demand 1,050/week comfortably within capacity."
    ),
    "injected_values_summary": [
        "current_stock: 8,500 units  |  days_of_supply: 57  (above safety_stock: 400)",
        "anomalies_found: 0  (no anomalies)",
        "trend: Stable  |  growth_rate_pct_per_week: 0.3",
        "monte_carlo: stockout_probability_pct = 2.1",
        "capacity: demand 1,050/week  vs  max_daily_output 220 → 1,540/week  (68% utilised)",
    ],

    "tool_overrides": {

        "get_demand_data_summary": {
            "product_info": {
                "product_id": "TEST-HEALTHY",
                "product_name": "Industrial Valve Assembly - Type A",
                "unit_cost": 52.0,
                "unit_price": 89.5,
                "margin_pct": 41.9,
                "lead_time_days": 5,
                "shelf_life_days": None,
                "min_order_quantity": 100,
                "customer_segments": {
                    "industrial": {"share_pct": 55, "avg_order_size": 40},
                    "commercial": {"share_pct": 30, "avg_order_size": 18},
                    "retail":     {"share_pct": 15, "avg_order_size": 8},
                },
            },
            "historical_demand_last_12_weeks": [
                {"week": "2025-W48", "demand_units": 1028, "avg_price": 89.5, "promotions_active": False, "competitor_price": 90.0},
                {"week": "2025-W49", "demand_units": 1035, "avg_price": 89.5, "promotions_active": False, "competitor_price": 90.0},
                {"week": "2025-W50", "demand_units": 1040, "avg_price": 89.4, "promotions_active": False, "competitor_price": 89.9},
                {"week": "2025-W51", "demand_units": 1042, "avg_price": 89.4, "promotions_active": True,  "competitor_price": 89.9},
                {"week": "2025-W52", "demand_units": 1038, "avg_price": 89.3, "promotions_active": False, "competitor_price": 89.8},
                {"week": "2026-W01", "demand_units": 1045, "avg_price": 89.3, "promotions_active": False, "competitor_price": 89.8},
                {"week": "2026-W02", "demand_units": 1050, "avg_price": 89.2, "promotions_active": False, "competitor_price": 89.7},
                {"week": "2026-W03", "demand_units": 1048, "avg_price": 89.2, "promotions_active": False, "competitor_price": 89.7},
                {"week": "2026-W04", "demand_units": 1052, "avg_price": 89.1, "promotions_active": False, "competitor_price": 89.6},
                {"week": "2026-W05", "demand_units": 1055, "avg_price": 89.1, "promotions_active": False, "competitor_price": 89.6},
                {"week": "2026-W06", "demand_units": 1049, "avg_price": 89.0, "promotions_active": False, "competitor_price": 89.5},
                {"week": "2026-W07", "demand_units": 1053, "avg_price": 89.0, "promotions_active": False, "competitor_price": 89.5},
            ],
            "current_inventory": {
                "product_id": "TEST-HEALTHY",
                "current_stock": 8500,
                "safety_stock": 400,
                "warehouse_capacity": 10000,
                "warehouse_utilization_pct": 85,
                "avg_daily_consumption": 150,
                "days_of_supply": 57,
                "incoming_orders": [
                    {"supplier": "SUP-A", "quantity": 1000, "expected_date": "2026-02-28"},
                ],
                "unit_holding_cost": 2.3,
                "unit_stockout_cost": 45.0,
            },
            "market_context": {
                "season": "Q1",
                "economic_indicator": "stable",
                "industry_trend": "growing at 4.2% YoY",
                "raw_material_price_trend": "stable",
                "competitor_activity": "No significant competitor activity",
                "social_media_mentions": {
                    "count_last_7_days": 210,
                    "sentiment": "72% positive",
                    "week_over_week_change_pct": 3,
                },
                "weather_forecast": "Normal conditions expected",
                "upcoming_events": [],
            },
            "production_capacity": {
                "max_daily_output": 220,
                "current_utilization_pct": 68,
                "available_lines": ["Line-1", "Line-2", "Line-3", "Line-4"],
                "lines_under_maintenance": [],
                "overtime_available": True,
                "overtime_cost_premium_pct": 35,
                "contract_manufacturer_available": True,
                "contract_manufacturer_cost_premium_pct": 42,
            },
        },

        "detect_demand_anomalies": {
            "product_id": "TEST-HEALTHY",
            "analysis_period": "2025-W48 to 2026-W07",
            "baseline_demand": 1045,
            "demand_std_dev": 8,
            "sensitivity_threshold": 1.5,
            "anomalies_found": 0,
            "anomalies": [],
            "context_clues_for_diagnosis": {
                "social_media": {"count_last_7_days": 210, "sentiment": "72% positive", "week_over_week_change_pct": 3},
                "competitor_activity": "No significant competitor activity",
                "upcoming_events": [],
                "economic_indicator": "stable",
            },
            "note": "No anomalies detected. Demand is behaving within normal statistical bounds.",
        },

        "analyze_demand_trends": {
            "product_id": "TEST-HEALTHY",
            "trend_analysis": {
                "direction": "Stable",
                "slope_units_per_week": 3.1,
                "growth_rate_pct_per_week": 0.3,
            },
            "demand_statistics": {
                "mean": 1045,
                "std_deviation": 8,
                "min": 1028,
                "max": 1055,
                "coefficient_of_variation": 0.8,
            },
            "week_over_week_changes_pct": [0.7, 0.5, 0.2, -0.4, 0.7, 0.5, -0.2, 0.4, 0.3, -0.6, 0.4],
            "anomalies_detected": [],
            "price_demand_correlation": {
                "correlation_coefficient": -0.08,
                "interpretation": "Weak/no correlation",
            },
            "market_context": {
                "season": "Q1",
                "economic_indicator": "stable",
                "industry_trend": "growing at 4.2% YoY",
                "raw_material_price_trend": "stable",
                "competitor_activity": "No significant competitor activity",
            },
        },

        "simulate_demand_scenarios": {
            "product_id": "TEST-HEALTHY",
            "forecast_horizon_weeks": 4,
            "historical_summary": {
                "weeks_analyzed": 12,
                "average_weekly_demand": 1045,
                "recent_4week_average": 1052,
                "trend": "Stable (+0.3%)",
                "volatility": "0.8%",
                "spike_detected": False,
                "spike_week_demand": None,
            },
            "scenarios": {
                "optimistic": {
                    "probability_weight": 0.20,
                    "description": "Modest upside from seasonal lift and trade show",
                    "weekly_forecast": [1080, 1090, 1100, 1110],
                    "total_units": 4380,
                    "assumptions": ["Minor seasonal uplift", "Trade show converts some leads"],
                },
                "base": {
                    "probability_weight": 0.55,
                    "description": "Demand continues stable at current levels",
                    "weekly_forecast": [1053, 1055, 1057, 1059],
                    "total_units": 4224,
                    "assumptions": ["Stable market conditions", "No disruptions"],
                },
                "pessimistic": {
                    "probability_weight": 0.25,
                    "description": "Minor softening due to raw material price pass-through",
                    "weekly_forecast": [1020, 1015, 1010, 1005],
                    "total_units": 4050,
                    "assumptions": ["Price increases reduce orders slightly"],
                },
            },
            "confidence_interval_95pct": {
                "lower": 1005,
                "upper": 1115,
            },
            "expected_weighted_demand": 4238,
        },

        "compare_production_strategies": {
            "strategies": {
                "conservative": {
                    "production_quantity": 893,
                    "description": "Produce 85% of expected demand. Low risk given high stock buffer.",
                    "expected_profit": 31850.00,
                    "profit_std_dev": 1240.00,
                    "worst_case_5pct": 29200.00,
                    "best_case_95pct": 34400.00,
                    "stockout_probability_pct": 0.0,
                    "risk_adjusted_return": 25.7,
                },
                "balanced": {
                    "production_quantity": 1050,
                    "description": "Produce 100% of expected demand. Optimal.",
                    "expected_profit": 39250.00,
                    "profit_std_dev": 1380.00,
                    "worst_case_5pct": 36400.00,
                    "best_case_95pct": 41900.00,
                    "stockout_probability_pct": 2.1,
                    "risk_adjusted_return": 28.4,
                },
                "aggressive": {
                    "production_quantity": 1207,
                    "description": "Produce 115% of expected demand. Slight overstock risk.",
                    "expected_profit": 37100.00,
                    "profit_std_dev": 2100.00,
                    "worst_case_5pct": 33100.00,
                    "best_case_95pct": 41200.00,
                    "stockout_probability_pct": 0.1,
                    "risk_adjusted_return": 17.7,
                },
            },
            "highest_expected_profit": "balanced",
            "best_risk_adjusted": "balanced",
            "expected_demand": 1050,
            "demand_uncertainty": 8.0,
        },

        "monte_carlo_profit_simulation": {
            "simulation_parameters": {
                "expected_demand": 1050,
                "production_quantity": 1050,
                "unit_price": 89.5,
                "unit_cost": 52.0,
                "simulations_run": 10000,
            },
            "profit_analysis": {
                "expected_profit": 39250.00,
                "profit_std_dev": 1380.00,
                "worst_case_5pct": 36400.00,
                "worst_case_10pct": 37200.00,
                "best_case_95pct": 41900.00,
                "min_profit": 33800.00,
                "max_profit": 43200.00,
            },
            "risk_metrics": {
                "stockout_probability_pct": 2.1,
                "overstock_probability_pct": 1.9,
                "profit_at_risk_5pct": 2850.00,
                "sharpe_ratio": 28.44,
            },
            "recommendation_data": {
                "break_even_demand": 610,
                "margin_per_unit": 37.5,
                "margin_pct": 41.9,
            },
        },
    },

    # ── What the agent MUST conclude from this data ────────────────────────
    "expected_checks": [
        {
            "id": "healthy_inventory",
            "category": "Inventory Status",
            "description": "Agent identifies high inventory (8,500 units / 57 days of supply)",
            "search_terms": ["8,500", "8500", "57 day", "57-day", "adequate", "healthy", "sufficient"],
            "match_mode": "any",
            "required": True,
        },
        {
            "id": "no_anomalies",
            "category": "Anomaly Detection",
            "description": "Agent correctly reports no demand anomalies",
            "search_terms": ["no anomal", "zero anomal", "no unusual", "normal demand", "no spike",
                             "zero", "0 anomal", "anomalies: 0", "anomalies detected: 0"],
            "match_mode": "any",
            "required": True,
        },
        {
            "id": "stable_trend",
            "category": "Trend Analysis",
            "description": "Agent identifies stable demand trend (not upward/critical)",
            "search_terms": ["stable", "steady", "consistent", "0.3", "flat"],
            "match_mode": "any",
            "required": True,
        },
        {
            "id": "low_stockout_risk",
            "category": "Risk Assessment",
            "description": "Agent reports low stockout probability (~2.1%)",
            "search_terms": ["2.1", "2%", "low risk", "minimal risk", "low stockout"],
            "match_mode": "any",
            "required": True,
        },
        {
            "id": "capacity_ok",
            "category": "Capacity",
            "description": "Agent confirms production capacity is sufficient for demand",
            "search_terms": ["sufficient capacity", "capacity available", "within capacity", "no capacity", "1,540", "1540", "68%"],
            "match_mode": "any",
            "required": False,
        },
        {
            "id": "no_escalation",
            "category": "Non-escalation Check",
            "description": "Agent does NOT recommend emergency action (healthy state)",
            "search_terms": ["immediate action required", "emergency", "critical alert", "escalat"],
            "match_mode": "none",   # MUST NOT contain these terms
            "required": True,
        },
        {
            "id": "balanced_strategy",
            "category": "Strategy Recommendation",
            "description": "Agent recommends balanced production strategy",
            "search_terms": ["balanced", "balance"],
            "match_mode": "any",
            "required": False,
        },
    ],
}


# ── Lookup ──────────────────────────────────────────────────────────────────

SCENARIOS = {
    "crisis":  CRISIS_SCENARIO,
    "healthy": HEALTHY_SCENARIO,
}
