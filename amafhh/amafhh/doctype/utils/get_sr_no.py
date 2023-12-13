import frappe


@frappe.whitelist()
def get_sr_no(sr_no):
    data = {}
    sr_no_doc = frappe.get_doc("SR NO", sr_no)
    if sr_no_doc:
        data.update(
            {
                "item_code": sr_no_doc.item_code,
                "purchase_rate": sr_no_doc.purchase_rate,
                "purchase_amount": sr_no_doc.purchase_amount,
                "weight_balance": sr_no_doc.weight_balance,
            }
        )
        item = frappe.get_doc("Item", sr_no_doc.item_code)
        if item:
            data.update(
                {
                    "width": item.width,
                    "gsm": item.gsm,
                }
            )
        return data
    return None
