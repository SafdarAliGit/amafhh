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
                        frappe.model.set_value(cdt, cdn, 'rate', response.message.rate);
                        frappe.model.set_value(cdt, cdn, 'amount', response.message.amount);
                        frappe.model.set_value(cdt, cdn, 'weightkg', response.message.weight_balance);
                        frappe.model.set_value(cdt, cdn, 'width', response.message.width);
                        frappe.model.set_value(cdt, cdn, 'gsm', response.message.gsm);

                        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weightkg);
                    } else {
                        frappe.msgprint(__('Record not found for SR No: {0}', [row.sr_no]));
                        frappe.model.set_value(cdt, cdn, 'item_code', '');
                    }
                }
            });
        }
    },
    weightkg: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weightkg);

        function calculate_net_total(frm) {
            var source_weight = 0;
            $.each(frm.doc.roll_to_sheet_conversion_source || [], function (i, d) {
                source_weight += flt(d.weightkg);
            });
            frm.set_value("source_weight", source_weight)
        }

        calculate_net_total(frm);
    },
    rate: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weightkg);
    }

});

function calculateWeightAndSetValues(row, conversionType, cdt, cdn) {
    var single_ream_pkt_weight, total_ream_pkt_weight=0, single_sheet_weight, total_sheet_weight=0, weightFactor;

    if (conversionType == 'REAM') {
        weightFactor = 3100;
        var single_ream_pkt_weight = (row.width_target * row.gsm_source * row.length_target) / weightFactor;
        var single_sheet_weight = single_ream_pkt_weight / 500;
    } else if (conversionType == 'PKT') {
        weightFactor = 15500;
        var single_ream_pkt_weight = (row.width_target * row.gsm_source * row.length_target) / weightFactor;
        var single_sheet_weight = single_ream_pkt_weight / 100;
    } else {
        // Adjust this part based on your requirements
        frappe.model.set_value(cdt, cdn, 'sheet_target', 0); // Set to a default value or handle differently
        frappe.msgprint("Please select Conversion Type");
        return;
    }

    if (row.ream_pkt_target !== null && row.ream_pkt_target !== undefined && row.ream_pkt_target !== "") {
        total_ream_pkt_weight = single_ream_pkt_weight * row.ream_pkt_target;
    }
    if (row.sheet_target !== null && row.sheet_target !== undefined && row.sheet_target !== "") {
        total_sheet_weight = single_sheet_weight * row.sheet_target;
    }
    frappe.model.set_value(cdt, cdn, 'weight_target', total_ream_pkt_weight + total_sheet_weight );
}


frappe.ui.form.on('Roll To Sheet Conversion Items', {

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
                        frappe.model.set_value(cdt, cdn, 'item_code_source', response.message.item_code);
                        frappe.model.set_value(cdt, cdn, 'rate', response.message.rate);
                        frappe.model.set_value(cdt, cdn, 'amount', response.message.amount);
                        frappe.model.set_value(cdt, cdn, 'weight_source', response.message.weight_balance);
                        frappe.model.set_value(cdt, cdn, 'width_source', response.message.width);
                        frappe.model.set_value(cdt, cdn, 'gsm_source', response.message.gsm);
                    } else {
                        frappe.msgprint(__('Record not found for SR No: {0}', [row.sr_no]));
                        frappe.model.set_value(cdt, cdn, 'item_code', '');
                    }
                }
            });
        }
    },
    weight_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weight_target);

        // function calculate_net_total(frm) {
        //     var weight_target = 0;
        //     $.each(frm.doc.roll_to_sheet_conversion_items || [], function (i, d) {
        //         weight_target += flt(d.weight_target);
        //     });
        //     frm.set_value("weight_target", weight_target)
        // }
        //
        // calculate_net_total(frm);
        // var source_weight = frm.doc.source_weight || 0;
        // var target_weight = frm.doc.target_weight || 0;
        // if (target_weight > source_weight) {
        //     frappe.model.set_value(cdt, cdn, 'weightkg', null);
        //     frappe.throw(__("Target Weight cannot be greater than Source Weight"));
        // }
    },
    rate: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weight_target);
    },

    sheet_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateWeightAndSetValues(row, conversionType, cdt, cdn);
    },
    ream_pkt_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateWeightAndSetValues(row, conversionType, cdt, cdn);
    },
    width_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateWeightAndSetValues(row, conversionType, cdt, cdn);
    },

    length_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateWeightAndSetValues(row, conversionType, cdt, cdn);
    }

});
