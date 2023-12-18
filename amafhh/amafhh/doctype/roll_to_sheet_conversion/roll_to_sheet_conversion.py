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
        for item in self.roll_to_sheet_conversion_target:
            batch = frappe.new_doc("Batch")
            batch.item = item.item_code
            batch.batch_id = item.batch_no
            batch.batch_qty = 10
            try:
                batch.save()
                frappe.db.commit()
            except Exception as e:
                    frappe.throw(_("Error saving BATCH NO: {0}".format(str(e))))

        # STOCK ENTRY SAVING
        doc = frappe.new_doc("Stock Entry")
        doc.stock_entry_type = "Repack"
        doc.purpose = "Repack"
        doc.posting_date = nowdate()
        source_warehouse = self.warehouse

        # Append source item
        doc.append("items", {
            "s_warehouse": source_warehouse,
            "item_code": self.roll_to_sheet_conversion_source[0].item_code,
            "qty": self.roll_to_sheet_conversion_source[0].weightkg,
            "set_basic_rate_manually": 1,
            "basic_rate": self.roll_to_sheet_conversion_source[0].rate,
            "amount": self.roll_to_sheet_conversion_source[0].amount,
        })

        # Append target items using a loop
        for item in self.roll_to_sheet_conversion_target:
            doc.append("items", {
                "t_warehouse": source_warehouse,
                "item_code": item.item_code,
                "qty": item.weightkg,
                "set_basic_rate_manually": 1,
                "basic_rate": item.rate,
                "amount": item.amount,
                "batch_no": item.batch_no
            })
        try:
            doc.submit()
            frappe.db.commit()
        except Exception as e:
            throw(_("Error submitting Stock Entry: {0}".format(str(e))))
