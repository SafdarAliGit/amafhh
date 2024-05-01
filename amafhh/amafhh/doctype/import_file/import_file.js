// Copyright (c) 2023, Tech Ventures and contributors
// For license information, please see license.txt

frappe.ui.form.on('Import File', {
	refresh: function(frm) {

        var import_file = frm.doc.name;
        if (import_file) {
            me.frm.call({
                method: "amafhh.amafhh.doctype.utils.update_avg_rate.update_avg_rate",
                args: {
                    import_file: import_file
                },
                callback: function (r, rt) {
                    if (r.message) {
                        frm.set_value("total_purchase_qty", r.message.total_purchase_qty);
                        frm.set_value("avg_purchase_rate", r.message.avg_purchase_rate);
                        frm.set_value("total_purchase_amount", r.message.total_purchase_amount);
                        frm.set_value("total_lc_amount", r.message.total_lc_amount);
                        frm.set_value("total_cost", r.message.total_cost);
                        frm.set_value("avg_rate_with_lc", r.message.avg_rate_with_lc);
                        frm.set_value("total_sales_qty", r.message.total_sales_qty);
                        frm.set_value("total_balance_qty", r.message.total_balance_qty);
                        frm.set_value("balance_stock_value", r.message.balance_stock_value);
                        frm.set_value("cogs", r.message.cogs);
                    }
                }
            });
        }
	}
});
