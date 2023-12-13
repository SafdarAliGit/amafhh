// Copyright (c) 2023, Tech Ventures and contributors
// For license information, please see license.txt

frappe.ui.form.on('Roll To Sheet Conversion', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on('Roll To Sheet Conversion Source', {

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
                         frappe.model.set_value(cdt, cdn, 'rate', response.message.purchase_rate);
                        frappe.model.set_value(cdt, cdn, 'amount', response.message.purchase_amount);
                        frappe.model.set_value(cdt, cdn, 'weightkg', response.message.weight_balance);
                        frappe.model.set_value(cdt, cdn, 'width', response.message.width);
                        frappe.model.set_value(cdt, cdn, 'gsm', response.message.gsm);
                    } else {
                        frappe.msgprint(__('Record not found for SR No: {0}', [row.sr_no]));
                        frappe.model.set_value(cdt, cdn, 'item_code', '');
                    }
                }
            });
        }
    }

});
frappe.ui.form.on('Roll To Sheet Conversion Target', {

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
