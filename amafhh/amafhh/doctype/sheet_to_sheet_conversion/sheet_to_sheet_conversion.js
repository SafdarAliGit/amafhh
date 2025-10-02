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
        frm.set_query('batch_no_source', 'sheet_to_sheet_conversion_items', function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                    ["Batch", "item_group", "=", 'Sheet']
                ]
            };
        });
        frm.set_query('item_code_target', 'sheet_to_sheet_conversion_items', function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                    ["Item", "item_group", "=", 'Sheet'],
                    ["Item", "gsm", "=", d.gsm_source]
                ]
            };
        });
    },

});
// CUSTOM ID
var maxSubBatchManager = {
    batch: {},
};

// CUSTOM OBJECT END
function setConversionType(frm, cdt, cdn) {
    let conversionType = "";
    var row = locals[cdt][cdn];
    let gsm = row.gsm_source;
    if (gsm >= 40 && gsm <= 90) {
        conversionType = 'REAM';
    } else if (gsm >= 91 && gsm <= 400) {
        conversionType = 'PKT';
    }
    else {
        frappe.msgprint("Invalid GSM");
        return;
    }
    return conversionType;
}

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
        return;
    }

    if (row.ream_pkt_source !== null && row.ream_pkt_source !== undefined && row.ream_pkt_source !== "") {
        total_ream_pkt_weight = single_ream_pkt_weight * row.ream_pkt_source;
    }
    if (row.sheet_source !== null && row.sheet_source !== undefined && row.sheet_source !== "") {
        total_sheet_weight = single_sheet_weight * row.sheet_source;
    }
    frappe.model.set_value(cdt, cdn, 'weight_source', total_ream_pkt_weight + total_sheet_weight);
    // frappe.model.set_value(cdt, cdn, 'weight_per_unit', single_sheet_weight);
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
        return;
    }

    if (row.ream_pkt_target !== null && row.ream_pkt_target !== undefined && row.ream_pkt_target !== "") {
        total_ream_pkt_weight = single_ream_pkt_weight * row.ream_pkt_target;
    }
    if (row.sheet_target !== null && row.sheet_target !== undefined && row.sheet_target !== "") {
        total_sheet_weight = single_sheet_weight * row.sheet_target;
    }
    frappe.model.set_value(cdt, cdn, 'weight_target', total_ream_pkt_weight + total_sheet_weight);
    // frappe.model.set_value(cdt, cdn, 'weight_per_unit', single_sheet_weight);
}

function calculate_source_target_weight_total(frm) {
    var weight_source = 0;
    var weight_target = 0;
    $.each(frm.doc.sheet_to_sheet_conversion_items || [], function (i, d) {

        weight_source += flt(d.weight_source);
        weight_target += flt(d.weight_target);
    });
    frm.set_value('source_weight', parseFloat(weight_source).toFixed(4));
    frm.set_value('target_weight', parseFloat(weight_target).toFixed(4));
}

function check_net_total(frm) {
    var weight_source = 0;
    var weight_target = 0;
    $.each(frm.doc.sheet_to_sheet_conversion_items || [], function (i, d) {
        if (row.item_code_source == d.item_code_source) {
            weight_source += flt(d.balance_qty);
            weight_target += flt(d.weight_target);
        }
    });
    if (weight_target > weight_source) {
        frappe.model.set_value(cdt, cdn, 'item_code_source', null);
        frappe.throw(__("Target Weight cannot be greater than Source Weight"));
    }

}

function target_ream_pkt(frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    var weight_factor = 1;
    if (frm.doc.conversion_type == 'REAM') {
        weight_factor = 3100;
    } else {
        weight_factor = 15500;
    }
    frappe.model.set_value(cdt, cdn, 'ream_pkt_projected', parseFloat(row.weight_source) / ((parseFloat(row.width_target) * parseFloat(row.length_target) * parseFloat(row.gsm_source)) / weight_factor));
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
                        frappe.model.set_value(cdt, cdn, 'rate', response.message.valuation_rate);
                        frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
                        frappe.model.set_value(cdt, cdn, 'stock_weight_source', response.message.weight_balance);
                        frappe.model.set_value(cdt, cdn, 'width_source', response.message.width);
                        frappe.model.set_value(cdt, cdn, 'gsm_source', response.message.gsm);
                        frappe.model.set_value(cdt, cdn, 'import_file', response.message.import_file);
                        frappe.model.set_value(cdt, cdn, 'length_source', response.message.length || 0);
                        frappe.model.set_value(cdt, cdn, 'item_category', response.message.item_category || '');
                        frappe.model.set_value(cdt, cdn, 'brand', response.message.brand || '');
                        var weight_factor = 1;
                        if (frm.doc.conversion_type == 'REAM') {
                            weight_factor = 3100;
                        } else {
                            weight_factor = 15500;
                        }
                        frappe.model.set_value(cdt, cdn, 'calculated_rp', parseFloat(row.stock_weight_source) / ((parseFloat(row.width_source) * parseFloat(row.length_source) * parseFloat(row.gsm_source)) / weight_factor));


                        // ADD NEW ITEM CODE CUSTOM WORK
                        // Iterate through each row in the child table
                        var itemCodeCount = {};

                        frm.doc.sheet_to_sheet_conversion_items.forEach(function (item, index) {
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
                                for (var i = 0; i < frm.doc.sheet_to_sheet_conversion_items.length; i++) {
                                    if (i !== index && frm.doc.sheet_to_sheet_conversion_items[i].item_code_source === itemCodeSource) {
                                        itemCodeCount[itemCodeSource]++;
                                        var newItemCode = itemCodeSource + '-' + itemCodeCount[itemCodeSource];
                                        frappe.model.set_value(cdt, cdn, 'item_code_target', newItemCode);
                                        if (frm.doc.generate_batch === 1) {
                                            frappe.model.set_value(cdt, cdn, 'batch_no_target', newItemCode);
                                        }
                                        break; // Exit the loop if a duplicate is found
                                    }
                                }

                                // If no duplicate is found, set the new item code
                                if (!frm.doc.sheet_to_sheet_conversion_items[index].item_code_target) {
                                    var newItemCode = itemCodeSource + '-' + itemCodeCount[itemCodeSource];
                                    frappe.model.set_value(cdt, cdn, 'item_code_target', newItemCode);
                                    if (frm.doc.generate_batch === 1) {
                                        frappe.model.set_value(cdt, cdn, 'batch_no_target', newItemCode);
                                    }
                                }
                            }
                        });
                        calculate_source_target_weight_total(frm);

                        // END CUSTOM

                    } else {
                        frappe.msgprint(__('Record not found for Batch No: {0}', [row.batch_no_source]));
                        frappe.model.set_value(cdt, cdn, 'item_code', '');
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
                        frappe.model.set_value(cdt, cdn, 'rate', response.message.valuation_rate);
                        frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
                        frappe.model.set_value(cdt, cdn, 'stock_weight_source', response.message.weight_balance);
                        frappe.model.set_value(cdt, cdn, 'width_source', response.message.width);
                        frappe.model.set_value(cdt, cdn, 'gsm_source', response.message.gsm);
                        frappe.model.set_value(cdt, cdn, 'import_file', response.message.import_file);
                        frappe.model.set_value(cdt, cdn, 'length_source', response.message.length || 0);
                        var weight_factor = 1;
                        if (frm.doc.conversion_type == 'REAM') {
                            weight_factor = 3100;
                        } else {
                            weight_factor = 15500;
                        }
                        frappe.model.set_value(cdt, cdn, 'calculated_rp', parseFloat(row.stock_weight_source) / ((parseFloat(row.width_source) * parseFloat(row.length_source) * parseFloat(row.gsm_source)) / weight_factor));
                        var itemCodeCount = {};

                        frm.doc.sheet_to_sheet_conversion_items.forEach(function (item, index) {
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
                                for (var i = 0; i < frm.doc.sheet_to_sheet_conversion_items.length; i++) {
                                    if (i !== index && frm.doc.sheet_to_sheet_conversion_items[i].item_code_source === itemCodeSource) {
                                        itemCodeCount[itemCodeSource]++;
                                        var newItemCode = itemCodeSource + '-' + itemCodeCount[itemCodeSource];
                                        frappe.model.set_value(cdt, cdn, 'item_code_target', newItemCode);
                                        if (frm.doc.generate_batch === 1) {
                                            frappe.model.set_value(cdt, cdn, 'batch_no_target', newItemCode);
                                        }
                                        break; // Exit the loop if a duplicate is found
                                    }
                                }

                                // If no duplicate is found, set the new item code
                                if (!frm.doc.sheet_to_sheet_conversion_items[index].item_code_target) {
                                    var newItemCode = itemCodeSource + '-' + itemCodeCount[itemCodeSource];
                                    frappe.model.set_value(cdt, cdn, 'item_code_target', newItemCode);
                                    if (frm.doc.generate_batch === 1) {
                                        frappe.model.set_value(cdt, cdn, 'batch_no_target', newItemCode);
                                    }
                                }
                            }
                        });

                        calculate_source_target_weight_total(frm);
                        // END CUSTOM
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
        var conversionType = setConversionType(frm,cdt,cdn);
        calculateSourceWeightAndSetValues(row, conversionType, cdt, cdn);
        calculate_source_target_weight_total(frm);
    },
    ream_pkt_source: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = setConversionType(frm,cdt,cdn);
        calculateSourceWeightAndSetValues(row, conversionType, cdt, cdn);
        calculate_source_target_weight_total(frm);
    },

    sheet_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = setConversionType(frm,cdt,cdn);
        calculateTargetWeightAndSetValues(row, conversionType, cdt, cdn);

        frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
        calculate_source_target_weight_total(frm)
    },
    ream_pkt_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = setConversionType(frm,cdt,cdn);
        calculateTargetWeightAndSetValues(row, conversionType, cdt, cdn);

        frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
        frappe.model.set_value(cdt, cdn, 'waste_qty', flt(row.weight_source) - flt(row.weight_target));
        frappe.model.set_value(cdt, cdn, 'balance_qty', flt(row.stock_weight_source) - flt(row.waste_qty));
        calculate_source_target_weight_total(frm);
    },

    length_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = setConversionType(frm,cdt,cdn);
        calculateTargetWeightAndSetValues(row, conversionType, cdt, cdn);
        calculate_source_target_weight_total(frm);
        frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
        target_ream_pkt(frm, cdt, cdn);
    },
    width_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (parseFloat(row.width_target) > parseFloat(row.width_source)) {
            frappe.model.set_value(cdt, cdn, 'width_target', null);
            frappe.throw(__("Target Width cannot be greater than Source Width"));
        } else {
            var conversionType = setConversionType(frm,cdt,cdn);
            calculateTargetWeightAndSetValues(row, conversionType, cdt, cdn);
            calculate_source_target_weight_total(frm);
            frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
            target_ream_pkt(frm, cdt, cdn);
        }
        if (parseFloat(row.width_target) < 1) {
            frappe.model.set_value(cdt, cdn, 'width_target', null);
            frappe.throw(__("Target Width cannot be less than 1"));
        } else {
            var conversionType = setConversionType(frm,cdt,cdn);
            calculateTargetWeightAndSetValues(row, conversionType, cdt, cdn);
            calculate_source_target_weight_total(frm);
            frappe.model.set_value(cdt, cdn, 'amount', parseFloat(row.rate * row.weight_target).toFixed(2));
            target_ream_pkt(frm, cdt, cdn);
        }
    },
    // item_code_source: function (frm, cdt, cdn) {
    //     var row = locals[cdt][cdn];
    //
    //     function check_net_total(frm) {
    //         var weight_source = 0;
    //         var weight_target = 0;
    //         $.each(frm.doc.sheet_to_sheet_conversion_items || [], function (i, d) {
    //             if (row.item_code_source == d.item_code_source) {
    //                 weight_source += flt(d.weight_source);
    //                 weight_target += flt(d.weight_target);
    //             }
    //         });
    //         if (weight_target > weight_source) {
    //             frappe.model.set_value(cdt, cdn, 'item_code_source', null);
    //             frappe.throw(__("Target Weight cannot be greater than Source Weight"));
    //         }
    //
    //     }
    //
    //     check_net_total(frm);
    //
    // },
    //         item_code_target: function (frm, cdt, cdn) {
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


