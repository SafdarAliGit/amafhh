// Copyright (c) 2025, Tech Ventures and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Packet Stock Balance"] = {
	"filters": [
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"reqd": 0
		},
		{
			"fieldname": "gsm",
			"label": __("GSM"),
			"fieldtype": "Data",
			"reqd": 0
		},
		{
			"fieldname": "item_category",
			"label": __("Item Category"),
			"fieldtype": "Link",
			"options": "Item Category",
			"reqd": 0
		},
		{
			"fieldname": "brand_item",
			"label": __("Brand Item"),
			"fieldtype": "Link",
			"options": "Brand",
			"reqd": 0
		},
		{
			"fieldname": "group_by",
			"label": __("Group By"),
			"fieldtype": "Select",
			"options": ["Brand", "GSM"],
			"default": "GSM"
		}
	]
};
