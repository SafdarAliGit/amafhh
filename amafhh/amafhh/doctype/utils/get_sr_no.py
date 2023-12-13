import frappe


@frappe.whitelist()
def get_sr_no(sr_no):
    sr_no_doc = frappe.get_doc("SR NO", sr_no)
    if sr_no_doc:
        return sr_no_doc
    return None
