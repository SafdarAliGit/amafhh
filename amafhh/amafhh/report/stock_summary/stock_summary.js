// Copyright (c) 2024, Tech Ventures and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Summary"] = {
		"filters": [
		{
		"fieldname": "item_group",
		"label": __("Item Group"),
		"fieldtype": "Link",
		"options": "Item Group",
		"reqd": 0
		},
			{
			"fieldname": "import_file",
			"label": __("Import File"),
			"fieldtype": "Link",
			"options": "Import File",
			"reqd": 0
			},
			{
			"fieldname": "gsm",
			"label": __("GSM"),
			"fieldtype": "Data",
			"reqd": 0
			}
	]
};
