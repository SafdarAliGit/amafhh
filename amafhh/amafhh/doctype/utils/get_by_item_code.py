import frappe


@frappe.whitelist()
def get_by_item_code(item_code):
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

    # Execute the query
    result = frappe.db.sql(sql_query, (item_code,), as_dict=True)

    # Access the result
    valuation_rate = None
    if result:
        valuation_rate = result[0].get('valuation_rate')

    stock = frappe.get_all(
        "Stock Ledger Entry",
        filters={"item_code": item_code, "qty_after_transaction": [">", 0]},
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

    item = frappe.get_doc("Item", item_code)
    if valuation_rate:
        data.update(
            {
                "valuation_rate": valuation_rate
            }
        )

    if item:
        data.update(
            {
                "width": item.width,
                "gsm": item.gsm,
                "length": item.length,
                "item_code": item.item_code,
                "rate": item.rate,
                "amount": item.amount,
                "import_file": item.import_file
            }
        )
        return data
    else:
        frappe.throw("Item not found")


