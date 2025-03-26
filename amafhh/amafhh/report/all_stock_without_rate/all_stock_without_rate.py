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
            "label": "<b>WAREHOUSE</b>",
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
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
        conditions.append(f"AND item.brand_item = %(brand_item)s")
    if filters.get("import_file"):
        conditions.append(f"AND item.import_file = %(import_file)s")
    if filters.get("item_code"):
        conditions.append(f"AND sle.item_code = %(item_code)s")
    if filters.get("to_date"):
        conditions.append(f"AND sle.posting_date <= %(to_date)s")
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
                item.brand_item,
                item.import_file,
                item.item_code,
                item.stock_uom,
                item.item_group,
                COALESCE(item.width, 0) AS width,
                COALESCE(item.length, 0) AS length,
                COALESCE(item.gsm, 0) AS gsm,
                CASE WHEN item.gsm < 100  THEN 3100 WHEN item.gsm >= 100 THEN 15500 ELSE 0 END AS factor,
                (SELECT actual_qty
                FROM `tabStock Ledger Entry` AS sle
                WHERE sle.item_code = item.item_code
                ORDER BY sle.posting_date DESC
                LIMIT 1) AS stock_qty,
                0 AS packet,
                (
                    SELECT warehouse
                    FROM `tabStock Ledger Entry` AS sle
                    WHERE sle.item_code = item.item_code
                        AND sle.is_cancelled = 0
                        {warehouse_condition}
                        {f"AND sle.posting_date <= %(to_date)s" if filters.get("to_date") else ""}
                    ORDER BY sle.posting_date DESC, sle.posting_time DESC
                    LIMIT 1
                ) AS warehouse
            FROM `tabItem` AS item
            JOIN `tabStock Ledger Entry` AS sle ON item.name = sle.item_code
            WHERE
                sle.is_cancelled = 0
                {conditions}
            HAVING stock_qty > {f"%(stock_limit)s" if filters.get("stock_limit") else 0}
            ORDER BY item.brand_item
        """

    stock_balance_result = frappe.db.sql(stock_balance_query, filters, as_dict=1)
    for i in stock_balance_result:
        try:
            factor = Decimal(i.factor)
            width = Decimal(i.width)
            length = Decimal(i.length)
            gsm = Decimal(i.gsm)
            stock_qty = Decimal(i.stock_qty)
            i.packet = round(stock_qty / ((width * length * gsm) / factor), 0 if gsm < 100 else 2) if i.item_group == 'Sheet' else 0
        except decimal.InvalidOperation as e:
            frappe.log_error(f"Invalid value encountered: {e}")
            continue
    data.extend(stock_balance_result)
    return data
