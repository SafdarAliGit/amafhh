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
            "label": "<b>ITEM GROUP</b>",
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 120
        },
        {
            "label": "<b>NUMBER OF ITEMS</b>",
            "fieldname": "number_of_items",
            "fieldtype": "Data",
            "width": 80
        },
        {
            "label": "<b>IMPORT FILE</b>",
            "fieldname": "import_file",
            "fieldtype": "Link",
            "options": "Import File",
            "width": 120
        },
        {
            "label": "<b>BRAND ITEM</b>",
            "fieldname": "brand_item",
            "fieldtype": "Link",
            "options": "Brand",
            "width": 140
        },
        {
            "label": "<b>ITEM CATEGORY</b>",
            "fieldname": "item_category",
            "fieldtype": "Link",
            "options": "Item Category",
            "width": 120
        },
        {
            "label": "<b>WIDTH</b>",
            "fieldname": "width",
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
            "label": "<b>BAL. QTY</b>",
            "fieldname": "balance_qty",
            "fieldtype": "Data",
            "width": 120
        }

    ]
    return columns


def get_conditions(filters):
    conditions = []
    if filters.get("item_group"):
        conditions.append(f"AND item.item_group = %(item_group)s")
    if filters.get("import_file"):
        conditions.append(f"AND item.import_file = %(import_file)s")
    if filters.get("gsm"):
        conditions.append(f"AND item.gsm = %(gsm)s")
    return " ".join(conditions)


def get_data(filters):
    data = []
    conditions = get_conditions(filters)

    stock_balance_query = f"""
            SELECT 
                item.item_group,
                COUNT(DISTINCT item.name) AS number_of_items,
                item.import_file,
                item.brand_item,
                item.item_category,
                COALESCE(item.width, 0) AS width,
                COALESCE(item.gsm, 0) AS gsm,
                (SUM(CASE WHEN sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) - ABS(SUM(CASE WHEN sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END))) AS balance_qty
            FROM `tabItem` AS item
            JOIN `tabStock Ledger Entry` AS sle ON item.name = sle.item_code
            WHERE
                sle.is_cancelled != 1
                {conditions}
             GROUP BY item.brand_item, item.import_file, item.width, item.gsm
            HAVING balance_qty != 0
            ORDER BY item.item_group
        """

    stock_balance_result = frappe.db.sql(stock_balance_query, filters, as_dict=1)
    data.extend(stock_balance_result)
    return data
