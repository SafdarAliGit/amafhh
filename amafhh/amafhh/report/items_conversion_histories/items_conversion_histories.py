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
            "label": "<b>ITEM CODE</b>",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": "<b>WIDTH</b>",
            "fieldname": "width",
            "fieldtype": "Data",
            "width": 120

        },
        {
            "label": "<b>LENGTH</b>",
            "fieldname": "length",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>GSM</b>",
            "fieldname": "gsm",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>QTY</b>",
            "fieldname": "qty",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>REAM/PKT</b>",
            "fieldname": "ream_pkt",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>RATE</b>",
            "fieldname": "rate",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>AMOUNT</b>",
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
               		ORDER BY pii.item_code
               	"""
    rtrct_query = """
                    SELECT 
                      '' AS import_file,
                      rtrct.item_code,
                      rtrct.width,
                      '' AS length,
                      '' AS gsm,
                      ROUND(rtrct.weight_target, 4) AS qty, 
                      '' AS ream_pkt,
                      '' AS rate,
                      '' AS amount
                    FROM `tabRoll To Roll Conversion Target` AS rtrct
                    WHERE  rtrct.import_file = %(import_file)s 
                    ORDER BY rtrct.item_code
                """
    rtsci_query = """
                        SELECT 
                          '' AS import_file,
                          rtsci.item_code_target AS item_code,
                          rtsci.width_target AS width,
                          rtsci.length_target AS length,
                   		  '' AS gsm,
                   		  ROUND(rtsci.weight_target, 4) AS qty, 
                   		  rtsci.ream_pkt_target AS ream_pkt,
                   		  '' AS rate,
                   		  '' AS amount
                   		FROM  `tabRoll To Sheet Conversion Items` AS rtsci
                   		WHERE  rtsci.import_file = %(import_file)s 
                   		ORDER BY rtsci.item_code_target
                   	"""
    stsci_query = """
                        SELECT 
                          '' AS import_file,
                          stsci.item_code_target AS item_code,
                          stsci.width_target AS width,
                          stsci.length_target AS length,
                          '' AS gsm,
                          ROUND(stsci.weight_target, 4) AS qty, 
                          stsci.ream_pkt_target AS ream_pkt,
                          '' AS rate,
                          stsci.amount
                        FROM  `tabSheet To Sheet Conversion Items` AS stsci
                        WHERE  stsci.import_file = %(import_file)s 
                        ORDER BY stsci.item_code_target
                    """
    sale_query = """
                        SELECT 
                          sii.import_file,
                          sii.item_code,
                          sii.width,
                          '' AS length,
                   		  sii.gsm,
                   		  sii.qty, 
                   		  '' AS ream_pkt,
                   		  sii.rate,
                   		  '' AS amount
                   		FROM `tabSales Invoice Item` AS sii
                   		WHERE  sii.import_file = %(import_file)s 
                   		ORDER BY sii.item_code
                   	"""
    purchase_query_result = frappe.db.sql(purchase_query, filters, as_dict=1)
    rtrct_query_result = frappe.db.sql(rtrct_query, filters, as_dict=1)
    rtsci_query_result = frappe.db.sql(rtsci_query, filters, as_dict=1)
    stsci_query_result = frappe.db.sql(stsci_query, filters, as_dict=1)
    sale_query_result = frappe.db.sql(sale_query, filters, as_dict=1)
    # ============================SUM PURCHASES=========================================
    purchase_sum_dict = [
        {'import_file': '<b>TOTAL =></b>', 'item_code': ' ', 'width': ' ',
         'gsm': ' ', 'qty': ' ', 'rate': ' '}]
    total_purchase_qty = 0
    for i in purchase_query_result:
        total_purchase_qty += Decimal(i.qty) if i.qty else 0
    purchase_sum_dict[0]['qty'] = f"<b>{total_purchase_qty:.4f}</b>" if total_purchase_qty else 0
    # ============================SUM ROLL TO ROLL=========================================
    rtrct_sum_dict = [
        {'import_file': '<b>TOTAL =></b>', 'item_code': ' ', 'width': ' ',
         'gsm': ' ', 'qty': ' ', 'rate': ' '}]
    total_rtrct_qty = 0
    for i in rtrct_query_result:
        total_rtrct_qty += Decimal(i.qty) if i.qty else 0
    rtrct_sum_dict[0]['qty'] = f"<b>{total_rtrct_qty:.4f}</b>" if total_rtrct_qty else 0
    # ============================SUM REEL TO SHEET=========================================
    rtsci_sum_dict = [
        {'import_file': '<b>TOTAL =></b>', 'item_code': ' ', 'width': ' ',
         'gsm': ' ', 'qty': ' ', 'rate': ' '}]
    total_rtsci_qty = 0
    for i in rtsci_query_result:
        total_rtsci_qty += Decimal(i.qty) if i.qty else 0
    rtsci_sum_dict[0]['qty'] = f"<b>{total_rtsci_qty:.4f}</b>" if total_rtsci_qty else 0
    # ============================SUM SHEET TO SHEET=========================================
    stsci_sum_dict = [
        {'import_file': '<b>TOTAL =></b>', 'item_code': ' ', 'width': ' ',
         'gsm': ' ', 'qty': ' ', 'rate': ' '}]
    total_stsci_qty =0
    for i in stsci_query_result:
        total_stsci_qty += Decimal(i.qty) if i.qty else 0
    stsci_sum_dict[0]['qty'] = f"<b>{total_stsci_qty:.4f}</b>" if total_stsci_qty else 0
    # ============================SUM SALE=========================================
    sale_sum_dict = [
        {'import_file': '<b>TOTAL =></b>', 'item_code': ' ', 'width': ' ',
         'gsm': ' ', 'qty': ' ', 'rate': ' '}]
    total_sale_qty = 0
    for i in sale_query_result:
        total_sale_qty += Decimal(i.qty) if i.qty else 0
    sale_sum_dict[0]['qty'] = f"<b>{total_sale_qty:.4f}</b>" if total_sale_qty else 0

    # =========================================================================
    # Roll To Roll Conversion (source)
    purchase_header_dict = [
        {'import_file': '<b>PURCHASE</b>', 'item_code': ' ', 'width': ' ',
         'gsm': ' ', 'qty': ' ', 'rate': ' '}]
    rtrct_header_dict = [
        {'import_file': '<b>SLITTING</b>', 'item_code': ' ', 'width': ' ',
         'gsm': ' ', 'qty': ' ', 'rate': ' '}]
    rtsci_header_dict = [
        {'import_file': '<b>REEL TO SHEET</b>', 'item_code': ' ', 'width': ' ',
         'gsm': ' ', 'qty': ' ', 'rate': ' '}]
    stsci_header_dict = [
        {'import_file': '<b>SHEET TO SHEET</b>', 'item_code': ' ', 'width': ' ',
         'gsm': ' ', 'qty': ' ', 'rate': ' '}]
    sale_header_dict = [
        {'import_file': '<b>SALE</b>', 'item_code': ' ', 'width': ' ',
         'gsm': ' ', 'qty': ' ', 'rate': ' '}]

    purchase_query_result = purchase_header_dict + purchase_query_result + purchase_sum_dict
    rtrct_query_result = rtrct_header_dict + rtrct_query_result + rtrct_sum_dict
    rtsci_query_result = rtsci_header_dict + rtsci_query_result + rtsci_sum_dict
    stsci_query_result = stsci_header_dict + stsci_query_result + stsci_sum_dict
    sale_query_result = sale_header_dict + sale_query_result + sale_sum_dict

    data.extend(purchase_query_result)
    data.extend(rtrct_query_result)
    data.extend(rtsci_query_result)
    data.extend(stsci_query_result)
    data.extend(sale_query_result)
    return data
