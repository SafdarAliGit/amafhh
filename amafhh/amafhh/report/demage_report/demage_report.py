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
        },
        {
            "label": "<b>TOTAL WEIGHT</b>",
            "fieldname": "total_weight",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>DMG RATIO</b>",
            "fieldname": "damage_avg",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>NP RATIO</b>",
            "fieldname": "np_damage_avg",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>BAL. WT.</b>",
            "fieldname": "balance_weight",
            "fieldtype": "Data",
            "width": 140

        },
        {
            "label": "<b>DMG GSM AVG.</b>",
            "fieldname": "conversion_gsm",
            "fieldtype": "Data",
            "width": 140

        },
        {
            "label": "<b>NP GSM AVG.</b>",
            "fieldname": "np_conversion_gsm",
            "fieldtype": "Data",
            "width": 140

        }

    ]
    return columns


import frappe


def get_conditions(filters):
    conditions = []
    if filters.get("import_file"):
        conditions.append(f"item.import_file = '{filters.get('import_file')}'")
    if conditions:
        return " AND ".join(conditions)
    else:
        return ""

def get_data(filters):
    data = []
    conditions = get_conditions(filters)
    conditions_query = f"WHERE item.item_code NOT LIKE '%-%'" if not conditions else f"WHERE {conditions} AND item.item_code NOT LIKE '%-%'"

    stock_damage_query = f"""
        SELECT 
            item.item_code,
            item.width,
            item.gsm,
            ROUND(item.qty, 4) AS qty,
            COALESCE(SUM(CASE WHEN sle.warehouse = 'Finished Goods - A' THEN sle.actual_qty ELSE 0 END), 0) AS finished,
            COALESCE(SUM(CASE WHEN sle.warehouse = 'Damaged - A' THEN sle.actual_qty ELSE 0 END), 0) AS damaged,
            COALESCE(SUM(CASE WHEN sle.warehouse = 'Goods In Transit - A' THEN sle.actual_qty ELSE 0 END), 0) AS sami_finished,
            COALESCE(SUM(CASE WHEN sle.warehouse = 'Non Fisical Damage - A' THEN sle.actual_qty ELSE 0 END), 0) AS non_physical,
            ROUND((COALESCE(SUM(CASE WHEN sle.warehouse = 'Finished Goods - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Damaged - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Goods In Transit - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Non Fisical Damage - A' THEN sle.actual_qty ELSE 0 END), 0)),4) AS total_weight,
            ROUND(((COALESCE(SUM(CASE WHEN sle.warehouse = 'Finished Goods - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Damaged - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Goods In Transit - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Non Fisical Damage - A' THEN sle.actual_qty ELSE 0 END), 0)) / (COALESCE(SUM(CASE WHEN sle.warehouse = 'Finished Goods - A' THEN sle.actual_qty ELSE 0 END), 0))),4) AS damage_avg,
            ROUND(((COALESCE(SUM(CASE WHEN sle.warehouse = 'Finished Goods - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Damaged - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Goods In Transit - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Non Fisical Damage - A' THEN sle.actual_qty ELSE 0 END), 0))/(COALESCE(SUM(CASE WHEN sle.warehouse = 'Finished Goods - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Damaged - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Goods In Transit - A' THEN sle.actual_qty ELSE 0 END), 0))),4) AS np_damage_avg,
            ROUND((item.qty - (COALESCE(SUM(CASE WHEN sle.warehouse = 'Finished Goods - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Damaged - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Goods In Transit - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Non Fisical Damage - A' THEN sle.actual_qty ELSE 0 END), 0))),4) AS balance_weight,
            ROUND((((COALESCE(SUM(CASE WHEN sle.warehouse = 'Finished Goods - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Damaged - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Goods In Transit - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Non Fisical Damage - A' THEN sle.actual_qty ELSE 0 END), 0)) / (COALESCE(SUM(CASE WHEN sle.warehouse = 'Finished Goods - A' THEN sle.actual_qty ELSE 0 END), 0)))* item.gsm),4) AS conversion_gsm,
            ROUND(((COALESCE(SUM(CASE WHEN sle.warehouse = 'Finished Goods - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Damaged - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Goods In Transit - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Non Fisical Damage - A' THEN sle.actual_qty ELSE 0 END), 0))/(COALESCE(SUM(CASE WHEN sle.warehouse = 'Finished Goods - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Damaged - A' THEN sle.actual_qty ELSE 0 END), 0) + COALESCE(SUM(CASE WHEN sle.warehouse = 'Goods In Transit - A' THEN sle.actual_qty ELSE 0 END), 0))* item.gsm),4) AS np_conversion_gsm

        FROM 
            `tabItem` AS item
        LEFT JOIN 
            `tabStock Ledger Entry` AS sle ON SUBSTRING_INDEX(sle.item_code, '-', 1) = item.item_code 
             AND sle.is_cancelled != 1 
             AND sle.voucher_type = 'Stock Entry' 
             AND item.item_code NOT LIKE '%-%'
        {conditions_query}
        GROUP BY 
             item.item_code, item.width, item.gsm, item.qty
        ORDER BY 
            item.item_code
    """

    stock_damage_result = frappe.db.sql(stock_damage_query, as_dict=True)
    data.extend(stock_damage_result)
    return data




