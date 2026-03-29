-- AMIS Database Schema
-- SQLite database for Autonomous Manufacturing Intelligence System

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory table
CREATE TABLE IF NOT EXISTS inventory (
    product_id TEXT PRIMARY KEY,
    current_stock INTEGER NOT NULL,
    safety_stock INTEGER,
    reorder_point INTEGER,
    avg_daily_usage REAL,
    lead_time INTEGER,
    stockout_risk REAL,
    warehouse_location TEXT,
    bin_location TEXT,
    last_replenishment_date DATE,
    last_stockout_date DATE,
    unit_cost REAL,
    holding_cost REAL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Machines table
CREATE TABLE IF NOT EXISTS machines (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT,
    line TEXT,
    status TEXT,
    oee REAL,
    availability REAL,
    performance REAL,
    quality REAL,
    failure_risk REAL,
    production_capacity INTEGER,
    current_utilization REAL,
    vibration_level REAL,
    temperature REAL,
    power_consumption REAL,
    runtime_hours REAL,
    cycle_count INTEGER,
    last_maintenance DATE,
    next_maintenance DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product-Machine mapping (many-to-many relationship)
CREATE TABLE IF NOT EXISTS product_machines (
    product_id TEXT,
    machine_id TEXT,
    PRIMARY KEY (product_id, machine_id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

-- Machine alarms
CREATE TABLE IF NOT EXISTS machine_alarms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT NOT NULL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    severity TEXT,
    message TEXT,
    acknowledged INTEGER DEFAULT 0,
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

-- Spare parts inventory
CREATE TABLE IF NOT EXISTS spare_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT NOT NULL,
    part_name TEXT NOT NULL,
    stock INTEGER DEFAULT 0,
    min_stock INTEGER DEFAULT 0,
    status TEXT,
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

-- Maintenance history
CREATE TABLE IF NOT EXISTS maintenance_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT NOT NULL,
    date DATE NOT NULL,
    type TEXT,
    technician TEXT,
    duration TEXT,
    notes TEXT,
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

-- Work orders
CREATE TABLE IF NOT EXISTS work_orders (
    id TEXT PRIMARY KEY,
    machine_id TEXT NOT NULL,
    type TEXT NOT NULL,
    priority TEXT NOT NULL,
    assigned_to TEXT,
    scheduled_date DATE,
    estimated_duration REAL,
    description TEXT,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT DEFAULT 'System User',
    completed_at TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

-- Suppliers
CREATE TABLE IF NOT EXISTS suppliers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT,
    score INTEGER,
    rating TEXT,
    on_time_delivery REAL,
    quality_score REAL,
    cost_index INTEGER,
    base_cost REAL,
    lead_time INTEGER,
    lead_time_variability INTEGER,
    risk TEXT,
    moq INTEGER,
    payment_terms TEXT,
    currency TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Supplier certifications
CREATE TABLE IF NOT EXISTS supplier_certifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id TEXT NOT NULL,
    certification TEXT NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- Supplier contracts
CREATE TABLE IF NOT EXISTS supplier_contracts (
    id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    volume INTEGER,
    status TEXT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- Supplier incidents
CREATE TABLE IF NOT EXISTS supplier_incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id TEXT NOT NULL,
    date DATE NOT NULL,
    type TEXT,
    severity TEXT,
    resolution TEXT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- BOM (Bill of Materials) items
CREATE TABLE IF NOT EXISTS bom_items (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    component_id TEXT NOT NULL,
    component_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    stock INTEGER DEFAULT 0,
    supplier_id TEXT,
    cost REAL,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- Activity log for audit trail
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user TEXT NOT NULL,
    action TEXT NOT NULL,
    details TEXT
);

-- Demand forecast data (AI-generated forecasts)
CREATE TABLE IF NOT EXISTS demand_forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    week_number INTEGER,
    forecast_date DATE,
    optimistic INTEGER,
    base_case INTEGER,
    pessimistic INTEGER,
    actual INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Historical demand data (actual past demand used as input for AI)
CREATE TABLE IF NOT EXISTS historical_demand_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    week_start_date DATE NOT NULL,
    week_number INTEGER NOT NULL,
    year INTEGER NOT NULL,
    demand_units INTEGER NOT NULL,
    avg_price REAL,
    promotions_active BOOLEAN DEFAULT 0,
    competitor_price REAL,
    is_anomaly BOOLEAN DEFAULT 0,
    anomaly_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    UNIQUE(product_id, week_start_date)
);

-- Market context data (macroeconomic and market conditions)
CREATE TABLE IF NOT EXISTS market_context_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_recorded DATE NOT NULL UNIQUE,
    industry_growth_rate REAL,
    economic_indicator TEXT,
    competitor_activity TEXT,
    raw_material_price_trend TEXT,
    trade_show_date DATE,
    major_client_contract_renewal_date DATE,
    seasonal_pattern TEXT,
    market_sentiment TEXT,
    supply_chain_status TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Warehouse zones (for warehouse details)
CREATE TABLE IF NOT EXISTS warehouse_zones (
    zone_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    current_units INTEGER NOT NULL,
    utilization REAL,
    zone_type TEXT,
    temperature_controlled BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Stockout events (for historical stockout tracking)
CREATE TABLE IF NOT EXISTS stockout_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    event_date DATE NOT NULL,
    duration_days INTEGER,
    units_short INTEGER,
    root_cause TEXT,
    revenue_lost REAL,
    customers_affected INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Purchase orders (for reorder history and open purchase orders)
CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    supplier_id TEXT NOT NULL,
    order_date DATE NOT NULL,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    quantity INTEGER NOT NULL,
    unit_cost REAL,
    total_cost REAL,
    status TEXT DEFAULT 'open',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- Shift configuration (for production shift details)
CREATE TABLE IF NOT EXISTS shift_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shifts_per_day INTEGER NOT NULL,
    hours_per_shift REAL NOT NULL,
    days_per_week INTEGER NOT NULL,
    overtime_available BOOLEAN DEFAULT 1,
    max_overtime_hours REAL,
    shift_names TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sensor readings (for machine sensor data)
CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    sensor_type TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT,
    baseline REAL,
    threshold_high REAL,
    threshold_critical REAL,
    status TEXT,
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

-- Supplier risk factors (for supply chain risk analysis)
CREATE TABLE IF NOT EXISTS supplier_risk (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id TEXT NOT NULL,
    component_name TEXT NOT NULL,
    sourcing_type TEXT,
    qualified_suppliers INTEGER,
    geographic_risk TEXT,
    lead_time_risk TEXT,
    risk_score REAL,
    mitigation_strategy TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Production lines
CREATE TABLE IF NOT EXISTS production_lines (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    current_product_id TEXT,
    capacity_per_hour INTEGER,
    status TEXT DEFAULT 'running',
    utilization REAL DEFAULT 0,
    bottleneck_machine_id TEXT,
    efficiency REAL,
    scrap_rate REAL,
    changeover_time REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (current_product_id) REFERENCES products(id),
    FOREIGN KEY (bottleneck_machine_id) REFERENCES machines(id)
);

-- Production schedule (weekly planning)
CREATE TABLE IF NOT EXISTS production_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    week_number INTEGER NOT NULL,
    week_start_date DATE NOT NULL,
    demand INTEGER,
    planned_production INTEGER,
    actual_production INTEGER,
    capacity INTEGER,
    gap INTEGER,
    overtime_hours REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Inventory history (for trend charts)
CREATE TABLE IF NOT EXISTS inventory_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    date DATE NOT NULL,
    stock_level INTEGER NOT NULL,
    stockout_risk REAL,
    days_supply REAL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Machine OEE history (for trend charts)
CREATE TABLE IF NOT EXISTS machine_oee_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT NOT NULL,
    date DATE NOT NULL,
    oee REAL,
    availability REAL,
    performance REAL,
    quality REAL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_work_orders_machine ON work_orders(machine_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_status ON work_orders(status);
CREATE INDEX IF NOT EXISTS idx_machine_alarms_machine ON machine_alarms(machine_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_timestamp ON activity_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_bom_items_product ON bom_items(product_id);
CREATE INDEX IF NOT EXISTS idx_production_schedule_product ON production_schedule(product_id);
CREATE INDEX IF NOT EXISTS idx_production_schedule_week ON production_schedule(week_number);
CREATE INDEX IF NOT EXISTS idx_inventory_history_product ON inventory_history(product_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_machine_oee_history_machine ON machine_oee_history(machine_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_historical_demand_product ON historical_demand_data(product_id, week_start_date DESC);
CREATE INDEX IF NOT EXISTS idx_historical_demand_date ON historical_demand_data(week_start_date DESC);
CREATE INDEX IF NOT EXISTS idx_market_context_date ON market_context_data(date_recorded DESC);
CREATE INDEX IF NOT EXISTS idx_warehouse_zones_product ON warehouse_zones(product_id);
CREATE INDEX IF NOT EXISTS idx_stockout_events_product ON stockout_events(product_id, event_date DESC);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_product ON purchase_orders(product_id);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_supplier ON purchase_orders(supplier_id);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_status ON purchase_orders(status);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_machine ON sensor_readings(machine_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_supplier_risk_component ON supplier_risk(component_id);
