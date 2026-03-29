# AMIS Data Sources: Database vs Python Functions

## Summary

| Category | Database Tables | Python Functions (sample_data.py) |
|----------|----------------|-----------------------------------|
| **Total** | **21 tables** | **20 functions** |
| **Actively Used** | **2 tables** | **20 functions** |
| **Populated** | **2 tables** | **All functions** |

---

## Database Tables (21 Total)

### ✅ ACTIVELY USED & POPULATED (2 tables)

These tables have data and are actively queried by the AI agents:

1. **`historical_demand_data`** (156 records)
   - Purpose: 52 weeks of historical demand for 3 products
   - Used by: Demand Forecasting Agent (Tool 1, 2, 3)
   - Populated by: `migrate_historical_data.py`
   - Status: ✅ MIGRATED - Now queries database instead of Python

2. **`market_context_data`** (1 record)
   - Purpose: Current market conditions and economic indicators
   - Used by: Demand Forecasting Agent (Tool 1)
   - Populated by: `migrate_historical_data.py`
   - Status: ✅ MIGRATED - Now queries database instead of Python

### ⚠️ DEFINED BUT NOT ACTIVELY USED (19 tables)

These tables exist in schema.sql but the AI agents don't actively query them. Data comes from Python functions instead.

#### Product & Inventory Tables

3. **`products`**
   - Purpose: Product catalog (id, name, description, category, price, cost)
   - Current source: Python function `get_product_info()`
   - Status: ⚠️ Table exists, not actively used

4. **`inventory`**
   - Purpose: Current inventory levels (stock, safety stock, reorder point)
   - Current source: Python function `get_current_inventory()`
   - Status: ⚠️ Table exists, not actively used

5. **`inventory_history`**
   - Purpose: Daily inventory snapshots over time
   - Current source: No Python equivalent (not tracked)
   - Status: ⚠️ Table exists, empty

#### Machine & Production Tables

6. **`machines`**
   - Purpose: Machine fleet (id, name, type, status, OEE, capacity)
   - Current source: Python function `get_machine_fleet()`
   - Status: ⚠️ Table exists, not actively used

7. **`product_machines`**
   - Purpose: Product-machine mapping (many-to-many)
   - Current source: No Python equivalent
   - Status: ⚠️ Table exists, empty

8. **`machine_alarms`**
   - Purpose: Machine alarm events (severity, message, timestamp)
   - Current source: Embedded in `get_sensor_readings()`
   - Status: ⚠️ Table exists, not actively used

9. **`spare_parts`**
   - Purpose: Spare parts inventory for machines
   - Current source: No Python equivalent
   - Status: ⚠️ Table exists, empty

10. **`maintenance_history`**
    - Purpose: Historical maintenance events
    - Current source: Python function `get_maintenance_history()`
    - Status: ⚠️ Table exists, not actively used

11. **`work_orders`**
    - Purpose: Maintenance work orders
    - Current source: No Python equivalent
    - Status: ⚠️ Table exists, empty

12. **`production_lines`**
    - Purpose: Production line definitions
    - Current source: Python function `get_production_lines()`
    - Status: ⚠️ Table exists, not actively used

13. **`production_schedule`**
    - Purpose: Scheduled production runs
    - Current source: No Python equivalent
    - Status: ⚠️ Table exists, empty

14. **`machine_oee_history`**
    - Purpose: Historical OEE (Overall Equipment Effectiveness)
    - Current source: Python function `get_oee_history()`
    - Status: ⚠️ Table exists, not actively used

#### Supplier Tables

15. **`suppliers`**
    - Purpose: Supplier information
    - Current source: Python function `get_supplier_performance()`
    - Status: ⚠️ Table exists, not actively used

16. **`supplier_certifications`**
    - Purpose: Supplier certifications and compliance
    - Current source: No Python equivalent
    - Status: ⚠️ Table exists, empty

17. **`supplier_contracts`**
    - Purpose: Supplier contract terms
    - Current source: Python function `get_supplier_contracts()`
    - Status: ⚠️ Table exists, not actively used

18. **`supplier_incidents`**
    - Purpose: Supplier quality incidents
    - Current source: No Python equivalent
    - Status: ⚠️ Table exists, empty

#### Other Tables

19. **`bom_items`**
    - Purpose: Bill of Materials (components per product)
    - Current source: Python function `get_bill_of_materials()`
    - Status: ⚠️ Table exists, not actively used

20. **`activity_log`**
    - Purpose: System activity logging
    - Current source: No Python equivalent
    - Status: ⚠️ Table exists, may have some records

21. **`demand_forecasts`**
    - Purpose: AI-generated demand forecasts (OUTPUT)
    - Current source: Written by Demand Forecasting Agent
    - Status: ✅ ACTIVELY WRITTEN TO (but not read from)

---

## Python Functions in sample_data.py (20 Total)

### 📦 ALL ACTIVELY USED (20 functions)

All these functions are currently called by AI agents:

#### Demand Forecasting Data

1. ~~`get_historical_demand()`~~ → ✅ **MIGRATED to database** (`historical_demand_data` table)
2. ~~`get_market_context()`~~ → ✅ **MIGRATED to database** (`market_context_data` table)
3. **`get_current_inventory()`** → Used by Demand Agent (Tool 1)
4. **`get_production_capacity()`** → Used by Demand Agent (Tool 1)
5. **`get_product_info()`** → Used by Demand Agent (Tool 1)

#### Inventory Management Data

6. **`get_current_inventory()`** → Used by Inventory Agent (Tool 1, 2, 4, 5)
7. **`get_warehouse_details()`** → Used by Inventory Agent (Tool 1)
8. **`get_supplier_performance()`** → Used by Inventory Agent (Tool 1, 6)
9. **`get_historical_stockouts()`** → Used by Inventory Agent (Tool 1, 5)
10. **`get_reorder_history()`** → Used by Inventory Agent (Tool 1)
11. **`get_product_info()`** → Used by Inventory Agent (Tool 5)

#### Machine Health Data

12. **`get_machine_fleet()`** → Used by Machine Health Agent
13. **`get_sensor_readings()`** → Used by Machine Health Agent
14. **`get_maintenance_history()`** → Used by Machine Health Agent
15. **`get_oee_history()`** → Used by Machine Health Agent

#### Production Planning Data

16. **`get_production_lines()`** → Used by Production Planning Agent
17. **`get_bill_of_materials()`** → Used by Production Planning Agent
18. **`get_production_history()`** → Used by Production Planning Agent
19. **`get_shift_configuration()`** → Used by Production Planning Agent

#### Supplier Coordination Data

20. **`get_open_purchase_orders()`** → Used by Supplier Agent
21. **`get_supplier_contracts()`** → Used by Supplier Agent
22. **`get_supply_chain_risk_factors()`** → Used by Supplier Agent

---

## Migration Status by AI Agent

### Demand Forecasting Agent

| Data Source | Current Location | Status |
|-------------|-----------------|--------|
| Historical Demand (52 weeks) | ✅ Database (`historical_demand_data`) | MIGRATED |
| Market Context | ✅ Database (`market_context_data`) | MIGRATED |
| Current Inventory | ❌ Python (`get_current_inventory()`) | NOT MIGRATED |
| Production Capacity | ❌ Python (`get_production_capacity()`) | NOT MIGRATED |
| Product Info | ❌ Python (`get_product_info()`) | NOT MIGRATED |

**Migration %: 40% (2 out of 5 sources)**

### Inventory Management Agent

| Data Source | Current Location | Status |
|-------------|-----------------|--------|
| Current Inventory | ❌ Python (`get_current_inventory()`) | NOT MIGRATED |
| Warehouse Details | ❌ Python (`get_warehouse_details()`) | NOT MIGRATED |
| Supplier Performance | ❌ Python (`get_supplier_performance()`) | NOT MIGRATED |
| Stockout History | ❌ Python (`get_historical_stockouts()`) | NOT MIGRATED |
| Reorder History | ❌ Python (`get_reorder_history()`) | NOT MIGRATED |
| Product Info | ❌ Python (`get_product_info()`) | NOT MIGRATED |

**Migration %: 0% (0 out of 6 sources)**

### Machine Health Agent

| Data Source | Current Location | Status |
|-------------|-----------------|--------|
| Machine Fleet | ❌ Python (`get_machine_fleet()`) | NOT MIGRATED |
| Sensor Readings | ❌ Python (`get_sensor_readings()`) | NOT MIGRATED |
| Maintenance History | ❌ Python (`get_maintenance_history()`) | NOT MIGRATED |
| OEE History | ❌ Python (`get_oee_history()`) | NOT MIGRATED |

**Migration %: 0% (0 out of 4 sources)**

### Production Planning Agent

| Data Source | Current Location | Status |
|-------------|-----------------|--------|
| Production Lines | ❌ Python (`get_production_lines()`) | NOT MIGRATED |
| Bill of Materials | ❌ Python (`get_bill_of_materials()`) | NOT MIGRATED |
| Production History | ❌ Python (`get_production_history()`) | NOT MIGRATED |
| Shift Configuration | ❌ Python (`get_shift_configuration()`) | NOT MIGRATED |

**Migration %: 0% (0 out of 4 sources)**

### Supplier Coordination Agent

| Data Source | Current Location | Status |
|-------------|-----------------|--------|
| Open Purchase Orders | ❌ Python (`get_open_purchase_orders()`) | NOT MIGRATED |
| Supplier Contracts | ❌ Python (`get_supplier_contracts()`) | NOT MIGRATED |
| Supply Chain Risk | ❌ Python (`get_supply_chain_risk_factors()`) | NOT MIGRATED |

**Migration %: 0% (0 out of 3 sources)**

---

## Overall Migration Status

### By Numbers

- **Total Data Sources:** 22 (across all agents)
- **Migrated to Database:** 2 (9%)
- **Still in Python Functions:** 20 (91%)

### By Agent

| Agent | Migrated | Not Migrated | Progress |
|-------|----------|--------------|----------|
| Demand Forecasting | 2/5 | 3/5 | 40% ✅ |
| Inventory Management | 0/6 | 6/6 | 0% ❌ |
| Machine Health | 0/4 | 4/4 | 0% ❌ |
| Production Planning | 0/4 | 4/4 | 0% ❌ |
| Supplier Coordination | 0/3 | 3/3 | 0% ❌ |

---

## Why This Matters

### ✅ Benefits of Database Storage (Already Done for 2 Sources)

1. **Repeatability:** Same data every time you run the pipeline
2. **Traceability:** Can trace every number back to database row
3. **SQL Validation:** Can verify AI inputs/outputs with SQL queries
4. **Auditability:** Full audit trail of what AI saw
5. **Professional:** Production-ready architecture

### ❌ Issues with Python Functions (Still True for 20 Sources)

1. **Random Data:** Changes every time (uses `random.gauss()`, etc.)
2. **No Traceability:** Can't trace numbers back to source
3. **No SQL Validation:** Can't verify with database queries
4. **Hard to Debug:** Data disappears after function returns
5. **Not Production-Ready:** Would need database in real deployment

---

## Next Steps for Full Migration

To achieve full database migration (like we did for `historical_demand_data`):

### Priority 1: Inventory Data (High Impact)
- Migrate `get_current_inventory()` → `inventory` table
- Migrate `get_warehouse_details()` → `warehouse_zones` table
- Migrate `get_supplier_performance()` → `suppliers` table
- Migrate `get_historical_stockouts()` → `stockout_events` table
- Migrate `get_reorder_history()` → `purchase_orders` table

### Priority 2: Machine Data (Medium Impact)
- Migrate `get_machine_fleet()` → `machines` table
- Migrate `get_maintenance_history()` → `maintenance_history` table
- Migrate `get_oee_history()` → `machine_oee_history` table
- Keep `get_sensor_readings()` as Python (real-time sensor data)

### Priority 3: Production Data (Medium Impact)
- Migrate `get_production_lines()` → `production_lines` table
- Migrate `get_bill_of_materials()` → `bom_items` table
- Migrate `get_production_history()` → `production_schedule` table

### Priority 4: Supplier Data (Low Impact)
- Migrate `get_supplier_contracts()` → `supplier_contracts` table
- Migrate `get_supply_chain_risk_factors()` → `supplier_risk` table

---

## Conclusion

**Current State:**
- ✅ 2 data sources migrated to database (Demand module only)
- ❌ 20 data sources still using Python functions
- 📊 9% migration complete

**Goal:**
- 100% migration for professional, production-ready system
- Full SQL validation capabilities
- Complete traceability and auditability

**The good news:** We've proven the migration pattern works! The process used for `historical_demand_data` and `market_context_data` can be repeated for all other data sources.
