# Copyright (c) 2023, Tech Ventures and contributors
# For license information, please see license.txt
import frappe
# import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from frappe import _, throw


class RollToRollConversion(Document):
    def before_insert(self):
        # super(SheetToSheetConversion, self).before_insert()
        batches = {}
        for i in self.roll_to_roll_conversion_target:
            last_record = frappe.get_all(
                'Roll To Roll Conversion Target',
                filters={
                    'batch_no_target': ('like', f'{self.roll_to_roll_conversion_source[0].batch_no_source}-%')},
                fields=['batch_no_target'],
                order_by='CAST(REPLACE(batch_no_target, "-", "") AS SIGNED) DESC',
                limit=1
            )
            if last_record:
                last_batch_number = int(last_record[0]['batch_no_target'].split('-')[-1])
                if self.roll_to_roll_conversion_source[0].batch_no_source in batches:
                    i.batch_no_target = f"{self.roll_to_roll_conversion_source[0].batch_no_source}-{last_batch_number + batches[self.roll_to_roll_conversion_source[0].batch_no_source]}"
                else:
                    batches[self.roll_to_roll_conversion_source[0].batch_no_source] = 1
                    i.batch_no_target = f"{self.roll_to_roll_conversion_source[0].batch_no_source}-{last_batch_number + 1}"
            else:
                if self.roll_to_roll_conversion_source[0].batch_no_source in batches:
                    i.batch_no_target = f"{self.roll_to_roll_conversion_source[0].batch_no_source}-{batches[self.roll_to_roll_conversion_source[0].batch_no_source]}"
                else:
                    batches[self.roll_to_roll_conversion_source[0].batch_no_source] = 1
                    i.batch_no_target = f"{self.roll_to_roll_conversion_source[0].batch_no_source}-{1}"

            i.save()

        frappe.db.commit()

    def on_submit(self):
        # super(RollToRollConversion, self).save()
        # CREATING BATCH NO
        for item in self.roll_to_roll_conversion_target:
            batch = frappe.new_doc("Batch")
            batch.item = item.item_code
            batch.batch_id = item.batch_no_target
            batch.batch_qty = item.weight_target
            batch.rate = item.rate
            batch.amount = item.amount
            batch.ref_no = self.name
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
        doc.batch_no = self.roll_to_roll_conversion_source[0].batch_no_source
        doc.posting_date = nowdate()
        doc.roll_to_roll_conversion = self.name
        source_warehouse = self.warehouse

        # Append source item
        it = doc.append("items", {})
        it.s_warehouse = source_warehouse
        it.item_code = self.roll_to_roll_conversion_source[0].item_code
        it.qty = self.target_weight
        it.basic_rate = self.roll_to_roll_conversion_source[0].rate
        it.amount = self.roll_to_roll_conversion_source[0].amount
        it.batch_no = self.roll_to_roll_conversion_source[0].batch_no_source

        # Append target items using a loop
        for item in self.roll_to_roll_conversion_target:
            it = doc.append("items", {})
            target_warehouse = None
            if item.stock_type_target == "Finished":
                target_warehouse = 'Finished Goods - A'
            elif item.stock_type_target == "Semi-Finished":
                target_warehouse = 'Goods In Transit - A'
            elif item.stock_type_target == "Damaged":
                target_warehouse = 'Damaged - A'
            it.t_warehouse = target_warehouse
            it.item_code = item.item_code
            it.qty = item.weight_target
            it.basic_rate = item.rate
            it.amount = item.amount
            it.batch_no = item.batch_no_target

        try:
            # doc.ignore_validation = True
            doc.submit()
        except Exception as e:
            frappe.throw(_("Error submitting Stock Entry: {0}".format(str(e))))
