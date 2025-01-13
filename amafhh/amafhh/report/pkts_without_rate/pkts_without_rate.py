import decimal

import frappe
from frappe import _
from decimal import Decimal


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "label": "<b>PRODUCT NAME</b>",
            "fieldname": "brand_item",
            "fieldtype": "Link",
            "options": "Brand",
            "width": 120
        },
        {
            "label": "<b>Lc No</b>",
            "fieldname": "import_file",
            "fieldtype": "Link",
            "options": "Import File",
            "width": 100
        },
        {
            "label": "<b>SERIAL NO</b>",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": "<b>UNIT</b>",
            "fieldname": "stock_uom",
            "fieldtype": "Data",
            "width": 80
        },
        {
            "label": "<b>STOCK QTY</b>",
            "fieldname": "stock_qty",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": "<b>PACKET</b>",
            "fieldname": "packet",
            "fieldtype": "Float",
            "width": 120

        }
    ]
    return columns


def get_conditions(filters):
    conditions = []
    if filters.get("brand_item"):
        conditions.append(f"AND item.brand_item = %(brand_item)s")
    if filters.get("import_file"):
        conditions.append(f"AND item.import_file = %(import_file)s")
    if filters.get("item_code"):
        conditions.append(f"AND sle.item_code = %(item_code)s")
    if filters.get("warehouse"):
        conditions.append(f"AND sle.warehouse = %(warehouse)s")
    if filters.get("to_date"):
        conditions.append(f"AND sle.posting_date <= %(to_date)s")
    return " ".join(conditions)


def get_data(filters):
    data = []
    conditions = get_conditions(filters)

    stock_balance_query = f"""
        SELECT DISTINCT 
    item.brand_item,
    item.import_file,
    item.item_code,
    item.stock_uom,
    item.item_group,
    COALESCE(item.width, 0) AS width,
    COALESCE(item.length, 0) AS length,
    COALESCE(item.gsm, 0) AS gsm,
    CASE 
        WHEN item.gsm < 100 THEN 3100 
        WHEN item.gsm >= 100 THEN 15500 
        ELSE 0 
    END AS factor,
    (
        SELECT qty_after_transaction
        FROM `tabStock Ledger Entry` AS sle_sub
        WHERE sle_sub.item_code = item.item_code 
            AND sle_sub.qty_after_transaction > 1 
            AND sle_sub.is_cancelled = 0
            {f"AND sle_sub.warehouse = %(warehouse)s" if filters.get("warehouse") else ""}
        ORDER BY sle_sub.posting_date DESC, sle_sub.posting_time DESC
        LIMIT 1
    ) AS stock_qty,
    0 AS packet
    FROM `tabItem` AS item
    WHERE
        item.item_group = 'Sheet'
        AND EXISTS (
            SELECT 1 
            FROM `tabStock Ledger Entry` AS sle
            WHERE sle.item_code = item.item_code
                AND sle.qty_after_transaction > 1
                AND sle.is_cancelled = 0
                {f"AND sle.warehouse = %(warehouse)s" if filters.get("warehouse") else ""}
        )
    HAVING stock_qty != 0
    ORDER BY item.brand_item;
    """

    stock_balance_result = frappe.db.sql(stock_balance_query, filters, as_dict=1)
    for i in stock_balance_result:
        try:
            factor = Decimal(i.factor)
            width = Decimal(i.width)
            length = Decimal(i.length)
            gsm = Decimal(i.gsm)
            stock_qty = Decimal(i.stock_qty)

            # Check for zero values in divisor components
            if width > 0 and length > 0 and gsm > 0 and factor > 0:
                i.packet = round(stock_qty / ((width * length * gsm) / factor),
                                 0 if gsm < 100 else 2) if i.item_group == 'Sheet' else 0
            else:
                i.packet = 0  # Set to 0 if division cannot be performed safely
        except decimal.InvalidOperation as e:
            frappe.log_error(f"Invalid value encountered: {e}")
            continue
    data.extend(stock_balance_result)
    return data

