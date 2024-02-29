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
            "label": "<b>REEL NO</b>",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": "<b>SIZE</b>",
            "fieldname": "width",
            "fieldtype": "Data",
            "width": 80
        },
        {
            "label": "<b>GSM</b>",
            "fieldname": "gsm",
            "fieldtype": "Link",
            "options": "Import File",
            "width": 120
        },
        {
            "label": "<b>REEL WEIGHT</b>",
            "fieldname": "qty",
            "fieldtype": "Data",
            "width": 140
        },

        {
            "label": "<b>FINISHED</b>",
            "fieldname": "finished",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>DAMAGED</b>",
            "fieldname": "damaged",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>SAMI FINISHED</b>",
            "fieldname": "sami_finished",
            "fieldtype": "Data",
            "width": 120

        },
        {
            "label": "<b>NO PHYSICAL</b>",
            "fieldname": "non_physical",
            "fieldtype": "Data",
            "width": 120
        }

    ]
    return columns


def get_conditions(filters):
    conditions = []
    if filters.get("import_file"):
        conditions.append(f"AND item.import_file = %(import_file)s")
    return " ".join(conditions)


def get_data(filters):
    data = []
    conditions = get_conditions(filters)

    stock_damage_query = f"""
            SELECT 
                item.item_code,
                item.width,
                item.gsm,
                ROUND(item.qty, 4) AS qty,
                COALESCE(SUM(CASE WHEN sle.warehouse = 'Finished Goods - A' THEN sle.actual_qty ELSE 0 END), 0) AS finished,
                COALESCE(SUM(CASE WHEN sle.warehouse = 'Damaged - A' THEN sle.actual_qty ELSE 0 END), 0) AS damaged,
                COALESCE(SUM(CASE WHEN sle.warehouse = 'Goods In Transit - A' THEN sle.actual_qty ELSE 0 END), 0) AS sami_finished,
                COALESCE(SUM(CASE WHEN sle.warehouse = 'Non Physical Damage - A' THEN sle.actual_qty ELSE 0 END), 0) AS non_physical
            FROM 
                `tabItem` AS item
            LEFT JOIN 
                `tabStock Ledger Entry` AS sle ON SUBSTRING_INDEX(sle.item_code, '-', 1) = item.item_code 
                                                AND sle.is_cancelled != 1 
                                                AND sle.voucher_type = 'Stock Entry'
            {conditions}
            GROUP BY 
                item.width, item.gsm, item.qty, item.item_code
            ORDER BY item.item_code
        """

    stock_damage_result = frappe.db.sql(stock_damage_query, filters, as_dict=1)
    data.extend(stock_damage_result)
    return data
