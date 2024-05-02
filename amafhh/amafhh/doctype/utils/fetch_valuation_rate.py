import frappe


@frappe.whitelist()
def fetch_valuation_rate(**args):
    item_code = args.get('item_code')
    data = {}
    # Construct the SQL query
    sql_query = """
        SELECT
            ROUND(valuation_rate,4) AS valuation_rate
        FROM
            `tabStock Ledger Entry`
        WHERE
            item_code = %s AND is_cancelled = 0
        ORDER BY
            posting_date DESC, posting_time DESC
        LIMIT 1
    """
    stock = frappe.get_all(
        "Stock Ledger Entry",
        filters={"item_code": item_code,"is_cancelled": 0},
        fields=["qty_after_transaction"],
        order_by="name desc",
        limit=1
    )
    if stock:
        data.update(
            {
                "weight_balance": float(stock[0].qty_after_transaction) if stock[0].qty_after_transaction else 0
            }
        )
    # Execute the query
    result = frappe.db.sql(sql_query, (item_code,), as_dict=True)

    # Access the result
    valuation_rate = None
    if result:
        valuation_rate = result[0].get('valuation_rate')
        data.update(
            {
                "valuation_rate": valuation_rate
            }
        )

    return data




