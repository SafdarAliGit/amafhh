// Copyright (c) 2024, Tech Ventures and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Items Conversion History"] = {
	"filters": [
		{
		"fieldname": "import_file",
		"label": __("Import File"),
		"fieldtype": "Link",
		"options": "Import File",
		"reqd": 1
		}
	]
};


