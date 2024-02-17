# my_custom_app.my_custom_app.report.daily_activity_report.daily_activity_report.py
from decimal import Decimal

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def decimal_format(value, decimals):
    formatted_value = "{:.{}f}".format(value, decimals)
    return formatted_value


def get_columns():
    columns = [
        {
            "label": _("Cut Option"),
            "fieldname": "cut_option",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 120

        },
        {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 120

        },
        {
            "label": _("Item Code"),
            "fieldname": "source_item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": _("Width"),
            "fieldname": "source_width",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Length"),
            "fieldname": "source_length",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Gsm"),
            "fieldname": "source_gsm",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Weight"),
            "fieldname": "weight_source",
            "fieldtype": "Data",
            "width": 120
        }

    ]
    return columns


def get_conditions(filters, doctype):
    conditions = []

    # if doctype == "Journal Entry":
    #     conditions.append("`tabJournal Entry`.is_opening = 0")

    return " AND ".join(conditions)


def get_data(filters):
    data = []

    RTRC_SOURCE = """
            SELECT 
              m.cut_option,
              m.posting_date,
              m.warehouse,
       		  f.item_code AS source_item_code,
       		  f.width AS source_width, 
       		  f.length AS source_length, 
       		  f.gsm AS source_gsm,
       		  f.weight_source
			FROM `tabRoll To Roll Conversion` AS m
			JOIN `tabRoll To Roll Conversion Source` AS f ON m.name = f.parent AND f.item_code = %(item_code)s
        """
    RTRC_TARGET = """
                SELECT 
                  '' AS cut_option,
                  '' AS posting_date,
                  '' AS warehouse,
                  t.item_code AS source_item_code,
                  t.width AS source_width,
                  t.length AS source_length,
                  t.gsm AS source_gsm,
                  t.weight_target AS weight_source
                FROM `tabRoll To Roll Conversion Target` AS t
                WHERE t.item_code LIKE CONCAT(%(item_code)s,'%%')
            """

    RTRC_SOURCE_result = frappe.db.sql(RTRC_SOURCE, filters, as_dict=1)
    RTRC_TARGET_result = frappe.db.sql(RTRC_TARGET, filters, as_dict=1)
    # =========================================================================
    # Roll To Roll Conversion (source)
    RTRC_SOURCE_header_dict = [
        {'cut_option': '<b><u>SLITING PROCESS</u></b>', 'posting_date': '', 'warehouse': '', 'source_item_code': '',
         'source_width': '', 'source_length': '', 'source_gsm': '', 'weight_source': ''}, ]
    RTRC_SOURCE_source_dict = [
        {'cut_option': '<b>SOURCE</b>', 'posting_date': '', 'warehouse': '', 'source_item_code': '',
         'source_width': '', 'source_length': '', 'source_gsm': '', 'weight_source': ''}, ]
    RTRC_SOURCE_result = RTRC_SOURCE_header_dict + RTRC_SOURCE_source_dict + RTRC_SOURCE_result

    # Roll To Roll Conversion (target)
    RTRC_TARGET_target_dict = [
        {'cut_option': '<b>TARGET</b>', 'posting_date': '', 'warehouse': '', 'source_item_code': '',
         'source_width': '', 'source_length': '', 'source_gsm': '', 'weight_source': ''}, ]
    RTRC_TARGET_target_sum_dict = {'cut_option': '<b>SUM</b>', 'posting_date': '', 'warehouse': '', 'source_item_code': '',
         'source_width': '', 'source_length': '', 'source_gsm': '', 'weight_source': ''}

    rtrc_total_width = 0
    rtrc_total_weight = 0
    for i in RTRC_TARGET_result:
        rtrc_total_width += Decimal(i.source_width)
        rtrc_total_weight += Decimal(i.weight_source)

    RTRC_TARGET_target_sum_dict['source_width'] = f"<b>{rtrc_total_width:.4f}</b>"
    RTRC_TARGET_target_sum_dict['weight_source'] = f"<b>{rtrc_total_weight:.4f}</b>"
    RTRC_TARGET_result = RTRC_TARGET_target_dict + RTRC_TARGET_result
    RTRC_TARGET_result.append(RTRC_TARGET_target_sum_dict)
    # ==========================================================================

    data.extend(RTRC_SOURCE_result)
    data.extend(RTRC_TARGET_result)
    return data
