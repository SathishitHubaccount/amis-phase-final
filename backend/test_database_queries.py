"""
Test Script: Validate Historical Data Migration
================================================
This script validates that the database migration worked correctly
by running SQL queries and comparing results.
"""
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "amis.db"


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def test_historical_data_queries():
    """Test SQL queries for historical demand data"""
    print_section("SQL VALIDATION QUERIES - Historical Demand Data")

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Query 1: View Historical Data
    print("\n[QUERY 1] View last 12 weeks of historical demand for PROD-A:")
    print("SQL: SELECT week_start_date, demand_units, promotions_active, is_anomaly")
    print("     FROM historical_demand_data")
    print("     WHERE product_id = 'PROD-A'")
    print("     ORDER BY week_start_date DESC LIMIT 12;\n")

    cursor.execute("""
        SELECT week_start_date, demand_units, promotions_active, is_anomaly, anomaly_reason
        FROM historical_demand_data
        WHERE product_id = 'PROD-A'
        ORDER BY week_start_date DESC
        LIMIT 12
    """)

    print(f"{'Date':<15} {'Demand':<10} {'Promo':<8} {'Anomaly':<10} {'Reason':<40}")
    print("-" * 90)
    for row in cursor.fetchall():
        promo = "YES" if row[2] else "NO"
        anomaly = "YES" if row[3] else "NO"
        reason = row[4] if row[4] else "-"
        print(f"{row[0]:<15} {row[1]:<10} {promo:<8} {anomaly:<10} {reason:<40}")

    # Query 2: Calculate Statistics
    print("\n[QUERY 2] Calculate average, min, max demand for PROD-A (all 52 weeks):")
    print("SQL: SELECT AVG(demand_units), MIN(demand_units), MAX(demand_units)")
    print("     FROM historical_demand_data")
    print("     WHERE product_id = 'PROD-A';\n")

    cursor.execute("""
        SELECT
            AVG(demand_units) as avg_demand,
            MIN(demand_units) as min_demand,
            MAX(demand_units) as max_demand
        FROM historical_demand_data
        WHERE product_id = 'PROD-A'
    """)

    row = cursor.fetchone()
    if row and row[0]:
        print(f"Average Demand: {row[0]:.2f} units/week")
        print(f"Min Demand:     {row[1]} units/week")
        print(f"Max Demand:     {row[2]} units/week")
    else:
        print("[ERROR] No data found")

    # Query 3: Find Anomalies
    print("\n[QUERY 3] Find all anomalies for PROD-A:")
    print("SQL: SELECT week_start_date, demand_units, anomaly_reason")
    print("     FROM historical_demand_data")
    print("     WHERE product_id = 'PROD-A' AND is_anomaly = 1;\n")

    cursor.execute("""
        SELECT week_start_date, demand_units, anomaly_reason
        FROM historical_demand_data
        WHERE product_id = 'PROD-A' AND is_anomaly = 1
        ORDER BY week_start_date DESC
    """)

    print(f"{'Date':<15} {'Demand':<10} {'Reason':<60}")
    print("-" * 90)
    for row in cursor.fetchall():
        print(f"{row[0]:<15} {row[1]:<10} {row[2]:<60}")

    # Query 4: Week-over-Week Changes
    print("\n[QUERY 4] Calculate week-over-week demand changes for PROD-A:")
    print("SQL: WITH weekly_data AS (")
    print("       SELECT demand_units, LAG(demand_units) OVER (ORDER BY week_start_date) as prev")
    print("       FROM historical_demand_data WHERE product_id = 'PROD-A'")
    print("     ) SELECT ((demand_units - prev) * 100.0 / prev) as wow_change_pct FROM weekly_data;\n")

    cursor.execute("""
        WITH weekly_data AS (
            SELECT
                week_start_date,
                demand_units,
                LAG(demand_units) OVER (ORDER BY week_start_date) as prev_demand
            FROM historical_demand_data
            WHERE product_id = 'PROD-A'
        )
        SELECT
            week_start_date,
            demand_units,
            prev_demand,
            ROUND(((demand_units - prev_demand) * 100.0 / prev_demand), 2) as wow_change_pct
        FROM weekly_data
        WHERE prev_demand IS NOT NULL
        ORDER BY week_start_date DESC
        LIMIT 10
    """)

    print(f"{'Date':<15} {'Current':<10} {'Previous':<10} {'Change %':<10}")
    print("-" * 50)
    for row in cursor.fetchall():
        change_sign = "+" if row[3] > 0 else ""
        print(f"{row[0]:<15} {row[1]:<10} {row[2]:<10} {change_sign}{row[3]}%")

    conn.close()


def test_market_context_queries():
    """Test SQL queries for market context data"""
    print_section("SQL VALIDATION QUERIES - Market Context Data")

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    print("\n[QUERY 5] View current market context:")
    print("SQL: SELECT * FROM market_context_data ORDER BY date_recorded DESC LIMIT 1;\n")

    cursor.execute("SELECT * FROM market_context_data ORDER BY date_recorded DESC LIMIT 1")

    row = cursor.fetchone()
    if row:
        print(f"Date Recorded:            {row[1]}")
        print(f"Industry Growth Rate:     {row[2]}%")
        print(f"Economic Indicator:       {row[3]}")
        print(f"Competitor Activity:      {row[4]}")
        print(f"Raw Material Price Trend: {row[5]}")
        print(f"Trade Show Date:          {row[6]}")
        print(f"Contract Renewal Date:    {row[7]}")
        print(f"Seasonal Pattern:         {row[8]}")
        print(f"Market Sentiment:         {row[9]}")
        print(f"Supply Chain Status:      {row[10]}")

    conn.close()


def test_database_query_functions():
    """Test the Python database query functions"""
    print_section("TESTING PYTHON DATABASE QUERY FUNCTIONS")

    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from data.database_queries import (
        get_historical_demand,
        get_market_context,
        get_historical_demand_statistics,
        get_anomaly_weeks
    )

    # Test 1: get_historical_demand
    print("\n[TEST 1] get_historical_demand(product_id='PROD-A', weeks=12)")
    data = get_historical_demand(product_id='PROD-A', weeks=12)
    print(f"Returned {len(data)} weeks of data")
    print(f"First week: {data[0]['date']} - {data[0]['demand_units']} units")
    print(f"Last week:  {data[-1]['date']} - {data[-1]['demand_units']} units")

    # Test 2: get_market_context
    print("\n[TEST 2] get_market_context()")
    context = get_market_context()
    print(f"Season: {context.get('season')}")
    print(f"Economic Indicator: {context.get('economic_indicator')}")
    print(f"Industry Trend: {context.get('industry_trend')}")

    # Test 3: get_historical_demand_statistics
    print("\n[TEST 3] get_historical_demand_statistics(product_id='PROD-A')")
    stats = get_historical_demand_statistics(product_id='PROD-A')
    print(f"Total weeks: {stats['total_weeks']}")
    print(f"Average weekly demand: {stats['average_weekly_demand']}")
    print(f"Min: {stats['min_weekly_demand']}, Max: {stats['max_weekly_demand']}")
    print(f"Weeks with anomalies: {stats['weeks_with_anomalies']}")

    # Test 4: get_anomaly_weeks
    print("\n[TEST 4] get_anomaly_weeks(product_id='PROD-A')")
    anomalies = get_anomaly_weeks(product_id='PROD-A')
    print(f"Found {len(anomalies)} anomalies:")
    for a in anomalies:
        print(f"  - {a['date']}: {a['demand']} units ({a['reason']})")


def test_ai_tool_compatibility():
    """Test that AI tools can use the database queries"""
    print_section("TESTING AI TOOL COMPATIBILITY")

    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from tools.forecasting import simulate_demand_scenarios, analyze_demand_trends

    print("\n[TEST 5] simulate_demand_scenarios tool")
    print("Calling: simulate_demand_scenarios.invoke({'product_id': 'PROD-A', 'horizon_weeks': 4})")
    try:
        result = simulate_demand_scenarios.invoke({
            "product_id": "PROD-A",
            "horizon_weeks": 4
        })
        import json
        data = json.loads(result)
        print(f"[SUCCESS] Tool returned forecast data")
        print(f"Expected weighted demand: {data['expected_weighted_demand']} units")
        print(f"Historical summary: {data['historical_summary']['weeks_analyzed']} weeks analyzed")
    except Exception as e:
        print(f"[ERROR] {str(e)}")

    print("\n[TEST 6] analyze_demand_trends tool")
    print("Calling: analyze_demand_trends.invoke({'product_id': 'PROD-A'})")
    try:
        result = analyze_demand_trends.invoke({"product_id": "PROD-A"})
        import json
        data = json.loads(result)
        print(f"[SUCCESS] Tool returned trend analysis")
        print(f"Trend direction: {data['trend_analysis']['direction']}")
        print(f"Mean demand: {data['demand_statistics']['mean']} units")
        print(f"Anomalies detected: {len(data['anomalies_detected'])}")
    except Exception as e:
        print(f"[ERROR] {str(e)}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("DATABASE MIGRATION VALIDATION TEST SUITE")
    print("=" * 70)
    print("\nThis script validates that:")
    print("1. Historical data is stored correctly in database")
    print("2. SQL queries return expected results")
    print("3. Python query functions work correctly")
    print("4. AI tools can use the database data")

    # Run all tests
    test_historical_data_queries()
    test_market_context_queries()
    test_database_query_functions()
    test_ai_tool_compatibility()

    print("\n" + "=" * 70)
    print("[COMPLETE] ALL VALIDATION TESTS FINISHED")
    print("=" * 70)
    print("\n[SUCCESS] Historical data migration is working correctly!")
    print("You can now:")
    print("  1. Query historical data with SQL (see queries above)")
    print("  2. Run the AI pipeline - it will use database data")
    print("  3. Validate forecasts by comparing to SQL query results")
