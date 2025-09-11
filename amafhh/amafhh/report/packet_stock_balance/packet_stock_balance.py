# my_custom_app.my_custom_app.report.daily_activity_report.daily_activity_report.py
from decimal import Decimal

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "label": "<b>LOCATION</b>",
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 120
        },
        {
            "label": "<b>WIDTH</b>",
            "fieldname": "width",
            "fieldtype": "Data",
            "width": 80
        },
        {
            "label": "<b>LENGTH</b>",
            "fieldname": "length",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>GSM</b>",
            "fieldname": "gsm",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>BRAND</b>",
            "fieldname": "brand_item",
            "fieldtype": "Link",
            "options": "Brand",
            "width": 120
        },
        {
            "label": "<b>ITEM CODE</b>",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
     
        {
            "label": "<b>PALLET</b>",
            "fieldname": "pallet",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>QTY IN KG</b>",
            "fieldname": "qty_after_transaction",
            "fieldtype": "Data",
            "width": 120
        }

    ]
    return columns

def get_conditions(filters):
    conditions = []
    
    if filters.get("warehouse"):
        # Use recursive CTE to get all child warehouses
        warehouse_condition = """
        AND sle.warehouse IN (
            WITH RECURSIVE warehouse_tree AS (
                SELECT name, parent_warehouse 
                FROM `tabWarehouse` 
                WHERE name = %(warehouse)s
                UNION ALL
                SELECT w.name, w.parent_warehouse 
                FROM `tabWarehouse` w
                INNER JOIN warehouse_tree wt ON w.parent_warehouse = wt.name
            )
            SELECT name FROM warehouse_tree
        )
        """
        conditions.append(warehouse_condition)
    
    if filters.get("gsm"):
        conditions.append(f"AND item.gsm = %(gsm)s")
    if filters.get("item_category"):
        conditions.append(f"AND item.item_category = %(item_category)s")
    if filters.get("brand_item"):
        conditions.append(f"AND item.brand_item = %(brand_item)s")
    
    return " ".join(conditions)


def get_data(filters):
    data = []
    conditions = get_conditions(filters)

    query = f"""
            WITH Ranked AS (
			SELECT
				sle.warehouse,
				sle.item_code,
				sle.qty_after_transaction,
				item.width,
				item.length,
				item.gsm,
				item.brand_item,
				item.custom_weight_per_unit,
                (CASE
                WHEN item.custom_weight_per_unit IS NULL OR item.custom_weight_per_unit = 0 
                    THEN sle.qty_after_transaction
                ELSE sle.qty_after_transaction / item.custom_weight_per_unit
                END ) AS pallet,
				ROW_NUMBER() OVER (
				PARTITION BY sle.warehouse, sle.item_code
				ORDER BY sle.posting_date DESC, sle.posting_time DESC
				) AS rn
			FROM `tabStock Ledger Entry` sle
			LEFT JOIN `tabItem` item
				ON sle.item_code = item.item_code
			WHERE sle.is_cancelled = 0 
            AND sle.qty_after_transaction > 0
            {conditions}
             AND item.item_group IN ('PKT', 'REAM')
			)
			SELECT
			warehouse,
			item_code,
			qty_after_transaction,
			width,
			length,
			gsm,
			brand_item,
			custom_weight_per_unit,
            ROUND(pallet,4) AS pallet
			FROM Ranked
			WHERE rn = 1
            ORDER BY gsm;

    """

    query_result = frappe.db.sql(query, filters, as_dict=1)

    group_by = filters.get("group_by", "GSM")  # Default to GSM if not specified
    
    if group_by == "GSM":
        return group_by_gsm(query_result)
    else:
        return group_by_brand(query_result)

def group_by_gsm(query_result):
    """Group data by GSM and add total rows - only GSM grouping"""
    # Group data by GSM
    grouped_data = {}
    for row in query_result:
        gsm_key = row['gsm']
        if gsm_key not in grouped_data:
            grouped_data[gsm_key] = []
        grouped_data[gsm_key].append(row)
    
    # Process each GSM group
    processed_data = []
    for gsm, rows in grouped_data.items():
        # Add all rows for the current GSM group
        processed_data.extend(rows)
        
        # Calculate totals for the GSM group
        gsm_total_qty = sum(row['qty_after_transaction'] for row in rows)
        gsm_total_pallet = sum(row['pallet'] for row in rows)
        
        # Add a GSM total row
        gsm_total_row = {
            'warehouse': '',
            'item_code': '',
            'qty_after_transaction': f"<b>{round(gsm_total_qty, 4)}</b>",
            'width': '',
            'length': '',
            'gsm': f"Total ({gsm})",
            'brand_item': '',
            'custom_weight_per_unit': '',
            'pallet': f"<b>{round(gsm_total_pallet, 4)}</b>"
        }
        processed_data.append(gsm_total_row)
    
    return processed_data

def group_by_brand(query_result):
    """Group data by brand_item and add total rows - only brand grouping, show all brand_item values"""
    # Group data by brand_item only (no GSM hierarchy)
    grouped_data = {}
    for row in query_result:
        brand_key = row['brand_item']
        if brand_key not in grouped_data:
            grouped_data[brand_key] = []
        grouped_data[brand_key].append(row)
    
    # Process each brand group
    processed_data = []
    
    for brand, rows in grouped_data.items():
                
        # Add all rows for the current brand group (including repeated brand_item values)
        processed_data.extend(rows)
        
        # Calculate totals for the brand group
        brand_total_qty = sum(row['qty_after_transaction'] for row in rows)
        brand_total_pallet = sum(row['pallet'] for row in rows)
        
        # Add a brand total row
        brand_total_row = {
            'warehouse': '',
            'item_code': '',
            'qty_after_transaction': f"<b>{round(brand_total_qty, 4)}</b>",
            'width': '',
            'length': '',
            'gsm': '',
            'brand_item': f"Brand Total: {brand}",
            'custom_weight_per_unit': '',
            'pallet': f"<b>{round(brand_total_pallet, 4)}</b>"
        }
        processed_data.append(brand_total_row)
    
    return processed_data