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
            "label": "<b>PALLET</b>",
            "fieldname": "custom_weight_per_unit",
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
        conditions.append(f"AND sle.warehouse = %(warehouse)s")
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
				sle.posting_date,
				sle.posting_time,
				item.width,
				item.length,
				item.gsm,
				item.brand_item,
				item.custom_weight_per_unit,
				ROW_NUMBER() OVER (
				PARTITION BY sle.warehouse, sle.item_code
				ORDER BY sle.posting_date DESC, sle.posting_time DESC
				) AS rn
			FROM `tabStock Ledger Entry` sle
			LEFT JOIN `tabItem` item
				ON sle.item_code = item.item_code
			WHERE sle.is_cancelled = 0 {conditions}
			)
			SELECT
			warehouse,
			item_code,
			qty_after_transaction,
			width,
			length,
			gsm,
			brand_item,
			custom_weight_per_unit
			FROM Ranked
			WHERE rn = 1;

    """

    query_result = frappe.db.sql(query, filters, as_dict=1)
    data.extend(query_result)
    return data
