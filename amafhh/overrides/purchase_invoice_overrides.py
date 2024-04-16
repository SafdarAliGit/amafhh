import frappe
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice


class PurchaseInvoiceOverrides(PurchaseInvoice):

    def on_submit(self):
        super(PurchaseInvoiceOverrides, self).on_submit()  # Corrected the super call

    def before_submit(self):
        # -----------START-------
        import_file = self.import_file
        pi = frappe.qb.DocType("Purchase Invoice")
        pii = frappe.qb.DocType("Purchase Invoice Item")
        pi_parent_query = (
            frappe.qb.from_(pi)
            .select(
                pi.posting_date,
                pi.supplier,
                pi.name.as_("voucher_no"),
                frappe.qb.functions("SUM", pii.qty).as_("qty"),
                frappe.qb.functions("AVG", pii.rate).as_("rate"),
                pi.grand_total.as_("amount")
            )
            .left_join(pii).on(pi.name == pii.parent)
            .where((pi.docstatus == 1) & (pi.import_file == import_file))
            .groupby(pi.name)
            .orderby(pi.posting_date)
        )
        pi_parent_query_result = pi_parent_query.run(as_dict=True)

        lcv = frappe.qb.DocType("Landed Cost Voucher")
        lctc = frappe.qb.DocType("Landed Cost Taxes and Charges")
        lcv_parent_query = (
            frappe.qb.from_(lcv)
            .select(
                lcv.posting_date,
                lctc.description.as_("qty"),
                lcv.name.as_("voucher_no"),
                lctc.expense_account.as_("supplier"),
                lctc.amount
            )
            .left_join(lctc).on(lcv.name == lctc.parent)
            .where((lcv.docstatus == 1) & (lcv.import_file == import_file))
        )

        lcv_parent_query_result = lcv_parent_query.run(as_dict=True)

        # -------------Purchase Invoice----------------
        total_purchase_qty = 0
        total_rate = 0
        total_purchase_amount = 0
        for purchase in pi_parent_query_result:
            total_purchase_qty += purchase.qty
            total_rate += purchase.rate
            total_purchase_amount += purchase.amount

        avg_purchase_rate = total_rate / len(pi_parent_query_result) if pi_parent_query_result else 0

        # -------------Landed Cost Voucher----------------
        total_lc_amount = sum(lcr.amount for lcr in lcv_parent_query_result)

        total_cost = total_purchase_amount + total_lc_amount
        avg_rate_with_lc = total_cost / total_purchase_qty if total_purchase_qty != 0 else 0

        imp_file = frappe.get_doc("Import File", import_file)

        imp_file.total_purchase_qty = round(total_purchase_qty, 2)
        imp_file.avg_purchase_rate = round(avg_purchase_rate, 2)
        imp_file.total_purchase_amount = round(total_purchase_amount, 2)
        imp_file.total_lc_amount = round(total_lc_amount, 2)
        imp_file.total_cost =  round(total_cost, 2)
        imp_file.avg_rate_with_lc = round(avg_rate_with_lc, 2)
        imp_file.save()

        # ----------END----------
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
