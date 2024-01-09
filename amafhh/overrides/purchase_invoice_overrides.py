import frappe
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice


class PurchaseInvoiceOverrides(PurchaseInvoice):

    def on_submit(self):
        super(PurchaseInvoiceOverrides, self).on_submit()  # Corrected the super call

    def before_submit(self):
        for item in self.items:
            batch = frappe.get_doc('Batch', item.batch_no)
            batch.rate = item.rate
            batch.amount = item.amount
            batch.item_group = item.item_group
            batch.ref_no = self.name
            batch.import_file = item.import_file
            batch.ref_type = "Purchase Invoice"
            try:
                batch.save()
                # frappe.db.commit()
            except Exception as e:
                frappe.throw(frappe._("Error saving BATCH NO: {0}".format(str(e))))
