// Copyright (c) 2023, Tech Ventures and contributors
// For license information, please see license.txt

frappe.ui.form.on('Roll To Sheet Conversion', {
    refresh: function(frm) {
      frm.set_query('batch_no_source', 'roll_to_sheet_conversion_items', function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                    ["Batch", "item_group", "=", "Roll"]
                ]
            };
        });
        frm.set_query('item_code_target', 'roll_to_sheet_conversion_items', function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                    ["Item", "item_group", "=", "Sheet"]
                ]
            };
        });
         frm.set_query('item_code_source', 'roll_to_sheet_conversion_items', function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                    ["Item", "item_group", "=", "Roll"]
                ]
            };
        });
    }
});


function calculateWeightAndSetValues(row, conversionType, cdt, cdn) {
    var single_ream_pkt_weight, total_ream_pkt_weight = 0, single_sheet_weight, total_sheet_weight = 0, weightFactor;

    if (conversionType == 'REAM') {
        weightFactor = 3100;
         single_ream_pkt_weight = (row.width_target * row.gsm_source * row.length_target) / weightFactor;
         single_sheet_weight = single_ream_pkt_weight / 500;
    } else if (conversionType == 'PKT') {
        weightFactor = 15500;
         single_ream_pkt_weight = (row.width_target * row.gsm_source * row.length_target) / weightFactor;
         single_sheet_weight = single_ream_pkt_weight / 100;
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
    frappe.model.set_value(cdt, cdn, 'weight_target', total_ream_pkt_weight + total_sheet_weight);
}


frappe.ui.form.on('Roll To Sheet Conversion Items', {

    batch_no_source: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.batch_no_source) {
            frappe.call({
                method: 'amafhh.amafhh.doctype.utils.get_batch_no.get_batch_no',

                args: {
                    batch_no: row.batch_no_source
                },
                callback: function (response) {
                    if (response.message) {
                        frappe.model.set_value(cdt, cdn, 'item_code_source', response.message.item_code);
                        frappe.model.set_value(cdt, cdn, 'rate', response.message.rate);
                        frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
                        frappe.model.set_value(cdt, cdn, 'weight_source', response.message.weight_balance);
                        frappe.model.set_value(cdt, cdn, 'width_source', response.message.width);
                        frappe.model.set_value(cdt, cdn, 'gsm_source', response.message.gsm);
                        frappe.model.set_value(cdt, cdn, 'length_source', response.message.length_source);
                        frappe.model.set_value(cdt, cdn, 'import_file', response.message.import_file);
                        frappe.model.set_value(cdt, cdn, 'length_source', response.message.length_source || 0);
                    } else {
                        frappe.msgprint(__('Record not found for SR No: {0}', [row.batch_no_source]));
                        frappe.model.set_value(cdt, cdn, 'item_code', '');
                    }
                }
            });
        }
    },
    weight_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));

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
        frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
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

    length_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateWeightAndSetValues(row, conversionType, cdt, cdn);
    },
    width_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (parseFloat(row.width_target) > parseFloat(row.width_source)) {
            frappe.model.set_value(cdt, cdn, 'width_target', null);
            frappe.throw(__("Target Width cannot be greater than Source Width"));
        } else {
            var conversionType = frm.doc.conversion_type;
            calculateWeightAndSetValues(row, conversionType, cdt, cdn);
        }
        if (parseFloat(row.width_target) < 1) {
            frappe.model.set_value(cdt, cdn, 'width_target', null);
            frappe.throw(__("Target Width cannot be less than 1"));
        } else {
            var conversionType = frm.doc.conversion_type;
            calculateWeightAndSetValues(row, conversionType, cdt, cdn);
        }
    },
        item_code_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.item_code_target) {
            frappe.call({
                method: 'amafhh.amafhh.doctype.utils.get_by_item_code.get_by_item_code',

                args: {
                    item_code: row.item_code_target
                },
                callback: function (response) {
                    if (response.message) {
                        frappe.model.set_value(cdt, cdn, 'width_target', response.message.width);
                        frappe.model.set_value(cdt, cdn, 'length_target', response.message.length || 0);

                        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weight_target);
                    } else {
                        frappe.msgprint(__('Record not found for Item: {0}', [row.item_code]));
                    }


                }
            });
        }


    },

});
