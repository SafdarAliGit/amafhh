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
    var weightFactor, singleUnitWeight, totalUnitWeight;

    if (conversionType == 'REAM') {
        weightFactor = 3100;
    } else if (conversionType == 'PKT') {
        weightFactor = 15500;
    } else {
        // Adjust this part based on your requirements
        frappe.model.set_value(cdt, cdn, 'sheets', 0); // Set to a default value or handle differently
        frappe.msgprint("Please select Conversion Type");
        return;
    }

    var weightkg = (row.width * row.gsm * row.length) / weightFactor;

    if (conversionType == 'REAM') {
        weightkg *= row.ream_packets;
        singleUnitWeight = weightkg / 500 || 0;
        totalUnitWeight = singleUnitWeight * row.sheets || 0;
    } else if (conversionType == 'PKT') {
        weightkg *= row.ream_packets;
        singleUnitWeight = weightkg / 100 || 0;
        totalUnitWeight = singleUnitWeight * row.sheets || 0;
    }

    frappe.model.set_value(cdt, cdn, 'weightkg', weightkg + totalUnitWeight);
}

frappe.ui.form.on('Roll To Sheet Conversion Target', {

    // sr_no: function (frm, cdt, cdn) {
    //     var row = locals[cdt][cdn];
    //     if (row.sr_no) {
    //         frappe.call({
    //             method: 'amafhh.amafhh.doctype.utils.get_sr_no.get_sr_no',
    //
    //             args: {
    //                 sr_no: row.sr_no
    //             },
    //             callback: function (response) {
    //                 if (response.message) {
    //                     frappe.model.set_value(cdt, cdn, 'item_code', response.message.item_code);
    //                 } else {
    //                     frappe.msgprint(__('Record not found for SR No: {0}', [row.sr_no]));
    //                     frappe.model.set_value(cdt, cdn, 'item_code', '');
    //                 }
    //             }
    //         });
    //     }
    // },
    roll_to_sheet_conversion_target_add: function (frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, 'gsm', frm.fields_dict['roll_to_sheet_conversion_source'].grid.data[0].gsm);
        frappe.model.set_value(cdt, cdn, 'rate', frm.fields_dict['roll_to_sheet_conversion_source'].grid.data[0].rate);
    },
    weightkg: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weightkg);

        function calculate_net_total(frm) {
            var target_weight = 0;
            $.each(frm.doc.roll_to_sheet_conversion_target || [], function (i, d) {
                target_weight += flt(d.weightkg);
            });
            frm.set_value("target_weight", target_weight)
        }

        calculate_net_total(frm);
        var source_weight = frm.doc.source_weight || 0;
        var target_weight = frm.doc.target_weight || 0;
        if (target_weight > source_weight) {
            frappe.model.set_value(cdt, cdn, 'weightkg', null);
            frappe.throw(__("Target Weight cannot be greater than Source Weight"));
        }
    },
    rate: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.weightkg);
    },

    sheets: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateWeightAndSetValues(row, conversionType, cdt, cdn);
    },
    ream_packets: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateWeightAndSetValues(row, conversionType, cdt, cdn);
    },
    width: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateWeightAndSetValues(row, conversionType, cdt, cdn);
    },

    length: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var conversionType = frm.doc.conversion_type;
        calculateWeightAndSetValues(row, conversionType, cdt, cdn);
    }

});
