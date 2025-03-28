import frappe

def get_doctypes_by_field(doctype_name, field_name, field_value):
    """Fetch all matching documents based on a field filter."""
    return frappe.get_all(doctype_name, filters={field_name: field_value}, fields=["name", "docstatus", "amended_from"])