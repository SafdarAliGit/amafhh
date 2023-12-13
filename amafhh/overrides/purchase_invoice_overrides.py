import frappe
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice


# form_grid_templates = {"items": "templates/form_grid/item_grid.html"}


class PurchaseInvoiceOverrides(PurchaseInvoice):

    def save(self):
        super(PurchaseInvoiceOverrides, self).save()
        for item in self.items:
            sr_no_doc = frappe.new_doc("SR NO")
            sr_no_doc.sr_no = item.sr_no
            sr_no_doc.item_code = item.item_code
            sr_no_doc.weight_total = item.qty
            sr_no_doc.weight_balance = item.qty
            sr_no_doc.purchase_rate = item.rate
            sr_no_doc.purchase_amount= item.amount
            sr_no_doc.save()
            frappe.db.commit()

