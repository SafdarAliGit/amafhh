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
            "label": "<b>ITEM CODE</b>",
            "fieldname": "reel_no",
            "fieldtype": "Link",
            "options": "Item",
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
        conditions.append(f"AND pii.import_file = %(import_file)s")
    return " ".join(conditions)


def get_data(filters):
    data = []
    conditions = get_conditions(filters)

    stock_damage_query = f"""
            SELECT 
                item.item_code,
                item.width,
                item.gsm,
                item.qty,
                sle.item_code AS reel_no,
                SUM(CASE WHEN sle.warehouse = 'Damaged - A' THEN sle.actual_qty ELSE 0 END) AS damaged,
                SUM(CASE WHEN sle.warehouse = 'Goods In Transit - A' THEN sle.actual_qty ELSE 0 END) AS sami_finished,
                SUM(CASE WHEN sle.warehouse = 'Non Physical Damage - A' THEN sle.actual_qty ELSE 0 END) AS non_physical
            FROM 
                `tabStock Ledger Entry` AS sle, `tabItem` AS item
            WHERE
                SUBSTRING_INDEX(sle.item_code, '-', 1) = item.item_code 
                AND sle.is_cancelled != 1 
                AND sle.voucher_type = 'Stock Entry'
                {conditions}
            GROUP BY 
                sle.item_code,item.width,item.gsm,item.qty,item.item_code
            HAVING
                damaged > 0 OR sami_finished > 0 OR non_physical > 0;
        """

    stock_damage_result = frappe.db.sql(stock_damage_query, filters, as_dict=1)
    data.extend(stock_damage_result)
    return data
