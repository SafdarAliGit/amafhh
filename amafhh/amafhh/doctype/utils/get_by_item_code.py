import frappe


@frappe.whitelist()
def get_by_item_code(item_code):
    data = {}
    stock = frappe.get_all(
        "Stock Ledger Entry",
        filters={"item_code": item_code},
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


