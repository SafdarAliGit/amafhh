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
            "label": "<b>PRODUCT CATEGORY</b>",
            "fieldname": "item_category",
            "fieldtype": "Data",
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
            "label": "<b>WAREHOUSE</b>",
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 120
        },
        {
            "label": "<b>STOCK QTY</b>",
            "fieldname": "stock_qty",
            "fieldtype": "Float",
            "width": 80
        },
        {
            "label": "<b>RATE</b>",
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": "<b>KG AMOUNT</b>",
            "fieldname": "kg_amount",
            "fieldtype": "Currency",
            "width": 120
        }
    ]
    return columns

def get_warehouse_condition(filters):
    """Returns the appropriate warehouse filtering condition for the SQL query."""
    if not filters.get("warehouse"):
        return ""  # No warehouse filter applied

    warehouse = filters["warehouse"]
    is_group = frappe.get_value("Warehouse", warehouse, "is_group")

    if is_group:
        # Fetch all subgroup warehouses recursively
        warehouses = get_child_warehouses(warehouse)  
        warehouses.append(warehouse)  # Include the group warehouse itself
        
        # Convert warehouse list to a proper SQL `IN` format
        warehouse_list = ", ".join(f"'{w}'" for w in warehouses)
        return f"AND sle.warehouse IN ({warehouse_list})"
    else:
        return "AND sle.warehouse = %(warehouse)s"


def get_child_warehouses(parent_warehouse):
    """Recursively fetch all child warehouses under a given warehouse."""
    child_warehouses = frappe.get_all(
        "Warehouse", filters={"parent_warehouse": parent_warehouse}, pluck="name"
    )

    # Recursively fetch sub-child warehouses
    for child in child_warehouses:
        child_warehouses.extend(get_child_warehouses(child))

    return child_warehouses

def get_conditions(filters):
    conditions = []
    
    if filters.get("brand_item"):
        conditions.append("AND item.brand_item = %(brand_item)s")
    if filters.get("import_file"):
        conditions.append("AND item.import_file = %(import_file)s")
    if filters.get("item_code"):
        conditions.append("AND sle.item_code = %(item_code)s")
    if filters.get("to_date"):
        conditions.append("AND sle.posting_date <= %(to_date)s")
    
    # Handle warehouse condition dynamically
    if filters.get("warehouse"):
        warehouse_condition = get_warehouse_condition(filters)
        conditions.append(warehouse_condition)  # Use the warehouse filtering function

    return " ".join(conditions)



def get_data(filters):
    data = []
    conditions = get_conditions(filters)
    warehouse_condition = get_warehouse_condition(filters)

    stock_balance_query = f"""
    SELECT 
        item.item_category, 
        item.brand_item, 
        item.import_file, 
        SUM(( SELECT actual_qty
            FROM `tabStock Ledger Entry` AS sle
            WHERE sle.item_code = item.item_code
              AND sle.is_cancelled = 0
            ORDER BY sle.posting_date DESC
            LIMIT 1)) AS stock_qty,
        (
            SELECT warehouse
            FROM `tabStock Ledger Entry` AS sle
            WHERE sle.item_code = item.item_code
                AND sle.is_cancelled = 0
                {warehouse_condition}
                {f"AND sle.posting_date <= %(to_date)s" if filters.get("to_date") else ""}
            ORDER BY sle.posting_date DESC, sle.posting_time DESC
            LIMIT 1
        ) AS warehouse,
        COALESCE((SELECT avg_rate_with_lc FROM `tabImport File` WHERE name = item.import_file),0) AS rate,
        0 AS kg_amount
    FROM `tabItem` AS item
    JOIN `tabStock Ledger Entry` AS sle ON item.name = sle.item_code
    WHERE
        sle.is_cancelled = 0
        {conditions}
    GROUP BY item.item_category
    HAVING stock_qty > {f"%(stock_limit)s" if filters.get("stock_limit") else 0}
    ORDER BY item.item_category
        """

    stock_balance_result = frappe.db.sql(stock_balance_query, filters, as_dict=1)
    for i in stock_balance_result:
        try:
            stock_qty = float(i.stock_qty)
            i.kg_amount = round(stock_qty * i.rate, 3)
        except decimal.InvalidOperation as e:
            frappe.log_error(f"Invalid value encountered: {e}")
            continue
    data.extend(stock_balance_result)
    return data
