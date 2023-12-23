import frappe
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice


class PurchaseInvoiceOverrides(PurchaseInvoice):

    def on_submit(self):
        super(PurchaseInvoiceOverrides, self).on_submit()  # Corrected the super call
        for item in self.items:
            sr_no_doc = frappe.new_doc("SR NO")
            sr_no_doc.sr_no = item.sr_no
            sr_no_doc.item_code = item.item_code
            sr_no_doc.item_group = item.group
            sr_no_doc.brand = item.brand
            sr_no_doc.weight_total = item.qty
            sr_no_doc.weight_balance = item.qty
            sr_no_doc.rate = item.rate
            sr_no_doc.amount = item.amount
            sr_no_doc.ref_type = 'Purchase Invoice'
            sr_no_doc.ref_no = self.name
            sr_no_doc.supplier = self.supplier
            try:
                if item.sr_no:
                    sr_no_doc.save()
                    frappe.db.commit()
            except Exception as e:
                frappe.throw(frappe._("Error saving SR NO: {0}".format(str(e))))

    def before_submit(self):
        for item in self.items:
            batch = frappe.get_doc('Batch', item.batch_no)
            batch.rate = item.rate
            batch.amount = item.amount
            batch.ref_no = self.name
            batch.ref_type = "Purchase Invoice"
            try:
                batch.save()
                frappe.db.commit()
            except Exception as e:
                frappe.throw(frappe._("Error saving BATCH NO: {0}".format(str(e))))
