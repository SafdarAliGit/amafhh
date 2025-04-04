import frappe
from frappe import _
from decimal import Decimal, InvalidOperation

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "label": "<b>PRODUCT CATEGORY</b>",
            "fieldname": "item_category",
            "fieldtype": "Data",
            "width": 150
        },

        {
            "label": "<b>STOCK QTY</b>",
            "fieldname": "stock_qty",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": "<b>RATE</b>",
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "<b>KG AMOUNT</b>",
            "fieldname": "kg_amount",
            "fieldtype": "Currency",
            "width": 140
        }
    ]


def get_conditions(filters):
    conditions = []

    if filters.get("item_code"):
        conditions.append("AND sle.item_code = %(item_code)s")
    if filters.get("to_date"):
        conditions.append("AND sle.posting_date <= %(to_date)s")
    
    return " ".join(conditions)

def get_data(filters):
    data = []
    conditions = get_conditions(filters)

    stock_balance_query = f"""
    SELECT 
        item.item_category, 
        AVG(COALESCE((
            SELECT valuation_rate
            FROM `tabStock Ledger Entry` AS sle
            WHERE sle.item_code = item.item_code
              AND sle.is_cancelled = 0
              {conditions}
            ORDER BY sle.posting_date DESC, sle.posting_time DESC
            LIMIT 1
        ), 0)) AS rate,
        SUM(CASE WHEN sle.is_cancelled = 0 THEN sle.actual_qty ELSE 0 END) AS stock_qty
    FROM `tabItem` AS item
    LEFT JOIN `tabStock Ledger Entry` AS sle ON item.name = sle.item_code
    WHERE EXISTS (
        SELECT 1
        FROM `tabStock Ledger Entry` AS sle
        WHERE sle.item_code = item.item_code
          AND sle.is_cancelled = 0
          {conditions}
    )
    GROUP BY item.item_category
    HAVING stock_qty > {filters.get("stock_limit", 0)}
    ORDER BY item.item_category
    """

    stock_balance_result = frappe.db.sql(stock_balance_query, filters, as_dict=1)
    for entry in stock_balance_result:
        try:
            stock_qty = Decimal(entry.get("stock_qty") or 0)
            rate = Decimal(entry.get("rate") or 0)
            entry["kg_amount"] = round(stock_qty * rate, 3)
        except InvalidOperation as e:
            frappe.log_error(f"Invalid value encountered during calculation: {e}")
            entry["kg_amount"] = 0
    data.extend(stock_balance_result)
    return data
