
frappe.query_reports["PKTS WITHOUT RATE"] = {
    "filters": [
        {
            "fieldname": "brand_item",
            "label": __("Product"),
            "fieldtype": "Link",
            "options": "Brand"
        },
        {
            "fieldname": "import_file",
            "label": __("Lc No"),
            "fieldtype": "Link",
            "options": "Import File"
        },
        {
            "fieldname": "item_code",
            "label": __("Serial No"),
            "fieldtype": "Link",
            "options": "Item"
        },
        {
            "fieldname": "warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 1
        }
    ]
};
