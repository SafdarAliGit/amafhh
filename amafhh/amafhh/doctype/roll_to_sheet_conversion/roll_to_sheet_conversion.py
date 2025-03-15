# Copyright (c) 2023, Tech Ventures and contributors
# For license information, please see license.txt
import frappe
# import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from frappe import _, throw
from amafhh.amafhh.doctype.utils_functions import get_doctypes_by_field
from frappe.model.naming import make_autoname


class RollToSheetConversion(Document):


    def on_submit(self):
        # super(RollToSheetConversion, self).save()
        # CREATING BATCH NO
        for item in self.roll_to_sheet_conversion_items:
            product_item = frappe.new_doc("Item")
            if item.batch_no_target:
                product_item.has_batch_no = 1
            product_item.item_code = item.item_code_target
            product_item.item_name = item.item_code_target
            product_item.item_group = 'Sheet'
            product_item.gsm = item.gsm_source
            product_item.width = item.width_target
            product_item.length = item.length_target
            product_item.stock_uom = 'Kg'
            product_item.is_stock_item = 1
            product_item.rate = item.rate
            product_item.amount = item.amount
            product_item.qty = item.weight_target
            product_item.import_file = item.import_file
            product_item.ref_no = self.name
            product_item.ref_type = "Roll To Sheet Conversion"
            product_item.item_category = item.item_category if item.item_category else ""
            product_item.brand_item = item.brand if item.brand else ""
            product_item.valuation_rate = item.rate
            try:
                product_item.save()
                # frappe.db.commit()
            except Exception as e:
                frappe.throw(frappe._("Error saving Item: {0}".format(str(e))))

            if item.batch_no_target:
                batch = frappe.new_doc("Batch")
                batch.item = item.item_code_target
                batch.batch_id = item.batch_no_target
                batch.batch_qty = item.weight_target
                batch.rate = item.rate
                batch.amount = item.amount
                batch.ref_no = self.name
                batch.item_group = 'Sheet'
                batch.ream_pkt_target = item.ream_pkt_target
                batch.gsm = item.gsm_source
                batch.import_file = item.import_file
                batch.ref_type = "Roll To Sheet Conversion"
                try:
                    batch.save()
                    # frappe.db.commit()
                except Exception as e:
                    frappe.throw(frappe._("Error saving BATCH NO: {0}".format(str(e))))

        # Append target items using a loop
        for item in self.roll_to_sheet_conversion_items:
            doc = frappe.new_doc("Stock Entry")
            doc.stock_entry_type = "Repack"
            doc.purpose = "Repack"
            if item.batch_no_target:
                doc.batch_no = item.batch_no_target
            doc.set_posting_time = 1
            doc.posting_date = self.posting_date
            doc.posting_time = self.posting_time
            doc.roll_to_sheet_conversion = self.name
            source_warehouse = self.warehouse
            target_warehouse = None
            if item.stock_type_target == "Finished":
                target_warehouse = 'Finished Goods - A'
            elif item.stock_type_target == "Semi-Finished":
                target_warehouse = 'Goods In Transit - A'
            elif item.stock_type_target == "Damaged":
                target_warehouse = 'Damaged - A'
            elif item.stock_type_target == "Non-Physical":
                target_warehouse = 'Non Fisical Damage - A'

            doc.append("items", {
                "set_basic_rate_manually": 1,
                "s_warehouse": source_warehouse,
                "t_warehouse": "",
                "item_code": item.item_code_source,
                "qty": item.weight_target,
                "valuation_rate": item.rate,
                "basic_rate": item.rate,
                "amount": item.amount,
                "batch_no": item.batch_no_source if item.batch_no_target else None
            })
            doc.append("items", {
                "set_basic_rate_manually": 1,
                "s_warehouse": "",
                "t_warehouse": target_warehouse,
                "item_code": item.item_code_target,
                "qty": item.weight_target,
                "valuation_rate": item.rate,
                "basic_rate": item.rate,
                "amount": item.amount,
                "batch_no": item.batch_no_target if item.batch_no_target else None,
                "ream_pkt": item.ream_pkt_target if item.ream_pkt_target else None
            })
            try:
                # doc.ignore_validate = True
                doc.submit()
                self.stock_entry = doc.name
                self.save()
                # frappe.db.commit()
            except Exception as e:
                throw(_("Error submitting Stock Entry: {0}".format(str(e))))


    def on_cancel(self):
        stock_entries = get_doctypes_by_field('Stock Entry', 'roll_to_sheet_conversion', self.name)

        if stock_entries:
            for se_data in stock_entries:
                se = frappe.get_doc('Stock Entry', se_data.name)
                if se.docstatus != 2:  # Ensure the document is not already cancelled
                    se.cancel()
                    frappe.db.commit()
                else:
                    frappe.throw(f"Stock Entry {se.name} is already cancelled.")

                # Generate new name for amendment if required
                if se.amended_from:
                    new_name = f"{se.name.split('-')[0]}-{int(se.name.split('-')[-1]) + 1}"
                else:
                    new_name = f"{se.name}-1"

                make_autoname(new_name, 'Stock Entry')