// Copyright (c) 2025, Tech Ventures and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Stock Report By Category"] = {
    "filters": [

        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "width": "80",
            "reqd": 1,
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "width": "80",
            "reqd": 1,
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Link",
            "width": "80",
            "options": "Warehouse"
        },
    ]
}
