import frappe


@frappe.whitelist()
def get_by_item_code(item_code):
    data = {}
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
                "weight_balance": float(item.qty)  if item.qty else 0,
                "import_file": item.import_file
            }
        )
        return data
    else:
        frappe.throw("Item not found")


