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
            }
        )
        return data
    else:
        frappe.throw("Item not found")


