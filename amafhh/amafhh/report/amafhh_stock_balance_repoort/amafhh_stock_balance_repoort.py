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
            "label": "<b>ITEM CODE</b>",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },

        {
            "label": "<b>BRAND ITEM</b>",
            "fieldname": "brand_item",
            "fieldtype": "Link",
            "options": "Brand",
            "width": 120
        },
        {
            "label": "<b>WIDTH</b>",
            "fieldname": "width",
            "fieldtype": "Data",
            "width": 120

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
            "label": "<b>ITEM GROUP</b>",
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 120
        },
        {
            "label": "<b>IMPORT FILE</b>",
            "fieldname": "import_file",
            "fieldtype": "Link",
            "options": "Import File",
            "width": 120
        },
        {
            "label": "<b>IN QTY</b>",
            "fieldname": "in_qty",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>IN RM/PKT</b>",
            "fieldname": "in_rm_pkt",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>OUT QTY</b>",
            "fieldname": "out_qty",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>OUT RM/PKT</b>",
            "fieldname": "out_rm_pkt",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>BAL. QTY</b>",
            "fieldname": "balance_qty",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>BAL. RM/PKT</b>",
            "fieldname": "balance_rm_pkt",
            "fieldtype": "Data",
            "width": 120
        }

    ]
    return columns


def get_conditions(filters):
    conditions = []
    if filters.get("item_code"):
        conditions.append(f"item.item_code = %(item_code)s")
    if filters.get("item_group"):
        conditions.append(f"item.item_group = %(item_group)s")
    if filters.get("warehouse"):
        conditions.append(f"sle.warehouse = %(warehouse)s")
    if filters.get("from_date"):
        conditions.append(f"sle.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append(f"sle.posting_date <= %(to_date)s")
    return " AND ".join(conditions)


def get_data(filters):
    data = []
    conditions = get_conditions(filters)
    if conditions:
        conditions = "WHERE " + conditions

    stock_balance_query = f"""
        SELECT 
            item.item_code,
            item.brand_item,
            COALESCE(item.width, 0) AS width,
            COALESCE(item.length, 0) AS length,
            COALESCE(item.gsm, 0) AS gsm,
            item.item_group,
            CASE WHEN item.item_group = 'Card' THEN 3100 WHEN item.item_group = 'Sheet' THEN 15500 ELSE 0 END AS factor,
            item.import_file,
            SUM(CASE WHEN sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) AS in_qty,
            '' AS in_rm_pkt,
            ABS(SUM(CASE WHEN sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END)) AS out_qty,
            '' AS out_rm_pkt,
            (SUM(CASE WHEN sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) - ABS(SUM(CASE WHEN sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END))) AS balance_qty,
            '' AS balance_rm_pkt  
        FROM `tabItem` AS item
        INNER JOIN `tabStock Ledger Entry` AS sle ON item.name = sle.item_code
        {conditions} AND item.item_group != 'Roll'
        GROUP BY item.item_code
        ORDER BY item.item_code
    """

    stock_balance_result = frappe.db.sql(stock_balance_query,filters, as_dict=1)
    for i in stock_balance_result:
        factor = Decimal(i.factor)
        width = Decimal(i.width)
        length = Decimal(i.length)
        gsm = Decimal(i.gsm)

        in_qty = Decimal(i.in_qty)
        out_qty = Decimal(i.out_qty)
        balance_qty = Decimal(i.balance_qty)

        i.in_rm_pkt = round(in_qty / ((width * length * gsm) / factor), 2)
        i.out_rm_pkt = round(out_qty / ((width * length * gsm) / factor), 2)
        i.balance_rm_pkt = round(balance_qty / ((width * length * gsm) / factor), 2)

    data.extend(stock_balance_result)
    return data
