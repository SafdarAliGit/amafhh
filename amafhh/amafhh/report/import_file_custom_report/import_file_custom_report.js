

frappe.query_reports["Import File Custom Report"] = {
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
