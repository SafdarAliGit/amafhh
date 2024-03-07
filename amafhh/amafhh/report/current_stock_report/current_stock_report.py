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
            "label": "<b>IMPORT FILE</b>",
            "fieldname": "import_file",
            "fieldtype": "Link",
            "options": "Import File",
            "width": 120
        },

        {
            "label": "<b>ITEM CATEGORY</b>",
            "fieldname": "item_category",
            "fieldtype": "Link",
            "options": "Item Category",
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
            "label": "<b>KG</b>",
            "fieldname": "balance_qty",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>RM/PKT</b>",
            "fieldname": "balance_rm_pkt",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>VALUE RATE</b>",
            "fieldname": "valuation_rate",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "<b>AMOUNT</b>",
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 120
        }

    ]
    return columns


def get_conditions(filters):
    conditions = []
    if filters.get("item_code"):
        conditions.append("item.item_code = %(item_code)s")
    if filters.get("item_group"):
        conditions.append("item.item_group = %(item_group)s")
    if filters.get("warehouse"):
        conditions.append("sle.warehouse = %(warehouse)s")
    if filters.get("to_date"):
        conditions.append("sle.posting_date <= %(to_date)s")
    return " AND ".join(conditions)


from decimal import Decimal

def get_data(filters):
    data = []
    conditions = get_conditions(filters)

    stock_balance_query = f"""
        SELECT 
            item.import_file,
            item.item_category,
            item.item_group,
            item.brand_item,
            item.item_code,
            COALESCE(item.width, 0) AS width,
            COALESCE(item.length, 0) AS length,
            COALESCE(item.gsm, 0) AS gsm,
            CASE WHEN item.gsm < 100  THEN 3100 WHEN item.gsm >= 100 THEN 15500 ELSE 0 END AS factor,
            SUM(CASE WHEN sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) AS in_qty,
            '' AS in_rm_pkt,
            ABS(SUM(CASE WHEN sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END)) AS out_qty,
            '' AS out_rm_pkt,
            (SUM(CASE WHEN sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) - ABS(SUM(CASE WHEN sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END))) AS balance_qty,
            '' AS balance_rm_pkt ,
            (SELECT valuation_rate FROM `tabStock Ledger Entry` WHERE item_code = item.item_code ORDER BY posting_date DESC, posting_time DESC LIMIT 1) AS valuation_rate,
            ((SUM(CASE WHEN sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) - ABS(SUM(CASE WHEN sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END))) * (SELECT valuation_rate FROM `tabStock Ledger Entry` WHERE item_code = item.item_code ORDER BY posting_date DESC, posting_time DESC LIMIT 1))  AS amount
        FROM `tabItem` AS item, `tabStock Ledger Entry` AS sle
        WHERE
            item.name = sle.item_code 
            AND 
            {conditions} 
            AND sle.is_cancelled != 1
        GROUP BY item.item_code
        HAVING (SUM(CASE WHEN sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) - ABS(SUM(CASE WHEN sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END))) != 0
        ORDER BY item.item_code
    """

    stock_balance_result = frappe.db.sql(stock_balance_query, filters, as_dict=1)
    for i in stock_balance_result:
        factor = Decimal(i.factor)
        width = Decimal(i.width)
        length = Decimal(i.length)
        gsm = Decimal(i.gsm)

        in_qty = Decimal(i.in_qty)
        out_qty = Decimal(i.out_qty)
        balance_qty = Decimal(i.balance_qty)
        valuation_rate = Decimal(i.valuation_rate)

        i.in_rm_pkt = round(in_qty / ((width * length * gsm) / factor), 0 if gsm < 100 else 2) if i.item_group == 'Sheet' else 0
        i.out_rm_pkt = round(out_qty / ((width * length * gsm) / factor), 0 if gsm < 100 else 2) if i.item_group == 'Sheet' else 0
        i.balance_rm_pkt = round(balance_qty / ((width * length * gsm) / factor), 0 if gsm < 100 else 2) if i.item_group == 'Sheet' else 0
        i.amount = balance_qty * valuation_rate

    data.extend(stock_balance_result)
    return data

