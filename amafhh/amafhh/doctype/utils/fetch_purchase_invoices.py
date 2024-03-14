import frappe


@frappe.whitelist()
def fetch_purchase_invoices(**args):
    import_file = args.get('import_file')
    pi = frappe.qb.DocType("Purchase Invoice")
    parent_query = (
        frappe.qb.from_(pi)
        .select(
            pi.name,
            pi.supplier,
            pi.grand_total,
            pi.import_file,
            pi.posting_date
        ).where((pi.import_file == import_file) & (pi.docstatus == 1))
    )
    purchase_invoices = parent_query.run(as_dict=True)

    return {
        "purchase_invoices": purchase_invoices,
    }
