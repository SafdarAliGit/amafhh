# Copyright (c) 2023, Tech Ventures and contributors
# For license information, please see license.txt
import frappe
# import frappe
from frappe.model.document import Document


class SheetToSheetConversion(Document):
    def validate(self):
        if self.source_weight != self.target_weight:
            frappe.throw("Total Source And Target Weight Should Be Same")
