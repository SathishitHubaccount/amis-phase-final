"""
CSV Export Utilities for AMIS
Generates CSV files from database data for export to Excel/ERP systems
"""
import csv
import io
from typing import List, Dict, Any
from datetime import datetime


def dict_to_csv(data: List[Dict[str, Any]], filename: str = None) -> str:
    """
    Convert list of dictionaries to CSV format

    Args:
        data: List of dictionaries with consistent keys
        filename: Optional filename (default: generated from timestamp)

    Returns:
        CSV string with UTF-8 BOM for Excel compatibility
    """
    if not data:
        return ""

    # Create CSV in memory
    output = io.StringIO()

    # Add UTF-8 BOM for Excel compatibility
    output.write('\ufeff')

    # Get all unique keys from all records (in case some records have different keys)
    all_keys = set()
    for record in data:
        all_keys.update(record.keys())

    fieldnames = sorted(list(all_keys))

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

    return output.getvalue()


def generate_filename(prefix: str, extension: str = 'csv') -> str:
    """Generate timestamped filename"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.{extension}"


# Specific export formatters for different data types

def export_inventory(inventory_data: List[Dict]) -> str:
    """
    Export inventory data with formatted columns
    """
    formatted_data = []
    for item in inventory_data:
        formatted_data.append({
            'Product ID': item.get('product_id', ''),
            'Product Name': item.get('product_name', ''),
            'Category': item.get('category', ''),
            'Current Stock': item.get('current_stock', 0),
            'Safety Stock': item.get('safety_stock', 0),
            'Reorder Point': item.get('reorder_point', 0),
            'Avg Daily Usage': round(item.get('avg_daily_usage', 0), 2),
            'Lead Time (days)': item.get('lead_time', 0),
            'Stockout Risk (%)': round(item.get('stockout_risk', 0), 1),
            'Last Updated': item.get('last_updated', ''),
        })

    return dict_to_csv(formatted_data)


def export_machines(machines_data: List[Dict]) -> str:
    """
    Export machine data with formatted columns
    """
    formatted_data = []
    for machine in machines_data:
        formatted_data.append({
            'Machine ID': machine.get('id', ''),
            'Machine Name': machine.get('name', ''),
            'Type': machine.get('type', ''),
            'Line': machine.get('line', ''),
            'Status': machine.get('status', ''),
            'OEE (%)': round(machine.get('oee', 0), 1),
            'Availability (%)': round(machine.get('availability', 0), 1),
            'Performance (%)': round(machine.get('performance', 0), 1),
            'Quality (%)': round(machine.get('quality', 0), 1),
            'Failure Risk (%)': round(machine.get('failure_risk', 0), 1),
            'Capacity (units/hr)': machine.get('production_capacity', 0),
            'Utilization (%)': round(machine.get('current_utilization', 0), 1),
            'Last Maintenance': machine.get('last_maintenance', ''),
            'Next Maintenance': machine.get('next_maintenance', ''),
        })

    return dict_to_csv(formatted_data)


def export_oee_history(oee_data: List[Dict], machine_id: str) -> str:
    """
    Export OEE history data
    """
    formatted_data = []
    for record in oee_data:
        formatted_data.append({
            'Machine ID': machine_id,
            'Date': record.get('date', ''),
            'OEE (%)': round(record.get('oee', 0), 1),
            'Availability (%)': round(record.get('availability', 0), 1),
            'Performance (%)': round(record.get('performance', 0), 1),
            'Quality (%)': round(record.get('quality', 0), 1),
            'Recorded At': record.get('recorded_at', ''),
        })

    return dict_to_csv(formatted_data)


def export_production_schedule(schedule_data: List[Dict]) -> str:
    """
    Export production schedule data
    """
    formatted_data = []
    for item in schedule_data:
        formatted_data.append({
            'Product ID': item.get('product_id', ''),
            'Week Number': item.get('week_number', ''),
            'Week Start': item.get('week_start_date', ''),
            'Demand': item.get('demand', 0),
            'Planned Production': item.get('planned_production', 0),
            'Actual Production': item.get('actual_production', 0) or 'N/A',
            'Capacity': item.get('capacity', 0),
            'Gap': item.get('gap', 0),
            'Overtime Hours': round(item.get('overtime_hours', 0), 1),
            'Created At': item.get('created_at', ''),
        })

    return dict_to_csv(formatted_data)


def export_suppliers(suppliers_data: List[Dict]) -> str:
    """
    Export supplier data
    """
    formatted_data = []
    for supplier in suppliers_data:
        formatted_data.append({
            'Supplier ID': supplier.get('id', ''),
            'Name': supplier.get('name', ''),
            'Location': supplier.get('location', ''),
            'Score': supplier.get('score', 0),
            'Rating': supplier.get('rating', ''),
            'On-Time Delivery (%)': round(supplier.get('on_time_delivery', 0), 1),
            'Quality Score (%)': round(supplier.get('quality_score', 0), 1),
            'Cost Index': supplier.get('cost_index', 0),
            'Base Cost ($)': round(supplier.get('base_cost', 0), 2),
            'Lead Time (days)': supplier.get('lead_time', 0),
            'Lead Time Variability': supplier.get('lead_time_variability', 0),
            'Risk Level': supplier.get('risk', ''),
            'MOQ': supplier.get('moq', 0),
            'Payment Terms': supplier.get('payment_terms', ''),
            'Currency': supplier.get('currency', ''),
        })

    return dict_to_csv(formatted_data)


def export_work_orders(work_orders_data: List[Dict]) -> str:
    """
    Export work orders data
    """
    formatted_data = []
    for wo in work_orders_data:
        formatted_data.append({
            'Work Order ID': wo.get('id', ''),
            'Machine ID': wo.get('machine_id', ''),
            'Machine Name': wo.get('machine_name', ''),
            'Type': wo.get('type', ''),
            'Priority': wo.get('priority', ''),
            'Assigned To': wo.get('assigned_to', '') or 'Unassigned',
            'Scheduled Date': wo.get('scheduled_date', ''),
            'Est. Duration (hrs)': wo.get('estimated_duration', '') or '',
            'Description': wo.get('description', ''),
            'Status': wo.get('status', ''),
            'Created By': wo.get('created_by', ''),
            'Created At': wo.get('created_at', ''),
            'Completed At': wo.get('completed_at', '') or 'Not completed',
        })

    return dict_to_csv(formatted_data)


def export_demand_forecast(forecast_data: List[Dict], product_id: str) -> str:
    """
    Export demand forecast data
    """
    formatted_data = []
    for record in forecast_data:
        formatted_data.append({
            'Product ID': product_id,
            'Week Number': record.get('week_number', ''),
            'Forecast Date': record.get('forecast_date', ''),
            'Optimistic': record.get('optimistic', 0),
            'Base Case': record.get('base_case', 0),
            'Pessimistic': record.get('pessimistic', 0),
            'Actual': record.get('actual', 0) or 'N/A',
            'Variance (%)': round(
                ((record.get('actual', 0) - record.get('base_case', 0)) / record.get('base_case', 1) * 100)
                if record.get('actual') and record.get('base_case') else 0,
                1
            ) if record.get('actual') else 'N/A',
            'Created At': record.get('created_at', ''),
        })

    return dict_to_csv(formatted_data)


def export_inventory_history(history_data: List[Dict], product_id: str) -> str:
    """
    Export inventory history data
    """
    formatted_data = []
    for record in history_data:
        formatted_data.append({
            'Product ID': product_id,
            'Date': record.get('date', ''),
            'Stock Level': record.get('stock_level', 0),
            'Stockout Risk (%)': round(record.get('stockout_risk', 0), 1),
            'Days Supply': round(record.get('days_supply', 0), 1),
            'Recorded At': record.get('recorded_at', ''),
        })

    return dict_to_csv(formatted_data)
