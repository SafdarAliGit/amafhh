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
            "width": 180
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
        },
        {
            "label": "<b>WAREHOUSE</b>",
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 120
        }
    ]


def get_conditions(filters):
    conditions = []
    filters = filters.copy()  # Prevent modifying the original

    if filters.get("item_code"):
        conditions.append("AND sle.item_code = %(item_code)s")

    if filters.get("to_date"):
        conditions.append("AND sle.posting_date <= %(to_date)s")

    if filters.get("warehouse"):
        warehouse = filters.get("warehouse")
        is_group = frappe.db.get_value("Warehouse", warehouse, "is_group")

        if is_group:
            # Get all child warehouses (including the group itself)
            warehouse_doc = frappe.get_doc("Warehouse", warehouse)
            warehouses = frappe.get_all(
                "Warehouse",
                filters={
                    "lft": [">=", warehouse_doc.lft],
                    "rgt": ["<=", warehouse_doc.rgt]
                },
                pluck="name"
            )
            if warehouses:
                conditions.append("AND sle.warehouse IN %(warehouses)s")
                filters["warehouses"] = tuple(warehouses)
        else:
            conditions.append("AND sle.warehouse = %(warehouse)s")

    return " ".join(conditions), filters


def get_data(filters):
    data = []
    condition_str, filters = get_conditions(filters)

    stock_balance_query = f"""
        SELECT 
            item.item_category, 
            AVG(COALESCE((
                SELECT valuation_rate
                FROM `tabStock Ledger Entry` AS sle_sub
                WHERE sle_sub.item_code = item.item_code
                  AND sle_sub.is_cancelled = 0
                  {condition_str}
                ORDER BY sle_sub.posting_date DESC, sle_sub.posting_time DESC
                LIMIT 1
            ), 0)) AS rate,
            SUM(CASE WHEN sle.is_cancelled = 0 THEN sle.actual_qty ELSE 0 END) AS stock_qty,
            sle.warehouse
        FROM `tabItem` AS item
        LEFT JOIN `tabStock Ledger Entry` AS sle ON item.name = sle.item_code
        WHERE EXISTS (
            SELECT 1
            FROM `tabStock Ledger Entry` AS sle_exists
            WHERE sle_exists.item_code = item.item_code
              AND sle_exists.is_cancelled = 0
              {condition_str}
        )
        GROUP BY item.item_category
        HAVING stock_qty > %(stock_limit)s
        ORDER BY item.item_category
    """

    # Ensure stock_limit has a default
    filters["stock_limit"] = filters.get("stock_limit", 0)

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