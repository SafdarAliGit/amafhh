// Copyright (c) 2023, Tech Ventures and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sheet To Sheet Conversion', {
    refresh: function (frm) {
        frm.set_query('item_code_source', 'sheet_to_sheet_conversion_items', function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                    ["Item", "item_group", "=", 'Sheet']
                ]
            };
        });
        frm.set_query('item_code_target', 'sheet_to_sheet_conversion_items', function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                    ["Item", "item_group", "=", 'Sheet']
                ]
            };
        });
    }
});
// CUSTOM ID
var maxSubBatchManager = {
    batch: {},
};

// CUSTOM OBJECT END

function calculateSourceWeightAndSetValues(row, conversionType, cdt, cdn) {
    var single_ream_pkt_weight, total_ream_pkt_weight = 0, single_sheet_weight, total_sheet_weight = 0, weightFactor;

    if (conversionType == 'REAM') {
        weightFactor = 3100;
         single_ream_pkt_weight = (row.width_source * row.gsm_source * row.length_source) / weightFactor;
         single_sheet_weight = single_ream_pkt_weight / 500;
    } else if (conversionType == 'PKT') {
        weightFactor = 15500;
         single_ream_pkt_weight = (row.width_source * row.gsm_source * row.length_source) / weightFactor;
         single_sheet_weight = single_ream_pkt_weight / 100;
    } else {
        // Adjust this part based on your requirements
        frappe.model.set_value(cdt, cdn, 'sheet_source', 0); // Set to a default value or handle differently
        frappe.msgprint("Please select Conversion Type");
        return;
    }

    if (row.ream_pkt_source !== null && row.ream_pkt_source !== undefined && row.ream_pkt_source !== "") {
        total_ream_pkt_weight = single_ream_pkt_weight * row.ream_pkt_source;
    }
    if (row.sheet_source !== null && row.sheet_source !== undefined && row.sheet_source !== "") {
        total_sheet_weight = single_sheet_weight * row.sheet_source;
    }
    frappe.model.set_value(cdt, cdn, 'weight_source', total_ream_pkt_weight + total_sheet_weight);
}


function calculateTargetWeightAndSetValues(row, conversionType, cdt, cdn) {
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

function calculate_source_target_weight_total(frm) {
    var weight_source = 0;
    var weight_target = 0;
    $.each(frm.doc.sheet_to_sheet_conversion_items || [], function (i, d) {

        weight_source += flt(d.weight_source);
        weight_target += flt(d.weight_target);
    });
    frm.set_value('source_weight', weight_source);
    frm.set_value('target_weight', weight_target);
}

frappe.ui.form.on('Sheet To Sheet Conversion Items', {

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
                        frappe.model.set_value(cdt, cdn, 'stock_weight_source', response.message.weight_balance);
                        frappe.model.set_value(cdt, cdn, 'width_source', response.message.width);
                        frappe.model.set_value(cdt, cdn, 'gsm_source', response.message.gsm);
                        frappe.model.set_value(cdt, cdn, 'length_source', response.message.length_source || 0);


                        // if (response.message.batch_id in maxSubBatchManager.batch) {
                        //     maxSubBatchManager.batch[response.message.batch_id] += 1;
                        // } else {
                        //     maxSubBatchManager.batch[response.message.batch_id] = 1;
                        // }
                        //
                        // frappe.model.set_value(cdt, cdn, 'batch_no_target', response.message.batch_id + ' - ' + maxSubBatchManager.batch[response.message.batch_id]);

                    } else {
                        frappe.msgprint(__('Record not found for Batch No: {0}', [row.batch_no_source]));
                        frappe.model.set_value(cdt, cdn, 'item_code', '');
                    }
                }
            });
        }
    },

    rate: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
    },
    sheet_source: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateSourceWeightAndSetValues(row, conversionType, cdt, cdn);
        calculate_source_target_weight_total(frm);
    },
    ream_pkt_source: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateSourceWeightAndSetValues(row, conversionType, cdt, cdn);
        calculate_source_target_weight_total(frm);
    },

    sheet_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateTargetWeightAndSetValues(row, conversionType, cdt, cdn);
        calculate_source_target_weight_total(frm)
        frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
    },
    ream_pkt_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateTargetWeightAndSetValues(row, conversionType, cdt, cdn);
        calculate_source_target_weight_total(frm);
        frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
    },

    length_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateTargetWeightAndSetValues(row, conversionType, cdt, cdn);
        calculate_source_target_weight_total(frm);
        frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
    },
    width_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (parseFloat(row.width_target) > parseFloat(row.width_source)) {
            frappe.model.set_value(cdt, cdn, 'width_target', null);
            frappe.throw(__("Target Width cannot be greater than Source Width"));
        } else {
            var conversionType = frm.doc.conversion_type;
            calculateTargetWeightAndSetValues(row, conversionType, cdt, cdn);
            calculate_source_target_weight_total(frm);
            frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
        }
        if (parseFloat(row.width_target) < 1) {
            frappe.model.set_value(cdt, cdn, 'width_target', null);
            frappe.throw(__("Target Width cannot be less than 1"));
        } else {
            var conversionType = frm.doc.conversion_type;
            calculateTargetWeightAndSetValues(row, conversionType, cdt, cdn);
            calculate_source_target_weight_total(frm);
            frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
        }
    },
    item_code_source: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        function check_net_total(frm) {
            var weight_source = 0;
            var weight_target = 0;
            $.each(frm.doc.sheet_to_sheet_conversion_items || [], function (i, d) {
                if (row.item_code_source == d.item_code_source) {
                    weight_source += flt(d.weight_source);
                    weight_target += flt(d.weight_target);
                }
            });
            if (weight_target > weight_source) {
                frappe.model.set_value(cdt, cdn, 'item_code_source', null);
                frappe.throw(__("Target Weight cannot be greater than Source Weight"));
            }

        }

        check_net_total(frm);

    }

});
