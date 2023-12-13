# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

form_grid_templates = {"items": "templates/form_grid/item_grid.html"}


class SalesInvoiceOverrides(SalesInvoice):
    def autoname(self):
        self.name = self.sales_form_id

