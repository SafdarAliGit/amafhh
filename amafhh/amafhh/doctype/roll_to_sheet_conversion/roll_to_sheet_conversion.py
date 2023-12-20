# Copyright (c) 2023, Tech Ventures and contributors
# For license information, please see license.txt
import frappe
# import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from frappe import _, throw


class RollToSheetConversion(Document):
    def on_submit(self):
        super(RollToSheetConversion, self).save()
        # CREATING BATCH NO
        # for item in self.roll_to_sheet_conversion_target:
        #     batch = frappe.new_doc("Batch")
        #     batch.item = item.item_code
        #     batch.batch_id = item.batch_no
        #     batch.batch_qty = 10
        #     try:
        #         batch.save()
        #         frappe.db.commit()
        #     except Exception as e:
        #             frappe.throw(_("Error saving BATCH NO: {0}".format(str(e))))

        # STOCK ENTRY SAVING


        # Append target items using a loop
        for item in self.roll_to_sheet_conversion_items:
            doc = frappe.new_doc("Stock Entry")
            doc.stock_entry_type = "Repack"
            doc.purpose = "Repack"
            doc.posting_date = nowdate()
            source_warehouse = self.warehouse
            target_warehouse = None
            if item.stock_type_source == "Finished":
                target_warehouse = 'Finished Goods - A'
            elif item.stock_type_source == "Semi-Finished":
                target_warehouse = 'Goods In Transit - A'
            elif item.stock_type_source == "Damaged":
                target_warehouse = 'Damaged - A'

            doc.append("items", {
                "s_warehouse": source_warehouse,
                "t_warehouse": "",
                "item_code": item.item_code_source,
                "qty": item.weight_target,
                "basic_rate": item.rate,
                "amount": item.amount
            })
            doc.append("items", {
                "s_warehouse": "",
                "t_warehouse": target_warehouse,
                "item_code": item.item_code_target,
                "qty": item.weight_target,
                "basic_rate": item.rate,
                "amount": item.amount
            })
            try:
                # doc.ignore_validate = True
                doc.submit()
                frappe.db.commit()
            except Exception as e:
                throw(_("Error submitting Stock Entry: {0}".format(str(e))))
