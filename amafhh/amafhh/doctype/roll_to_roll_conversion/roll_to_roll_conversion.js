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

    },
  cut_option: function (frm, cdt, cdn) {
    if (frm.doc.cut_option == 'Manual') {
        $.each(frm.doc.roll_to_roll_conversion_target || [], function (i, d) {
            frappe.model.set_value(d.doctype, d.name, 'weight_target', null);
            frappe.model.set_value(d.doctype, d.name, 'amount', null);
        });
    }
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
                        frappe.model.set_value(cdt, cdn, 'rate', response.message.rate);
                        frappe.model.set_value(cdt, cdn, 'amount', response.message.amount);
                        frappe.model.set_value(cdt, cdn, 'weight_source', response.message.weight_balance);
                        frappe.model.set_value(cdt, cdn, 'width', response.message.width);
                        frappe.model.set_value(cdt, cdn, 'gsm', response.message.gsm);
                        frappe.model.set_value(cdt, cdn, 'length_source', response.message.length_source || 0);

                        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weight_source);
                    } else {
                        frappe.msgprint(__('Record not found for SR No: {0}', [row.sr_no]));
                        frappe.model.set_value(cdt, cdn, 'item_code', '');
                    }


                }
            });
        }


    },
    weight_source: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weight_source);

        function calculate_net_total(frm) {
            var source_weight = 0;
            $.each(frm.doc.roll_to_roll_conversion_source || [], function (i, d) {
                source_weight += flt(d.weight_source);
            });
            frm.set_value("source_weight", source_weight)
        }

        calculate_net_total(frm);
    },
    rate: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weight_source);
    }

});

frappe.ui.form.on('Roll To Roll Conversion Target', {

    roll_to_roll_conversion_target_add: function (frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, 'gsm', frm.fields_dict['roll_to_roll_conversion_source'].grid.data[0].gsm);
        frappe.model.set_value(cdt, cdn, 'rate', frm.fields_dict['roll_to_roll_conversion_source'].grid.data[0].rate);
    },
    weight_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weight_target);

        function calculate_net_total(frm) {
            var target_weight = 0;
            $.each(frm.doc.roll_to_roll_conversion_target || [], function (i, d) {
                target_weight += flt(d.weight_target);
            });
            frm.set_value("target_weight", target_weight)
        }

        calculate_net_total(frm);
        var source_weight = frm.doc.source_weight || 0;
        var target_weight = frm.doc.target_weight || 0;
        if (target_weight > source_weight) {
            frappe.model.set_value(cdt, cdn, 'weight_target', null);
            frappe.throw(__("Target Weight cannot be greater than Source Weight"));
        }
    },
    rate: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weight_target);
    },
    width: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (parseInt(row.width) > frm.doc.roll_to_roll_conversion_source[0].width) {
            frappe.model.set_value(cdt, cdn, 'width', null);
            frappe.throw(__("Target Width cannot be greater than Source Width"));
        }
        if (parseInt(row.width) < 1) {
            frappe.model.set_value(cdt, cdn, 'width', null);
            frappe.throw(__("Target Width cannot be less than 1"));
        }
        if (frm.doc.cut_option =='Full Width') {
            var weight_target = (parseInt(row.width) / frm.doc.roll_to_roll_conversion_source[0].width) * frm.doc.roll_to_roll_conversion_source[0].weight_source;
            frappe.model.set_value(cdt, cdn, 'weight_target', weight_target);
        }
    },


});