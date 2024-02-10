frappe.query_reports["Daily Activity Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		  {
            "fieldname": "transaction_types",
            "label": __("Transaction Types"),
            "fieldtype": "Select",
            "options": ["All","Sales", "Purchases","Cash Receipt","Cash Payment","Bank Receipt","Bank Payment"],
            "default": ["All"]  // Preselecting "Sales"
        }
	]
};
