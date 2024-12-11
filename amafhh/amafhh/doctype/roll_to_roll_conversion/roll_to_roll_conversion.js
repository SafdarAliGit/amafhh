// Copyright (c) 2023, Tech Ventures and contributors
// For license information, please see license.txt

frappe.ui.form.on('Roll To Roll Conversion', {
    refresh(frm) {
        if (frm.doc.docstatus == 1 && frm.doc.non_physical_stock_entry == 0 && frm.doc.weight_difference > 0) {
            frm.add_custom_button(__('Non Physical Stock Entry'), function () {
                frm.trigger("make_non_physical_stock_entry");
            });
        }

        frm.set_query('item_code', 'roll_to_roll_conversion_source', function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                    ["Item", "item_group", "=", "Roll"],
                     ["Item", "qty", ">", 0]
                ]
            };
        });
        frm.set_query('item_code', 'roll_to_roll_conversion_target', function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                    ["Item", "item_group", "=", "Roll"],
                    ["Item", "gsm", "=", frm.fields_dict['roll_to_roll_conversion_source'].grid.data[0].gsm]
                ]
            };
        });

        frm.set_query('batch_no_source', 'roll_to_roll_conversion_source', function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [
                    ["Batch", "item_group", "=", "Roll"]
                ]
            };
        });

    },
    make_non_physical_stock_entry: function (frm) {
        if (frm.doc.roll_to_roll_conversion_source && frm.doc.roll_to_roll_conversion_source.length > 0) {
            frappe.call({
                method: 'amafhh.amafhh.doctype.utils.make_non_physical_stock_entry.make_non_physical_stock_entry',
                args: {
                    'batch_no_source': frm.doc.roll_to_roll_conversion_source[0].batch_no_source,
                    'posting_date': frm.doc.posting_date,
                    'name': frm.doc.name,
                    'source_warehouse': frm.doc.warehouse,
                    'source_item_code': frm.doc.roll_to_roll_conversion_source[0].item_code,
                    'weight_difference': frm.doc.weight_difference,
                    'rate': frm.doc.roll_to_roll_conversion_source[0].rate
                },
                callback: function (r) {
                    if (!r.exc) {
                        frappe.msgprint('Non Physical Stock Entry Created');
                    }
                }
            });
        } else {
            frappe.msgprint('Error: No roll to roll conversion source found.');
        }
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
                        frappe.model.set_value(cdt, cdn, 'item_code', response.message.item_code);
                        frappe.model.set_value(cdt, cdn, 'rate', response.message.rate);
                        frappe.model.set_value(cdt, cdn, 'amount', response.message.amount);
                        frappe.model.set_value(cdt, cdn, 'weight_source', response.message.weight_balance);
                        frappe.model.set_value(cdt, cdn, 'width', response.message.width);
                        frappe.model.set_value(cdt, cdn, 'gsm', response.message.gsm);
                        frappe.model.set_value(cdt, cdn, 'import_file', response.message.import_file);
                        frappe.model.set_value(cdt, cdn, 'length', response.message.length || 0);
                        frappe.model.set_value(cdt, cdn, 'item_category', response.message.item_category || '');
                        frappe.model.set_value(cdt, cdn, 'brand', response.message.brand || '');

                        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weight_source);
                    } else {
                        frappe.msgprint(__('Record not found for SR No: {0}', [row.batch_no_source]));
                        frappe.model.set_value(cdt, cdn, 'item_code', '');
                    }


                }
            });
        }


    },
    item_code: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        // if (row.item_code) {
        //     frappe.call({
        //         method: 'amafhh.amafhh.doctype.utils.get_by_item_code.get_by_item_code',
        //
        //         args: {
        //             item_code: row.item_code
        //         },
        //         callback: function (response) {
        //             if (response.message) {
        //                 frappe.model.set_value(cdt, cdn, 'item_code', response.message.item_code);
        //                 frappe.model.set_value(cdt, cdn, 'rate', response.message.rate);
        //                 frappe.model.set_value(cdt, cdn, 'amount', response.message.amount);
        //                 frappe.model.set_value(cdt, cdn, 'weight_source', response.message.weight_balance);
        //                 frappe.model.set_value(cdt, cdn, 'width', response.message.width);
        //                 frappe.model.set_value(cdt, cdn, 'gsm', response.message.gsm);
        //                 frappe.model.set_value(cdt, cdn, 'import_file', response.message.import_file);
        //                 frappe.model.set_value(cdt, cdn, 'length', response.message.length || 0);
        //
        //
        //             } else {
        //                 frappe.msgprint(__('Record not found for SR No: {0}', [row.batch_no_source]));
        //                 frappe.model.set_value(cdt, cdn, 'item_code', '');
        //             }
        //
        //
        //         }
        //     });
        // }

        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weight_source);
    },
    weight_source: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weight_source);

        function calculate_net_total(frm) {
            var source_weight = 0;
            $.each(frm.doc.roll_to_roll_conversion_source || [], function (i, d) {
                source_weight += flt(d.weight_source);
            });
            frm.set_value("source_weight", parseFloat(source_weight).toFixed(3))
        }

        calculate_net_total(frm);
    },
    rate: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weight_source);
    },
    item_code: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.item_code) {
            frappe.call({
                method: 'amafhh.amafhh.doctype.utils.fetch_valuation_rate.fetch_valuation_rate',

                args: {
                    item_code: row.item_code
                },
                callback: function (response) {
                    if (response.message) {
                        frappe.model.set_value(cdt, cdn, 'rate', response.message.valuation_rate);
                        frappe.model.set_value(cdt, cdn, 'weight_source', response.message.weight_balance);
                    } else {
                        frappe.msgprint(__('Valuation Rate not found for Item: {0}', [row.item_code]));
                    }


                }
            });
        }


    }

});

frappe.ui.form.on('Roll To Roll Conversion Target', {

    roll_to_roll_conversion_target_add: function (frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, 'gsm', frm.fields_dict['roll_to_roll_conversion_source'].grid.data[0].gsm);
        frappe.model.set_value(cdt, cdn, 'rate', frm.fields_dict['roll_to_roll_conversion_source'].grid.data[0].rate);
        frappe.model.set_value(cdt, cdn, 'import_file', frm.fields_dict['roll_to_roll_conversion_source'].grid.data[0].import_file);
        frappe.model.set_value(cdt, cdn, 'item_category', frm.fields_dict['roll_to_roll_conversion_source'].grid.data[0].item_category);
        frappe.model.set_value(cdt, cdn, 'brand', frm.fields_dict['roll_to_roll_conversion_source'].grid.data[0].brand);
        // ADD NEW ITEM CODE CUSTOM WORK
        // Iterate through each row in the child table
        frm.doc.roll_to_roll_conversion_target.forEach(function (item, index) {
            // Check if the item code is empty
            if (!item.item_code) {
                //     // Get the last item code in the child table
                //     var lastItemCode = frm.doc.roll_to_roll_conversion_source[0]?.item_code || '';
                // } else {
                var lastItemCode = frm.doc.roll_to_roll_conversion_target[index - 1]?.item_code || '';

                // Extract the numeric part of the last item code
                var numericPart = lastItemCode.match(/\d+$/);

                // Increment the numeric part and append it to the parent's item code
                var newItemCode = frm.fields_dict['roll_to_roll_conversion_source'].grid.data[0].item_code.toString() + '-' + (numericPart ? (parseInt(numericPart[0]) + 1) : 1);
                // Set the new item code in the current row
                if (frm.doc.generate_batch === 1) {
                    frappe.model.set_value(cdt, cdn, 'batch_no_target', newItemCode);
                }
                frappe.model.set_value(item.doctype, item.name, 'item_code', newItemCode);
            }
        });

        // END CUSTOM
    },
    weight_target: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weight_target);

        function calculate_net_total(frm) {
            var target_weight = 0;
            var weight_difference = 0;
            $.each(frm.doc.roll_to_roll_conversion_target || [], function (i, d) {
                target_weight += flt(d.weight_target);
            });
            weight_difference = frm.doc.roll_to_roll_conversion_source[0].weight_source - target_weight;
            frm.set_value("target_weight", parseFloat(target_weight).toFixed(3))
            frm.set_value("weight_difference", parseFloat(weight_difference).toFixed(3))
        }

        calculate_net_total(frm);
        var source_weight = frm.doc.source_weight || 0;
        var target_weight = frm.doc.target_weight || 0;
        if (parseFloat(target_weight) > parseFloat(source_weight)) {
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
        if (parseFloat(row.width) > frm.doc.roll_to_roll_conversion_source[0].width) {
            frappe.model.set_value(cdt, cdn, 'width', null);
            frappe.throw(__("Target Width cannot be greater than Source Width"));
        }
        if (parseFloat(row.width) < 1) {
            frappe.model.set_value(cdt, cdn, 'width', null);
            frappe.throw(__("Target Width cannot be less than 1"));
        }
        if (frm.doc.cut_option == 'Full Width') {
            var weight_target = (parseFloat(row.width) / frm.doc.roll_to_roll_conversion_source[0].width) * frm.doc.roll_to_roll_conversion_source[0].weight_source;
            frappe.model.set_value(cdt, cdn, 'weight_target', parseFloat(weight_target).toFixed(3));
        }
    },
    item_code: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.item_code) {
            frappe.call({
                method: 'amafhh.amafhh.doctype.utils.get_by_item_code.get_by_item_code',

                args: {
                    item_code: row.item_code
                },
                callback: function (response) {
                    if (response.message) {
                        frappe.model.set_value(cdt, cdn, 'width', response.message.width);
                        frappe.model.set_value(cdt, cdn, 'gsm', response.message.gsm);
                        frappe.model.set_value(cdt, cdn, 'length', response.message.length || 0);
                        if (frm.doc.generate_batch === 1) {
                            frappe.model.set_value(cdt, cdn, 'batch_no_target', row.item_code);
                        }

                        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weight_target);
                    } else {
                        frappe.msgprint(__('Record not found for Item: {0}', [row.item_code]));
                    }


                }
            });
        }


    }

});