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
        for item in self.roll_to_sheet_conversion_items:
            batch = frappe.new_doc("Batch")
            batch.item = item.item_code_target
            batch.batch_id = item.batch_no_target
            batch.batch_qty = item.weight_target
            batch.rate = item.rate
            batch.amount = item.amount
            batch.ref_no = self.name
            batch.ref_type = "Roll To Sheet Conversion"
            try:
                batch.save()
                frappe.db.commit()
            except Exception as e:
                frappe.throw(frappe._("Error saving BATCH NO: {0}".format(str(e))))

        # Append target items using a loop
        for item in self.roll_to_sheet_conversion_items:
            doc = frappe.new_doc("Stock Entry")
            doc.stock_entry_type = "Repack"
            doc.purpose = "Repack"
            doc.sr_no = item.sr_no
            doc.posting_date = nowdate()
            doc.roll_to_sheet_conversion = self.name
            source_warehouse = self.warehouse
            target_warehouse = None
            if item.stock_type_target == "Finished":
                target_warehouse = 'Finished Goods - A'
            elif item.stock_type_target == "Semi-Finished":
                target_warehouse = 'Goods In Transit - A'
            elif item.stock_type_target == "Damaged":
                target_warehouse = 'Damaged - A'

            doc.append("items", {
                "s_warehouse": source_warehouse,
                "t_warehouse": "",
                "item_code": item.item_code_source,
                "qty": item.weight_target,
                "basic_rate": item.rate,
                "amount": item.amount,
                "sr_no": item.sr_no
            })
            doc.append("items", {
                "s_warehouse": "",
                "t_warehouse": target_warehouse,
                "item_code": item.item_code_target,
                "qty": item.weight_target,
                "basic_rate": item.rate,
                "amount": item.amount,
                "sr_no": item.sr_no
            })
            try:
                # doc.ignore_validate = True
                doc.submit()
                self.stock_entry = doc.name
                self.save()
                frappe.db.commit()
            except Exception as e:
                throw(_("Error submitting Stock Entry: {0}".format(str(e))))
