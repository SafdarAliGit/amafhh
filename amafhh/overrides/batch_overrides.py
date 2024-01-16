import frappe
from erpnext.stock.doctype.batch.batch import Batch


class BatchOverrides(Batch):

    def set_search_fields(self):
        # Specify the DocType for which you want to set search fields
        doctype = "Batch"

        # Specify the list of fields you want to set as search fields
        search_fields = ['item', 'batch_qty']

        # Fetch the existing Meta information for the DocType
        meta = frappe.get_meta(doctype)

        # Update the search fields in the Meta information
        meta.search_fields = search_fields

        # Save the updated Meta information
        meta.save()

    # Call the function to set search fields
    def onload(self):
        self.set_search_fields()
