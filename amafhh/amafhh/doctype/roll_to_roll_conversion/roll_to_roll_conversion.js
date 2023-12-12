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
