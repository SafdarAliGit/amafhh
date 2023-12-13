import frappe
from erpnext.selling.doctype.customer.customer import Customer


class CustomerOverrides(Customer):
    def after_insert(self):
        supplier = frappe.new_doc('Supplier')
        supplier.supplier_name = self.customer_name
        supplier.supplier_group = 'All Supplier Groups'
        supplier.supplier_type = 'Individual'
        supplier.insert()
        party_link = frappe.new_doc('Party Link')
        party_link.primary_role = 'Customer'
        party_link.primary_party = self.customer_name
        party_link.secondary_role = 'Supplier'
        party_link.secondary_party = self.customer_name
        party_link.insert()
