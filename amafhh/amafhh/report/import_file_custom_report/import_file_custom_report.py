# my_custom_app.my_custom_app.report.daily_activity_report.daily_activity_report.py
import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "label": _("Headings"),
            "fieldname": "heading",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("<b>Date</b>"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 150
        },
        {
            "label": _("<b>Supplier</b>"),
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 100
        },
        {
            "label": _("<b>Pur. Inv#</b>"),
            "fieldname": "voucher_no",
            "fieldtype": "Link",
            "options": "Purchase Invoice",
            "width": 180
        },
        {
            "label": _("<b>Total Qty</b>"),
            "fieldname": "qty",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": _("<b>Rate</b>"),
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 180
        },

        {
            "label": _("<b>Amount</b>"),
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 200
        }

    ]
    return columns


def get_conditions(filters, doctype):
    conditions = []
    if doctype in ["pi","lcv"]:
        conditions.append(f"`{doctype}`.import_file = %(import_file)s")
    return " AND ".join(conditions)


def get_data(filters):
    data = []

    purchase = """
                SELECT
                   '' AS heading,
                    pi.posting_date,
                    pi.supplier,
                    pi.name AS voucher_no,
                    SUM(pii.qty) AS qty,
                    AVG(pii.rate) AS rate,
                    pi.grand_total AS amount
                FROM
                    `tabPurchase Invoice` AS pi
                LEFT JOIN
                    `tabPurchase Invoice Item` AS pii ON pi.name = pii.parent
                WHERE
                    {conditions} 
                    AND 
                    pi.docstatus = 1
                GROUP BY
                    pi.name
                ORDER BY
                    pi.posting_date ASC
            """.format(conditions=get_conditions(filters, "pi"))


    landed_cost = """
                SELECT
                   '' AS heading,
                    lcv.posting_date,
                    lctc.description AS qty,
                    lcv.name AS voucher_no,
                    lctc.expense_account AS supplier,
                    '' AS rate,
                    lctc.amount
                FROM
                    `tabLanded Cost Voucher` AS lcv
                LEFT JOIN
                    `tabLanded Cost Taxes and Charges` AS lctc ON lcv.name = lctc.parent
                WHERE
                    {conditions} 
                    AND 
                    lcv.docstatus = 1
                """.format(conditions=get_conditions(filters, "lcv"))

    purchase_result = frappe.db.sql(purchase, filters, as_dict=1)
    landed_cost_result = frappe.db.sql(landed_cost, filters, as_dict=1)
    #
    # ====================CALCULATING TOTAL IN PURCHASE====================
    purchase_header_dict = [{'heading': '<b><u>Purchase Detail</b></u>','posting_date': '', 'supplier': '', 'voucher_no': '', 'qty': '',
         'rate': '', 'amount': ''}]
    purchase_total_dict = {'heading': '<b>Total</b>', 'posting_date': '-------', 'supplier': '-------', 'voucher_no': '-------',
                           'qty': None, 'rate': None, ',' 'amount': None}
    total_qty = 0
    total_rate = 0
    total_amount = 0
    for purchase in purchase_result:
        total_qty += purchase.qty
        total_rate += purchase.rate
        total_amount += purchase.amount
    if len(purchase_result) != 0:
        avg_rate = total_rate / len(purchase_result)
    else:
        # Handle the case where len(purchase_result) is zero
        avg_rate = 0  # or any other appropriate value

    purchase_total_dict['qty'] = total_qty
    purchase_total_dict['rate'] = avg_rate
    purchase_total_dict['amount'] = total_amount

    purchase_result = purchase_header_dict + purchase_result
    purchase_result.append(purchase_total_dict)
    # ====================CALCULATING TOTAL IN PURCHASE END====================

    # # ====================CALCULATING TOTAL IN LANDED COST VOUCHER====================
    landed_cost_header_dict = [
        {'heading': '<b><u>Expense Detail</b></u>', 'posting_date': '-------', 'supplier': '-------',
         'voucher_no': '-------', 'qty': '-------',
         'rate': '-------', 'amount': ''},
        {'heading': '', 'posting_date': '-------', 'supplier': '<b>Account</b>',
         'voucher_no': '<b>LCV#</b>', 'qty': '<b>Description</b>',
         'rate': '-------', 'amount': ''}
    ]
    landed_cost_total_dict = {'heading': '<b>Total</b>', 'posting_date': '-------', 'supplier': '-------',
                           'voucher_no': '-------',
                           'qty': '-------', 'rate':'-------' , 'amount': None}

    total_lc_amount = 0
    for lcr in landed_cost_result:
        total_lc_amount += lcr.amount

    landed_cost_total_dict['amount'] = total_lc_amount

    landed_cost_result = landed_cost_header_dict + landed_cost_result

    # # ====================CALCULATING TOTAL IN LANDED COST VOUCHER END====================
    # SUMMARY
    total_cost = total_amount + total_lc_amount
    total_cost_summary = {'heading': '<b>Total Cost</b>', 'posting_date': '-------', 'supplier': '-------',
                              'voucher_no': '-------',
                              'qty': '-------', 'rate': '-------', ',' 'amount': None}
    total_cost_summary['amount'] = total_cost
    cost_after_expense_summary = {'heading': '<b>Cost after Expense</b>', 'posting_date': '-------', 'supplier': '-------',
                          'voucher_no': '-------',
                          'qty': '-------', 'rate': '-------', ',' 'amount': None}
    if total_qty != 0:
        cost_after_expense_summary['amount'] = total_cost / total_qty
    else:
        # Handle the case where total_qty is zero
        cost_after_expense_summary['amount'] = 0  # or any other appropriate value

    landed_cost_result.append(landed_cost_total_dict)
    landed_cost_result.append(total_cost_summary)
    landed_cost_result.append(cost_after_expense_summary)

    data.extend(purchase_result)

    data.extend(landed_cost_result)

    return data
