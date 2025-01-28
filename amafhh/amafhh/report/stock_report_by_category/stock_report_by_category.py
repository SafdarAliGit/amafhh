import frappe



def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "label": "<b>ITEM CODE</b>",
            "fieldname": "item_category",
            "fieldtype": "Data",
            "width": 120

        },
        {
            "label": "<b>QTY</b>",
            "fieldname": "stock_qty",
            "fieldtype": "Float",
            "width": 100

        },
        {
            "label": "<b>STOCK VALUE</b>",
            "fieldname": "stock_value",
            "fieldtype": "Currency",
            "width": 120
        }

    ]
    return columns


def get_data(filters):
    data = []

    stock_balance_query = f"""
        SELECT 
            item.item_category,
            SUM((
                SELECT sle.qty_after_transaction
                FROM `tabStock Ledger Entry` AS sle
                WHERE sle.item_code = item.item_code
                    AND sle.is_cancelled = 0
                    {f" AND sle.warehouse = %(warehouse)s" if filters.get("warehouse") else ""}
                    {f" AND sle.posting_date >= %(from_date)s" if filters.get("from_date") else ""}
                    {f" AND sle.posting_date <= %(to_date)s" if filters.get("to_date") else ""}
                ORDER BY sle.posting_date DESC, sle.posting_time DESC
                LIMIT 1
            )) AS stock_qty,
            SUM((
                SELECT sle.stock_value
                FROM `tabStock Ledger Entry` AS sle
                WHERE sle.item_code = item.item_code
                    AND sle.is_cancelled = 0
                    {f" AND sle.warehouse = %(warehouse)s" if filters.get("warehouse") else ""}
                    {f" AND sle.posting_date >= %(from_date)s" if filters.get("from_date") else ""}
                    {f" AND sle.posting_date <= %(to_date)s" if filters.get("to_date") else ""}
                ORDER BY sle.posting_date DESC, sle.posting_time DESC
                LIMIT 1
            )) AS stock_value
            
        FROM `tabItem` AS item
        GROUP BY item.item_category
    """

    stock_balance_result = frappe.db.sql(stock_balance_query, filters, as_dict=1)

    data.extend(stock_balance_result)
    return data
