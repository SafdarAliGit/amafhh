# my_custom_app.my_custom_app.report.daily_activity_report.daily_activity_report.py
from decimal import Decimal

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "label": "<b>IMPORT FILE</b>",
            "fieldname": "import_file",
            "fieldtype": "Link",
            "options": "Import File",
            "width": 120
        },

        {
            "label": "<b>SUPPLIERS</b>",
            "fieldname": "suppliers",
            "fieldtype": "Data",
            "width": 250
        },

        {
            "label": "<b>AMOUNT</b>",
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "width": 120
        },

        {
            "label": "<b>QTY</b>",
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": "<b>RATE</b>",
            "fieldname": "rate",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": "<b>EXPENSE ACCOUNTS</b>",
            "fieldname": "expense_accounts",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "<b>EXPENSE AMOUNT</b>",
            "fieldname": "expense_amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "<b>COST RATE</b>",
            "fieldname": "cost_rate",
            "fieldtype": "Currency",
            "width": 120
        }

    ]
    return columns


def get_conditions(filters):
    conditions = []
    if filters.get("import_file"):
        conditions.append(f"AND lcv.import_file = '{filters.get('import_file')}'")
    if conditions:
        return " AND ".join(conditions)
    else:
        return ""


def get_data(filters):
    data = []
    conditions = get_conditions(filters)
    lcv_query = f"""
    SELECT 
        lcv.import_file,
        GROUP_CONCAT(
            DISTINCT CONCAT(
                lcvr.supplier
            ) 
        ) AS suppliers,
        SUM(lci.amount) AS grand_total,
        SUM(lci.qty) AS qty,
        AVG(lci.rate) AS rate,
        GROUP_CONCAT(
           DISTINCT CONCAT(
                lctc.expense_account
            ) 
        ) AS expense_accounts,
        sum(lctc.amount) AS expense_amount,
        (SUM(lci.amount) + sum(lctc.amount))/SUM(lci.qty) AS cost_rate
    FROM `tabLanded Cost Voucher` AS lcv
    JOIN `tabLanded Cost Purchase Receipt` AS lcvr ON lcv.name = lcvr.parent
    JOIN `tabLanded Cost Item` AS lci ON lcv.name = lci.parent AND lcvr.idx = lci.idx
    JOIN `tabLanded Cost Taxes and Charges` AS lctc ON lcv.name = lctc.parent
    WHERE
        lcv.docstatus = 1 
        AND lcv.import_file IS NOT NULL
        {conditions} 
    GROUP BY
        lcv.import_file
    ORDER BY
        lcv.import_file
    """
    lcv_result = frappe.db.sql(lcv_query, filters, as_dict=True)
    data.extend(lcv_result)
    return data

