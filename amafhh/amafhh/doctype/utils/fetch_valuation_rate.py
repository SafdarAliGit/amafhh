import frappe


@frappe.whitelist()
def fetch_valuation_rate(**args):
    item_code = args.get('item_code')

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

    return {
        "valuation_rate": valuation_rate,
    }




