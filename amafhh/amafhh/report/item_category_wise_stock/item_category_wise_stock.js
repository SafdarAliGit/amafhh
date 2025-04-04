

    frappe.query_reports["ITEM CATEGORY WISE STOCK"] = {
        "filters": [
            {
                "fieldname": "brand_item",
                "label": __("Product"),
                "fieldtype": "Link",
                "options": "Brand"
            },
            
            {
                "fieldname": "item_code",
                "label": __("Serial No"),
                "fieldtype": "Link",
                "options": "Item"
            },
            {
                "fieldname": "to_date",
                "label": __("To Date"),
                "fieldtype": "Date",
                "reqd": 1
            },
            {
                "fieldname": "stock_limit",
                "label": __("Stock Limit"),
                "fieldtype": "Int",
                "default": 10
            }
        ]
    };
    