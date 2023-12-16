# Copyright (c) 2023, Tech Ventures and contributors
# For license information, please see license.txt
import frappe
# import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from frappe import _, throw


class RollToSheetConversion(Document):
    def validate(self):
        # Add any validation checks here if needed
        pass

    def on_submit(self):
        super(RollToSheetConversion, self).save()
        self.create_stock_entry()

    def create_stock_entry(self):
        doc = frappe.new_doc("Stock Entry")
        doc.stock_entry_type = "Repack"
        doc.posting_date = nowdate()
        source_warehouse = self.warehouse

        it = doc.append("items", {
            "s_warehouse": source_warehouse,
            "item_code": self.roll_to_sheet_conversion_source[0].item_code,
            "qty": self.roll_to_sheet_conversion_source[0].weightkg,
            "basic_rate": self.roll_to_sheet_conversion_source[0].rate,
            "amount": self.roll_to_sheet_conversion_source[0].amount
        })

        for item in self.roll_to_sheet_conversion_target:
            it = doc.append("items", {
                "t_warehouse": source_warehouse,
                "item_code": item.item_code,
                "qty": item.weightkg,
                "basic_rate": item.rate,
                "amount": item.amount
            })

        try:
            doc.submit()
            frappe.db.commit()
        except Exception as e:
            throw(_("Error submitting Stock Entry: {0}".format(str(e))))
