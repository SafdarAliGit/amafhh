// Copyright (c) 2023, Tech Ventures and contributors
// For license information, please see license.txt

frappe.ui.form.on('Roll To Sheet Conversion', {
    refresh: function (frm) {
        frm.set_query('batch_no_source', 'roll_to_sheet_conversion_items', function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                    ["Batch", "item_group", "=", "Roll"],
                    ["Batch", "batch_qty", ">", 0]
                ]
            };
        });
        frm.set_query('item_code_target', 'roll_to_sheet_conversion_items', function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                    ["Item", "item_group", "=", "Sheet"],
                    ["Item", "gsm", "=", d.gsm_source]
                ]
            };
        });
        frm.set_query('item_code_source', 'roll_to_sheet_conversion_items', function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                    ["Item", "item_group", "=", "Roll"],
                    ["Item", "qty", ">", 0]

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

function calculate_source_target_weight_total(frm) {
    var weight_source = 0;
    var weight_target = 0;
    $.each(frm.doc.roll_to_sheet_conversion_items || [], function (i, d) {

        weight_source += flt(d.weight_source);
        weight_target += flt(d.weight_target);
    });
    frm.set_value('source_weight', weight_source);
    frm.set_value('target_weight', weight_target);
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
                        frappe.model.set_value(cdt, cdn, 'import_file', response.message.import_file);
                        frappe.model.set_value(cdt, cdn, 'length_source', response.message.length || 0);
                        frappe.model.set_value(cdt, cdn, 'item_category', response.message.item_category || '');
                        frappe.model.set_value(cdt, cdn, 'brand', response.message.brand || '');
                        // ADD NEW ITEM CODE CUSTOM WORK
                        // Iterate through each row in the child table
                        var itemCodeCount = {};

                        frm.doc.roll_to_sheet_conversion_items.forEach(function (item, index) {
                            // Check if the item code is empty
                            if (!item.item_code_target) {
                                var itemCodeSource = row.item_code_source.toString();

                                // Check if the item_code_source has occurred before
                                if (itemCodeCount[itemCodeSource]) {
                                    // Increment the count
                                    itemCodeCount[itemCodeSource]++;
                                } else {
                                    // Initialize the count
                                    itemCodeCount[itemCodeSource] = 1;
                                }

                                // Check for duplicates and update item_code_target
                                for (var i = 0; i < frm.doc.roll_to_sheet_conversion_items.length; i++) {
                                    if (i !== index && frm.doc.roll_to_sheet_conversion_items[i].item_code_source === itemCodeSource) {
                                        itemCodeCount[itemCodeSource]++;
                                        var newItemCode = itemCodeSource + '-' + itemCodeCount[itemCodeSource];
                                        frappe.model.set_value(cdt, cdn, 'item_code_target', newItemCode);
                                        if (frm.doc.generate_batch == 1) {
                                            frappe.model.set_value(cdt, cdn, 'batch_no_target', newItemCode);
                                        }
                                        break; // Exit the loop if a duplicate is found
                                    }
                                }

                                // If no duplicate is found, set the new item code
                                if (!frm.doc.roll_to_sheet_conversion_items[index].item_code_target) {
                                    var newItemCode = itemCodeSource + '-' + itemCodeCount[itemCodeSource];
                                    frappe.model.set_value(cdt, cdn, 'item_code_target', newItemCode);
                                    if (frm.doc.generate_batch == 1) {
                                        frappe.model.set_value(cdt, cdn, 'batch_no_target', newItemCode);
                                    }
                                }
                            }
                        });
                        calculate_source_target_weight_total(frm);

                        // END CUSTOM
                    } else {
                        frappe.msgprint(__('Record not found for SR No: {0}', [row.batch_no_source]));
                        frappe.model.set_value(cdt, cdn, 'item_code_source', '');
                    }
                }
            });
        }
    },
    item_code_source: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.item_code_source) {
            frappe.call({
                method: 'amafhh.amafhh.doctype.utils.get_by_item_code.get_by_item_code',

                args: {
                    item_code: row.item_code_source
                },
                callback: function (response) {
                    if (response.message) {
                        frappe.model.set_value(cdt, cdn, 'item_code_source', response.message.item_code);
                        frappe.model.set_value(cdt, cdn, 'rate', response.message.rate);
                        frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
                        frappe.model.set_value(cdt, cdn, 'weight_source', response.message.weight_balance);
                        frappe.model.set_value(cdt, cdn, 'width_source', response.message.width);
                        frappe.model.set_value(cdt, cdn, 'gsm_source', response.message.gsm);
                        frappe.model.set_value(cdt, cdn, 'import_file', response.message.import_file);
                        frappe.model.set_value(cdt, cdn, 'length_source', response.message.length || 0);
                        // ADD NEW ITEM CODE CUSTOM WORK
                        // Iterate through each row in the child table
                        var itemCodeCount = {};

                        frm.doc.roll_to_sheet_conversion_items.forEach(function (item, index) {
                            // Check if the item code is empty
                            if (!item.item_code_target) {
                                var itemCodeSource = row.item_code_source.toString();

                                // Check if the item_code_source has occurred before
                                if (itemCodeCount[itemCodeSource]) {
                                    // Increment the count
                                    itemCodeCount[itemCodeSource]++;
                                } else {
                                    // Initialize the count
                                    itemCodeCount[itemCodeSource] = 1;
                                }

                                // Check for duplicates and update item_code_target
                                for (var i = 0; i < frm.doc.roll_to_sheet_conversion_items.length; i++) {
                                    if (i !== index && frm.doc.roll_to_sheet_conversion_items[i].item_code_source === itemCodeSource) {
                                        itemCodeCount[itemCodeSource]++;
                                        var newItemCode = itemCodeSource + '-' + itemCodeCount[itemCodeSource];
                                        frappe.model.set_value(cdt, cdn, 'item_code_target', newItemCode);
                                        if (frm.doc.generate_batch == 1) {
                                            frappe.model.set_value(cdt, cdn, 'batch_no_target', newItemCode);
                                        }
                                        break; // Exit the loop if a duplicate is found
                                    }
                                }

                                // If no duplicate is found, set the new item code
                                if (!frm.doc.roll_to_sheet_conversion_items[index].item_code_target) {
                                    var newItemCode = itemCodeSource + '-' + itemCodeCount[itemCodeSource];
                                    frappe.model.set_value(cdt, cdn, 'item_code_target', newItemCode);
                                    if (frm.doc.generate_batch == 1) {
                                        frappe.model.set_value(cdt, cdn, 'batch_no_target', newItemCode);
                                    }
                                }
                            }
                        });
                    calculate_source_target_weight_total(frm);

                        // END CUSTOM
                    } else {
                        frappe.msgprint(__('Record not found for SR No: {0}', [row.batch_no_source]));
                        frappe.model.set_value(cdt, cdn, 'item_code_source', '');
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
        calculate_source_target_weight_total(frm);
    },
    ream_pkt_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateWeightAndSetValues(row, conversionType, cdt, cdn);
        calculate_source_target_weight_total(frm);
    },

    length_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateWeightAndSetValues(row, conversionType, cdt, cdn);
        calculate_source_target_weight_total(frm);
    },
    width_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (parseFloat(row.width_target) > parseFloat(row.width_source)) {
            frappe.model.set_value(cdt, cdn, 'width_target', null);
            frappe.throw(__("Target Width cannot be greater than Source Width"));
        } else {
            var conversionType = frm.doc.conversion_type;
            calculateWeightAndSetValues(row, conversionType, cdt, cdn);
            calculate_source_target_weight_total(frm);
        }
        if (parseFloat(row.width_target) < 1) {
            frappe.model.set_value(cdt, cdn, 'width_target', null);
            frappe.throw(__("Target Width cannot be less than 1"));
        } else {
            var conversionType = frm.doc.conversion_type;
            calculateWeightAndSetValues(row, conversionType, cdt, cdn);
            calculate_source_target_weight_total(frm);
        }
    },
    //     item_code_target: function (frm, cdt, cdn) {
    //     var row = locals[cdt][cdn];
    //     if (row.item_code_target) {
    //         frappe.call({
    //             method: 'amafhh.amafhh.doctype.utils.get_by_item_code.get_by_item_code',
    //
    //             args: {
    //                 item_code: row.item_code_target
    //             },
    //             callback: function (response) {
    //                 if (response.message) {
    //                     frappe.model.set_value(cdt, cdn, 'width_target', response.message.width);
    //                     frappe.model.set_value(cdt, cdn, 'length_target', response.message.length || 0);
    //                     frappe.model.set_value(cdt, cdn, 'batch_no_target', row.item_code_target);
    //
    //                     frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weight_target);
    //                 } else {
    //                     frappe.msgprint(__('Record not found for Item: {0}', [row.item_code]));
    //                 }
    //
    //
    //             }
    //         });
    //     }
    //
    //
    // },

});
