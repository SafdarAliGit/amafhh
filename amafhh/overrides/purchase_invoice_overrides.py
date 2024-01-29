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
                batch.import_file = item.import_file
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
                product_item.import_file = item.import_file
                product_item.gsm = item.gsm
                product_item.ref_type = "Purchase Invoice"
                product_item.qty = item.qty
                try:
                    product_item.save()
                    # frappe.db.commit()
                except Exception as e:
                    frappe.throw(frappe._("Error Updating Item NO: {0}".format(str(e))))
