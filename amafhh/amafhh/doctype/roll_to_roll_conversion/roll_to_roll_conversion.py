# Copyright (c) 2023, Tech Ventures and contributors
# For license information, please see license.txt
import frappe
# import frappe
from frappe.model.document import Document

class RollToRollConversion(Document):
	def on_submit(self):
		super(RollToRollConversion, self).save()
		for item in self.roll_to_roll_conversion_target:
			sr_no_doc = frappe.new_doc("SR NO")
			sr_no_doc.sr_no = item.sr_no
			sr_no_doc.item_code = item.item_code
			sr_no_doc.weight_total = item.weightkg
			sr_no_doc.weight_balance = item.weightkg
			sr_no_doc.rate = item.rate
			sr_no_doc.amount = item.amount
			sr_no_doc.ref_type = 'Roll To Roll Conversion'
			sr_no_doc.ref_no = self.name
			sr_no_doc.save()
			frappe.db.commit()
