from tools.forecasting import simulate_demand_scenarios, analyze_demand_trends, get_demand_data_summary
from tools.simulation import monte_carlo_profit_simulation, compare_production_strategies
from tools.anomaly import detect_demand_anomalies
from tools.inventory import (
    get_inventory_status,
    calculate_reorder_point,
    optimize_safety_stock,
    simulate_stockout_risk,
    evaluate_holding_costs,
    generate_replenishment_plan,
)
from tools.machine_health import (
    get_machine_fleet_status,
    analyze_sensor_readings,
    predict_failure_risk,
    calculate_oee,
    generate_maintenance_schedule,
    assess_production_capacity_impact,
)
from tools.production import (
    get_production_context,
    build_master_production_schedule,
    analyze_production_bottlenecks,
    evaluate_capacity_gap,
    optimize_production_mix,
    generate_production_requirements,
)
from tools.supplier import (
    get_procurement_context,
    evaluate_supplier_options,
    generate_purchase_orders,
    assess_supply_chain_risk,
    simulate_delivery_risk,
    optimize_supplier_allocation,
)
from tools.orchestrator import (
    get_demand_intelligence,
    get_inventory_intelligence,
    get_machine_health_intelligence,
    get_production_intelligence,
    get_supplier_intelligence,
    synthesize_manufacturing_report,
)

DEMAND_TOOLS = [
    get_demand_data_summary,
    simulate_demand_scenarios,
    analyze_demand_trends,
    monte_carlo_profit_simulation,
    compare_production_strategies,
    detect_demand_anomalies,
]

INVENTORY_TOOLS = [
    get_inventory_status,
    calculate_reorder_point,
    optimize_safety_stock,
    simulate_stockout_risk,
    evaluate_holding_costs,
    generate_replenishment_plan,
]

MACHINE_HEALTH_TOOLS = [
    get_machine_fleet_status,
    analyze_sensor_readings,
    predict_failure_risk,
    calculate_oee,
    generate_maintenance_schedule,
    assess_production_capacity_impact,
]

PRODUCTION_TOOLS = [
    get_production_context,
    build_master_production_schedule,
    analyze_production_bottlenecks,
    evaluate_capacity_gap,
    optimize_production_mix,
    generate_production_requirements,
]

SUPPLIER_TOOLS = [
    get_procurement_context,
    evaluate_supplier_options,
    generate_purchase_orders,
    assess_supply_chain_risk,
    simulate_delivery_risk,
    optimize_supplier_allocation,
]

ORCHESTRATOR_TOOLS = [
    get_demand_intelligence,
    get_inventory_intelligence,
    get_machine_health_intelligence,
    get_production_intelligence,
    get_supplier_intelligence,
    synthesize_manufacturing_report,
]

# Backward compatibility
ALL_TOOLS = DEMAND_TOOLS
