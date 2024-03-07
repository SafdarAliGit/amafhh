// Copyright (c) 2024, Tech Ventures and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Current Stock Report"] = {
	"filters": [
		{
		"fieldname": "item_code",
		"label": __("Item"),
		"fieldtype": "Link",
		"options": "Item",
		"reqd": 0
		},
		{
		"fieldname": "item_group",
		"label": __("Item Group"),
		"fieldtype": "Link",
		"options": "Item Group",
		"reqd": 0
		},
		{
		"fieldname": "warehouse",
		"label": __("Warehouse"),
		"fieldtype": "Link",
		"options": "Warehouse",
		"reqd": 0
		},
		{
			label: __("To Date"),
			fieldname: "to_date",
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		},
	]
};
