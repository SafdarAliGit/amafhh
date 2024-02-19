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
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": "Width",
            "fieldname": "width",
            "fieldtype": "Data",
            "width": 120

        },
        {
            "label": "Length",
            "fieldname": "length",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "GSM",
            "fieldname": "gsm",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Qty",
            "fieldname": "qty",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Ream/Pkt",
            "fieldname": "ream_pkt",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Rate",
            "fieldname": "rate",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Amount",
            "fieldname": "amount",
            "fieldtype": "Data",
            "width": 120
        }

    ]
    return columns


def get_data(filters):
    data = []
    purchase_query = """
                    SELECT 
                      pii.import_file,
                      pii.item_code,
                      pii.width,
                      '' AS length,
               		  pii.gsm,
               		  pii.qty, 
               		  '' AS ream_pkt,
               		  pii.rate,
               		  '' AS amount
               		FROM `tabPurchase Invoice Item` AS pii
               		WHERE  pii.import_file = %(import_file)s 
               	"""
    rtrct_query = """
                    SELECT 
                      '' AS import_file,
                      rtrct.item_code,
                      rtrct.width,
                      '' AS length,
                      '' AS gsm,
                      rtrct.weight_target AS qty, 
                      '' AS ream_pkt,
                      '' AS rate,
                      '' AS amount
                    FROM `tabRoll To Roll Conversion Target` AS rtrct
                    WHERE  rtrct.import_file = %(import_file)s 
                """
    rtsci_query = """
                        SELECT 
                          '' AS import_file,
                          rtsci.item_code_target AS item_code,
                          rtsci.width_target AS width,
                          rtsci.length_target AS length,
                   		  '' AS gsm,
                   		  rtsci.weight_target AS qty, 
                   		  rtsci.ream_pkt_target AS ream_pkt,
                   		  '' AS rate,
                   		  '' AS amount
                   		FROM  `tabRoll To Sheet Conversion Items` AS rtsci
                   		WHERE  rtsci.import_file = %(import_file)s 
                   	"""
    stsci_query = """
                        SELECT 
                          '' AS import_file,
                          stsci.item_code_target AS item_code,
                          stsci.width_target AS width,
                          stsci.length_target AS length,
                          '' AS gsm,
                          stsci.weight_target AS qty, 
                          stsci.ream_pkt_target AS ream_pkt,
                          '' AS rate,
                          stsci.amount
                        FROM  `tabSheet To Sheet Conversion Items` AS stsci
                        WHERE  stsci.import_file = %(import_file)s 
                    """

    purchase_query_result = frappe.db.sql(purchase_query, filters, as_dict=1)
    rtrct_query_result = frappe.db.sql(rtrct_query, filters, as_dict=1)
    rtsci_query_result = frappe.db.sql(rtsci_query, filters, as_dict=1)
    stsci_query_result = frappe.db.sql(stsci_query, filters, as_dict=1)
    # =========================================================================
    # Roll To Roll Conversion (source)
    purchase_header_dict = [
        {'import_file': '<b><u>PURCHASE</u></b>', 'item_code': ' ', 'width': ' ',
         'gsm': ' ', 'qty': ' ', 'rate': ' '}]
    rtrct_header_dict = [
        {'import_file': '<b><u>SLITTING</u></b>', 'item_code': ' ', 'width': ' ',
         'gsm': ' ', 'qty': ' ', 'rate': ' '}]
    rtsci_header_dict = [
        {'import_file': '<b><u>REEL TO SHEET</u></b>', 'item_code': ' ', 'width': ' ',
         'gsm': ' ', 'qty': ' ', 'rate': ' '}]
    stsci_header_dict = [
        {'import_file': '<b><u>REEL TO SHEET</u></b>', 'item_code': ' ', 'width': ' ',
         'gsm': ' ', 'qty': ' ', 'rate': ' '}]

    purchase_query_result = purchase_header_dict + purchase_query_result
    rtrct_query_result = rtrct_header_dict + rtrct_query_result
    rtsci_query_result = rtsci_header_dict + rtsci_query_result
    stsci_query_result = stsci_header_dict + stsci_query_result


    data.extend(purchase_query_result)
    data.extend(rtrct_query_result)
    data.extend(rtsci_query_result)
    data.extend(stsci_query_result)
    return data
