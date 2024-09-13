# Copyright (c) 2023, Tech Ventures and contributors
# For license information, please see license.txt
import frappe
from decimal import Decimal
from frappe.model.document import Document
from frappe.utils import nowdate
from frappe import _, throw


class RollToRollConversion(Document):
    def validate(self):
        sum_of_target_width = 0
        for i in self.roll_to_roll_conversion_target:
            sum_of_target_width += Decimal(i.width) if i.width else 0
        if float(sum_of_target_width) != float(self.roll_to_roll_conversion_source[0].width):
            frappe.throw("Source And Target Total Width Should Be Same")

    def on_submit(self):
        # super(RollToRollConversion, self).save()
        # CREATING BATCH NO
        for item in self.roll_to_roll_conversion_target:
            product_item = frappe.new_doc("Item")
            if item.batch_no_target:
                product_item.has_batch_no = 1
            product_item.item_code = item.item_code
            product_item.item_name = item.item_code
            product_item.item_group = 'Roll'
            product_item.gsm = item.gsm
            product_item.width = item.width
            product_item.length = item.length
            product_item.stock_uom = 'Kg'
            product_item.is_stock_item = 1
            product_item.rate = item.rate
            product_item.amount = item.amount
            product_item.qty = item.weight_target
            product_item.import_file = item.import_file
            product_item.ref_no = self.name
            product_item.ref_type = "Roll To Roll Conversion"
            product_item.item_category = item.item_category if item.item_category else ""
            product_item.brand_item = item.brand if item.brand else ""
            # product_item.valuation_rate = item.rate
            try:
                product_item.save()
                # frappe.db.commit()
            except Exception as e:
                frappe.throw(frappe._("Error saving Item: {0}".format(str(e))))
            if item.batch_no_target:
                batch = frappe.new_doc("Batch")
                batch.item = item.item_code
                batch.batch_id = item.batch_no_target
                batch.batch_qty = item.weight_target
                batch.rate = item.rate
                batch.amount = item.amount
                batch.ref_no = self.name
                batch.item_group = 'Roll'
                batch.gsm = item.gsm
                batch.import_file = item.import_file
                batch.ref_type = "Roll To Roll Conversion"
                try:
                    batch.save()
                    # frappe.db.commit()
                except Exception as e:
                    frappe.throw(frappe._("Error saving BATCH NO: {0}".format(str(e))))

        # STOCK ENTRY SAVING
        doc = frappe.new_doc("Stock Entry")
        doc.stock_entry_type = "Repack"
        doc.purpose = "Repack"
        doc.batch_no = self.roll_to_roll_conversion_source[0].batch_no_source if self.roll_to_roll_conversion_source[0].batch_no_source else None
        doc.posting_date = self.posting_date
        doc.roll_to_roll_conversion = self.name
        source_warehouse = self.warehouse
        # Append source item
        it = doc.append("items", {})
        it.set_basic_rate_manually = 1
        it.s_warehouse = source_warehouse
        it.item_code = self.roll_to_roll_conversion_source[0].item_code
        it.qty = self.target_weight
        it.valuation_rate = self.roll_to_roll_conversion_source[0].rate
        it.basic_rate = self.roll_to_roll_conversion_source[0].rate
        it.amount = self.roll_to_roll_conversion_source[0].amount
        it.batch_no = self.roll_to_roll_conversion_source[0].batch_no_source if self.roll_to_roll_conversion_source[0].batch_no_source else None

        # Append target items using a loop
        for item in self.roll_to_roll_conversion_target:
            it = doc.append("items", {})
            # target_warehouse = None
            it.set_basic_rate_manually = 1
            # if item.stock_type_target == "Finished":
            #     target_warehouse = 'Finished Goods - A'
            # elif item.stock_type_target == "Semi-Finished":
            #     target_warehouse = 'Goods In Transit - A'
            # elif item.stock_type_target == "Damaged":
            #     target_warehouse = 'Damaged - A'
            it.t_warehouse = self.warehouse
            it.item_code = item.item_code
            it.qty = item.weight_target
            it.valuation_rate = item.rate
            it.basic_rate = item.rate
            it.basic_amount = item.amount
            it.batch_no = item.batch_no_target

        try:
            doc.ignore_validation = True
            doc.save()
            doc.submit()
            self.stock_entry = doc.name
            self.save()
        except Exception as e:
            frappe.throw(_("Error submitting Stock Entry: {0}".format(str(e))))
