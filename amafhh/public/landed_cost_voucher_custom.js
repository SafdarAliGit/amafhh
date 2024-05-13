frappe.ui.form.on("Landed Cost Voucher", {
    import_file: function (frm) {
        var import_file = frm.doc.import_file;
        fetch_purchase_invoices(frm, import_file);

    },
    on_submit: function (frm) {
        frappe.set_route("Form", "Import File", frm.doc.import_file);
    }

});

function fetch_purchase_invoices(frm, import_file) {
    if (import_file) {
        // Clear existing data before adding new entries
        frm.clear_table("purchase_receipts");

        frappe.call({
            method: "amafhh.amafhh.doctype.utils.fetch_purchase_invoices.fetch_purchase_invoices",
            args: {
                import_file: import_file
            },
            callback: function (response) {
                if (response.message.purchase_invoices) {
                    response.message.purchase_invoices.forEach(function (invoice) {
                        let entry = frm.add_child("purchase_receipts");
                        entry.receipt_document = invoice.name,
                        entry.receipt_document_type = 'Purchase Invoice',
                        entry.supplier = invoice.supplier,
                        entry.grand_total = invoice.grand_total,
                        entry.posting_date = invoice.posting_date,
                        entry.import_file = invoice.import_file

                    });
                }
                frm.refresh_field('purchase_receipts');
            }
        });
    }
}
