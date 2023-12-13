// Copyright (c) 2023, Tech Ventures and contributors
// For license information, please see license.txt

frappe.ui.form.on('Roll To Roll Conversion', {
    refresh(frm) {
        frm.set_query('item_code', 'roll_to_roll_conversion_source', function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                    ["Item", "item_group", "=", d.item_group]
                ]
            };
        });

    }
});


frappe.ui.form.on('Roll To Roll Conversion Source', {

    sr_no: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.sr_no) {
            frappe.call({
                method: 'amafhh.amafhh.doctype.utils.get_sr_no.get_sr_no',

                args: {
                    sr_no: row.sr_no
                },
                callback: function (response) {
                    if (response.message) {
                        frappe.model.set_value(cdt, cdn, 'item_code', response.message.item_code);
                    } else {
                        frappe.msgprint(__('Record not found for SR No: {0}', [row.sr_no]));
                        frappe.model.set_value(cdt, cdn, 'item_code', '');
                    }
                }
            });
        }
    }

});

frappe.ui.form.on('Roll To Roll Conversion Target', {

    sr_no: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.sr_no) {
            frappe.call({
                method: 'amafhh.amafhh.doctype.utils.get_sr_no.get_sr_no',

                args: {
                    sr_no: row.sr_no
                },
                callback: function (response) {
                    if (response.message) {
                        frappe.model.set_value(cdt, cdn, 'item_code', response.message.item_code);
                   } else {
                        frappe.msgprint(__('Record not found for SR No: {0}', [row.sr_no]));
                        frappe.model.set_value(cdt, cdn, 'item_code', '');
                    }
                }
            });
        }
    }

});