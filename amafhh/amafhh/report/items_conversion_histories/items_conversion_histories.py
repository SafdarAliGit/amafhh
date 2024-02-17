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
            "label": "Import File",
            "fieldname": "import_file",
            "fieldtype": "Link",
            "options": "Import File",
            "width": 120
        },

        {
            "label": "Item Code",
            "fieldname": "sale_item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": "Width",
            "fieldname": "sale_width",
            "fieldtype": "Data",
            "width": 120

        },
        {
            "label": "GSM",
            "fieldname": "sale_gsm",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Qty",
            "fieldname": "sale_qty",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Rate",
            "fieldname": "sale_rate",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Item Code",
            "fieldname": "rtrct_item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": "Width",
            "fieldname": "rtrct_width",
            "fieldtype": "Data",
            "width": 120
        },

        {
        "label": "Qty",
            "fieldname": "rtrct_weight_target",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Item Code",
            "fieldname": "rtsci_item_code_target",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": "Width",
            "fieldname": "rtsci_width_target",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Length",
            "fieldname": "rtsci_length_target",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Qty",
            "fieldname": "rtsci_weight_target",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "RM/PKT",
            "fieldname": "rtsci_ream_pkt_target",
            "fieldtype": "Data",
            "width": 120
        }
        ,
        {
            "label": "Item Code",
            "fieldname": "stsci_item_code_target",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": "Width",
            "fieldname": "stsci_width_target",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Length",
            "fieldname": "stsci_length_target",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Qty",
            "fieldname": "stsci_weight_target",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "RM/PKT",
            "fieldname": "stsci_ream_pkt_target",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Rate",
            "fieldname": "stsci_rate",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Amount",
            "fieldname": "stsci_amount",
            "fieldtype": "Data",
            "width": 120
        }


    ]
    return columns



def get_data(filters):
    data = []

    conversion_query = """
                SELECT 
                  pii.import_file,
                  pii.item_code AS sale_item_code,
                  pii.width AS sale_width,
           		  pii.gsm AS sale_gsm,
           		  pii.qty AS sale_qty, 
           		  pii.rate AS sale_rate,
           		  rtrct.item_code AS rtrct_item_code,
           		  rtrct.width AS rtrct_width,
           		  rtrct.weight_target AS rtrct_weight_target,
           		  rtsci.item_code_target AS rtsci_item_code_target,
           		  rtsci.width_target AS rtsci_width_target,
           		  rtsci.length_target AS rtsci_length_target,
           		  rtsci.weight_target AS rtsci_weight_target,
           		  rtsci.ream_pkt_target AS rtsci_ream_pkt_target,
           		  stsci.item_code_target AS stsci_item_code_target,
           		  stsci.width_target AS stsci_width_target,
           		  stsci.length_target AS stsci_length_target,
           		  stsci.weight_target AS stsci_weight_target,
           		  stsci.ream_pkt_target AS stsci_ream_pkt_target,
           		  stsci.rate AS stsci_rate,
           		  stsci.amount AS stsci_amount
    			FROM `tabPurchase Invoice Item` AS pii
                LEFT JOIN `tabRoll To Roll Conversion Target` AS rtrct ON pii.import_file = rtrct.import_file
                LEFT JOIN `tabRoll To Sheet Conversion Items` AS rtsci ON rtrct.import_file = rtsci.import_file
                LEFT JOIN `tabSheet To Sheet Conversion Items` AS stsci ON rtsci.import_file = stsci.import_file
                WHERE  pii.import_file = %(import_file)s 
            """
    conversion_query_result = frappe.db.sql(conversion_query, filters, as_dict=1)
    # =========================================================================
    # Roll To Roll Conversion (source)
    conversion_header_dict = [
        {'import_file': '<--------------', 'sale_item_code': '--------------', 'sale_width': '<sapan style="color:green"><b>PURCHASE</b></span>', 'sale_gsm': '--------------',
         'sale_qty': '--------------', 'sale_rate': '-------------->', 'rtrct_item_code': '<--------------', 'rtrct_width': '<sapan style="color:blue"><b>SLITTING</b></span>',
         'rtrct_weight_target': '-------------->','rtsci_item_code_target':'<--------------', 'rtsci_width_target':'--------------',
         'rtsci_length_target':'<sapan style="color:orange"><b>REEL TO SHEET</b></span>', 'rtsci_weight_target':'--------------', 'rtsci_ream_pkt_target':'-------------->',
           'stsci_item_code_target':'<--------------', 'stsci_width_target':'--------------', 'stsci_length_target':'--------------', 'stsci_weight_target':'<sapan style="color:red"><b>SHEET TO SHEET</b></span>', 'stsci_ream_pkt_target':'--------------', 'stsci_rate':'--------------', 'stsci_amount':'-------------->'} ]

    conversion_query_result = conversion_header_dict + conversion_query_result

    # # ==================first duplication removal=============================
    # keys_to_check = ['import_file', 'sale_item_code', 'sale_width', 'sale_gsm', 'sale_qty', 'sale_rate' ]
    # seen_values = []
    #
    # for entry in conversion_query_result:
    #     key_values = tuple(entry[key] for key in keys_to_check)
    #
    #     if key_values in seen_values:
    #         for key in keys_to_check:
    #             entry[key] = None
    #     else:
    #         seen_values.append(key_values)
    #
    # # ==================second duplication removal=============================
    # keys_to_check = ['rtrct_item_code', 'rtrct_width', 'rtrct_weight_target']
    # seen_values = []
    #
    # for entry in conversion_query_result:
    #     key_values = tuple(entry[key] for key in keys_to_check)
    #
    #     if key_values in seen_values:
    #         for key in keys_to_check:
    #             entry[key] = None
    #     else:
    #         seen_values.append(key_values)
    #
    # # ==================third duplication removal=============================
    keys_to_check = ['rtsci_item_code_target', 'rtsci_width_target', 'rtsci_length_target', 'rtsci_weight_target','rtsci_ream_pkt_target']
    seen_values = []

    for entry in conversion_query_result:
        key_values = tuple(entry[key] for key in keys_to_check)

        if key_values in seen_values:
            for key in keys_to_check:
                entry[key] = None
        else:
            seen_values.append(key_values)
    #     # ==================fourth duplication removal=============================
    keys_to_check = ['stsci_item_code_target', 'stsci_width_target', 'stsci_length_target', 'stsci_weight_target',
                     'stsci_ream_pkt_target', 'stsci_rate', 'stsci_amount']
    seen_values = []

    for entry in conversion_query_result:
        key_values = tuple(entry[key] for key in keys_to_check)

        if key_values in seen_values:
            for key in keys_to_check:
                entry[key] = None
        else:
            seen_values.append(key_values)

    # END
    data.extend(conversion_query_result)
    return data
