# Copyright (c) 2023, Tech Ventures and contributors
# For license information, please see license.txt
import frappe
# import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from frappe import _, throw


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
			try:
				sr_no_doc.save()
				frappe.db.commit()
			except Exception as e:
				frappe.throw(_("Error saving SR NO: {0}".format(str(e))))
		# STOCK ENTRY SAVING
		doc = frappe.new_doc("Stock Entry")
		doc.stock_entry_type = "Repack"
		doc.purpose = "Repack"
		doc.posting_date = nowdate()
		source_warehouse = self.warehouse

		# Append source item
		doc.append("items", {
			"s_warehouse": source_warehouse,
			"t_warehouse":"",
			"item_code": self.roll_to_roll_conversion_source[0].item_code,
			"qty": self.roll_to_roll_conversion_source[0].weightkg,
			"set_basic_rate_manually": 1,
			"basic_rate": self.roll_to_roll_conversion_source[0].rate,
			"amount": self.roll_to_roll_conversion_source[0].amount
		})

		# Append target items using a loop
		for item in self.roll_to_roll_conversion_target:
			doc.append("items", {
				"s_warehouse":"",
				"t_warehouse": source_warehouse,
				"item_code": item.item_code,
				"qty": item.weightkg,
				"set_basic_rate_manually": 1,
				"basic_rate": item.rate,
				"amount": item.amount
			})
		try:
			doc.submit()
			frappe.db.commit()
		except Exception as e:
			frappe.throw(_("Error submitting Stock Entry: {0}".format(str(e))))
