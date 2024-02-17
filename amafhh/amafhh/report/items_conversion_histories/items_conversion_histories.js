
frappe.query_reports["Items Conversion Histories"] = {
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