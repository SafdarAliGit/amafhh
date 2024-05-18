import frappe
from frappe import _

import frappe
from frappe import _


@frappe.whitelist()
def update_import_file_in_sle():
    # Fetch all items with the 'import_file' field
    items = frappe.get_all("Item", fields=["name", "import_file"])

    for item in items:
        # Get all related stock ledger entries for the item
        stock_entries = frappe.get_list("Stock Ledger Entry", fields=["name"], filters={"voucher_detail_no": item.name})

        # Update Stock Ledger Entries with the import_file value from the item
        for entry in stock_entries:
            frappe.db.set_value("Stock Ledger Entry", entry.name, "import_file", item["import_file"])

    frappe.db.commit()
    return _("Stock Ledger Entries updated successfully.")