import frappe
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice


class PurchaseInvoiceOverrides(PurchaseInvoice):

    def on_submit(self):
        super(PurchaseInvoiceOverrides, self).on_submit()  # Corrected the super call

    def before_submit(self):

        for item in self.items:
            if item.batch_no:
                batch = frappe.get_doc('Batch', item.batch_no)
                batch.rate = item.rate
                batch.amount = item.amount
                batch.item_group = item.item_group
                batch.ref_no = self.name
                batch.import_file = self.import_file
                batch.gsm = item.gsm
                batch.ref_type = "Purchase Invoice"
                try:
                    batch.save()
                    # frappe.db.commit()
                except Exception as e:
                    frappe.throw(frappe._("Error saving BATCH NO: {0}".format(str(e))))
            else:
                product_item = frappe.get_doc('Item', item.item_code)
                product_item.rate = item.rate
                product_item.amount = item.amount
                product_item.item_group = item.item_group
                product_item.ref_no = self.name
                product_item.import_file = self.import_file
                product_item.gsm = item.gsm
                product_item.ref_type = "Purchase Invoice"
                product_item.qty = item.qty
                try:
                    product_item.save()
                    # frappe.db.commit()
                except Exception as e:
                    frappe.throw(frappe._("Error Updating Item NO: {0}".format(str(e))))


def insert_import_file_to_stock_ledger_entry(doc, method):
    # Loop through items in the Purchase Invoice
    for item in doc.items:
        # Check if there's a related stock entry (this is a simplified example)
        stock_entries = frappe.get_list("Stock Ledger Entry", fields=["name"],
                                        filters={"voucher_detail_no": item.name})

        # Update Stock Ledger Entries with the import_file value from Purchase Invoice Item
        for entry in stock_entries:
            frappe.db.set_value("Stock Ledger Entry", entry.name, "import_file", item.import_file)

    frappe.db.commit()
