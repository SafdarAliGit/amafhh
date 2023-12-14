import frappe


@frappe.whitelist()
def get_sr_no(sr_no):
    data = {}
    sr_no_doc = frappe.get_doc("SR NO", sr_no)
    if sr_no_doc:
        data.update(
            {
                "item_code": sr_no_doc.item_code,
                "rate": sr_no_doc.rate,
                "amount": sr_no_doc.amount,
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
