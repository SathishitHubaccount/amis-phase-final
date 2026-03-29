"""
AI Database Bridge
Automatically syncs AI agent outputs to database tables
This is the CRITICAL missing piece that makes AI results actionable
"""
from datetime import datetime, timedelta
from database import (
    create_demand_forecast,
    update_inventory,
    update_production_schedule,
    create_work_order,
    log_activity,
    get_db_connection
)
import json

# Import decision creation helpers
from ai_database_bridge_helpers import (
    create_forecast_decision,
    create_inventory_decision,
    create_production_decision,
    create_maintenance_decision
)


class AIDatabaseBridge:
    """
    Bridges the gap between AI agent outputs and database persistence.

    This class:
    1. Takes structured AI agent outputs
    2. Validates and transforms data
    3. Writes to appropriate database tables
    4. Creates audit trail
    5. Triggers alerts/notifications
    """

    def __init__(self):
        self.changes_made = []
        self.warnings = []
        self.errors = []

    def sync_pipeline_results(self, pipeline_result: dict, auto_execute: bool = True) -> dict:
        """
        Main entry point: sync complete pipeline results to database

        Args:
            pipeline_result: Output from OrchestratorAgent.run_full_pipeline()
            auto_execute: If True, auto-approve LOW risk items and queue others.
                         If False, create decisions but don't execute anything.

        Returns:
            Summary of changes made and pending approvals
        """
        from approval_system import get_approval_system

        product_id = pipeline_result.get("product_id")
        planning_weeks = pipeline_result.get("planning_horizon_weeks", 4)
        outputs = pipeline_result.get("pipeline_outputs", {})

        print(f"\n🔄 AI DATABASE BRIDGE: Syncing results for {product_id}")
        print("=" * 60)

        approval_system = get_approval_system()
        decisions_created = []

        # 1. Create decisions for demand forecasts (LOW RISK - auto-approve)
        if "demand" in outputs:
            decision = self._create_forecast_decision(product_id, outputs["demand"], planning_weeks)
            decisions_created.append(decision)
            if auto_execute and decision.status.value == "auto_approved":
                self._sync_demand_forecasts(product_id, outputs["demand"], planning_weeks)

        # 2. Create decisions for inventory updates (MEDIUM RISK - require approval)
        if "inventory" in outputs:
            decision = self._create_inventory_decision(product_id, outputs["inventory"])
            decisions_created.append(decision)
            if auto_execute and decision.status.value == "auto_approved":
                self._sync_inventory_data(product_id, outputs["inventory"])

        # 3. Create decisions for production schedule (HIGH RISK - require approval)
        if "production" in outputs:
            decision = self._create_production_decision(product_id, outputs["production"], planning_weeks)
            decisions_created.append(decision)
            if auto_execute and decision.status.value == "auto_approved":
                self._sync_production_schedule(product_id, outputs["production"], planning_weeks)

        # 4. Create decisions for machine maintenance (HIGH RISK - require approval)
        if "machine_health" in outputs:
            decision = self._create_maintenance_decision(outputs["machine_health"])
            decisions_created.append(decision)
            if auto_execute and decision.status.value == "auto_approved":
                self._sync_machine_actions(outputs["machine_health"])

        # 5. Create audit log entry
        self._create_audit_log(product_id, pipeline_result)

        print("=" * 60)
        print(f"✅ SYNC COMPLETE: {len(self.changes_made)} executed, {len([d for d in decisions_created if d.requires_approval])} pending approval\n")

        return {
            "success": True,
            "mode": "auto_execute" if auto_execute else "approval_required",
            "changes_made": self.changes_made,
            "warnings": self.warnings,
            "errors": self.errors,
            "decisions_created": [d.to_dict() for d in decisions_created],
            "pending_approvals": [d.to_dict() for d in decisions_created if d.status.value == "pending"],
            "summary": self._generate_summary()
        }

    def _sync_demand_forecasts(self, product_id: str, demand_output: dict, weeks: int):
        """Write AI demand forecasts to demand_forecasts table"""
        print("\n📊 [1/4] Syncing Demand Forecasts...")

        try:
            # Extract scenario data
            scenarios = demand_output.get("scenarios", {})
            base_weekly = scenarios.get("base", {}).get("weekly_avg", 0)
            optimistic_weekly = scenarios.get("optimistic", {}).get("weekly_avg", 0)
            pessimistic_weekly = scenarios.get("pessimistic", {}).get("weekly_avg", 0)

            # Clear existing forecasts for this product (avoid duplicates)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM demand_forecasts WHERE product_id = ?", (product_id,))
            conn.commit()

            # Create forecasts for next N weeks
            today = datetime.now()
            created_count = 0

            for week_num in range(1, weeks + 1):
                week_date = today + timedelta(days=week_num * 7)

                forecast_id = create_demand_forecast(
                    product_id=product_id,
                    week_number=week_num,
                    forecast_data={
                        "forecast_date": week_date.strftime("%Y-%m-%d"),
                        "base_case": base_weekly,
                        "optimistic": optimistic_weekly,
                        "pessimistic": pessimistic_weekly,
                        "actual": None
                    }
                )
                created_count += 1

            conn.close()

            change_msg = f"Created {created_count} demand forecasts (Base: {base_weekly} units/week)"
            self.changes_made.append(change_msg)
            print(f"  ✅ {change_msg}")

        except Exception as e:
            error_msg = f"Failed to sync demand forecasts: {str(e)}"
            self.errors.append(error_msg)
            print(f"  ❌ {error_msg}")

    def _sync_inventory_data(self, product_id: str, inventory_output: dict):
        """Update inventory table with AI-calculated metrics"""
        print("\n📦 [2/4] Syncing Inventory Data...")

        try:
            updates = {}

            # Update stockout risk if AI calculated it
            if "stockout_probability_pct" in inventory_output:
                updates["stockout_risk"] = inventory_output["stockout_probability_pct"]

            # Update reorder point if AI calculated it
            if "reorder_point_units" in inventory_output:
                updates["reorder_point"] = inventory_output["reorder_point_units"]

            # Update safety stock if AI recommended changes
            if "safety_stock" in inventory_output:
                updates["safety_stock"] = inventory_output["safety_stock"]

            if updates:
                success = update_inventory(product_id, updates)
                if success:
                    change_msg = f"Updated inventory: " + ", ".join([f"{k}={v}" for k, v in updates.items()])
                    self.changes_made.append(change_msg)
                    print(f"  ✅ {change_msg}")
                else:
                    self.warnings.append(f"Inventory update returned False")
            else:
                print("  ℹ️  No inventory updates needed")

        except Exception as e:
            error_msg = f"Failed to sync inventory: {str(e)}"
            self.errors.append(error_msg)
            print(f"  ❌ {error_msg}")

    def _sync_production_schedule(self, product_id: str, production_output: dict, weeks: int):
        """Update production_schedule table with AI-generated MPS"""
        print("\n🏭 [3/4] Syncing Production Schedule...")

        try:
            mps_summary = production_output.get("mps_summary", {})
            weekly_target = production_output.get("weekly_production_target", 0)

            # Get existing schedule from database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, week_number, demand, planned_production, capacity, overtime_hours
                FROM production_schedule
                WHERE product_id = ?
                ORDER BY week_number
                LIMIT ?
            """, (product_id, weeks))

            existing_schedules = [dict(row) for row in cursor.fetchall()]

            updated_count = 0
            for schedule in existing_schedules:
                schedule_id = schedule["id"]

                # Update planned production to match AI recommendation
                updates = {
                    "planned_production": weekly_target,
                    "gap": schedule["demand"] - weekly_target,
                    "overtime_hours": mps_summary.get("total_overtime_hours", 0) // weeks
                }

                cursor.execute("""
                    UPDATE production_schedule
                    SET planned_production = ?, gap = ?, overtime_hours = ?
                    WHERE id = ?
                """, (
                    updates["planned_production"],
                    updates["gap"],
                    updates["overtime_hours"],
                    schedule_id
                ))
                updated_count += 1

            conn.commit()
            conn.close()

            change_msg = f"Updated {updated_count} production schedules (Target: {weekly_target} units/week)"
            self.changes_made.append(change_msg)
            print(f"  ✅ {change_msg}")

        except Exception as e:
            error_msg = f"Failed to sync production schedule: {str(e)}"
            self.errors.append(error_msg)
            print(f"  ❌ {error_msg}")

    def _sync_machine_actions(self, machine_output: dict):
        """Create work orders for critical machine maintenance"""
        print("\n🔧 [4/4] Syncing Machine Maintenance Actions...")

        try:
            # Extract critical machines that need maintenance
            critical_machines = machine_output.get("critical_machines", [])
            recommendations = machine_output.get("recommendations", [])

            created_count = 0
            for machine_id in critical_machines:
                # Check if work order already exists
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as count FROM work_orders
                    WHERE machine_id = ? AND status = 'open'
                """, (machine_id,))
                existing = cursor.fetchone()["count"]
                conn.close()

                if existing > 0:
                    print(f"  ℹ️  Work order already exists for {machine_id}")
                    continue

                # Create new work order
                today = datetime.now()
                wo_id = create_work_order({
                    "machine_id": machine_id,
                    "type": "Preventive Maintenance",
                    "priority": "high",
                    "assigned_to": "Maintenance Team",
                    "scheduled_date": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "estimated_duration": 8.0,
                    "description": f"AI-detected high failure risk. Immediate maintenance required.",
                    "created_by": "AI System"
                })

                created_count += 1
                change_msg = f"Created work order {wo_id} for {machine_id}"
                self.changes_made.append(change_msg)
                print(f"  ✅ {change_msg}")

            if created_count == 0:
                print("  ℹ️  No critical maintenance actions needed")

        except Exception as e:
            error_msg = f"Failed to sync machine actions: {str(e)}"
            self.errors.append(error_msg)
            print(f"  ❌ {error_msg}")

    def execute_approved_decision(self, decision_id: int, decision_type: str, payload: dict, product_id: str, planning_weeks: int = 4) -> dict:
        """Execute a previously approved decision by syncing its data to DB"""
        self.changes_made = []
        self.errors = []
        try:
            if decision_type == 'demand_forecast_update':
                self._sync_demand_forecasts(product_id, payload, planning_weeks)
            elif decision_type == 'inventory_adjustment':
                self._sync_inventory_data(product_id, payload)
            elif decision_type == 'production_schedule_change':
                self._sync_production_schedule(product_id, payload, planning_weeks)
            elif decision_type == 'machine_maintenance':
                self._sync_machine_actions(payload)

            from approval_system import get_approval_system
            get_approval_system().mark_executed(decision_id)

            return {"success": True, "changes": self.changes_made, "errors": self.errors}
        except Exception as e:
            return {"success": False, "error": str(e), "changes": self.changes_made}

    def _create_audit_log(self, product_id: str, pipeline_result: dict):
        """Create audit trail of AI-driven changes"""
        report = pipeline_result.get("manufacturing_intelligence_report", {})
        system_health = report.get("system_health_score", "N/A")

        log_activity(
            user="AI Pipeline",
            action="Manufacturing Intelligence Analysis",
            details=f"Analyzed {product_id} | System Health: {system_health}/100 | Changes: {len(self.changes_made)}"
        )

    def _generate_summary(self) -> str:
        """Generate human-readable summary"""
        summary = f"""
AI Database Sync Summary:
✅ Changes Applied: {len(self.changes_made)}
⚠️  Warnings: {len(self.warnings)}
❌ Errors: {len(self.errors)}

Changes:
{chr(10).join(f"  • {change}" for change in self.changes_made)}
"""
        if self.warnings:
            summary += f"\nWarnings:\n{chr(10).join(f'  • {w}' for w in self.warnings)}"
        if self.errors:
            summary += f"\nErrors:\n{chr(10).join(f'  • {e}' for e in self.errors)}"

        return summary


# Singleton instance
_bridge_instance = None

def get_bridge() -> AIDatabaseBridge:
    """Get singleton bridge instance"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = AIDatabaseBridge()
    return _bridge_instance
