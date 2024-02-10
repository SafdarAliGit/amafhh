# my_custom_app.my_custom_app.report.daily_activity_report.daily_activity_report.py
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
            "label": _("Voucher Type"),
            "fieldname": "voucher_type",
            "fieldtype": "Link",
            "options": "DocType",
            "width": 120
        },
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 90
        },
        {
            "label": _("Voucher No"),
            "fieldname": "voucher_no",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 120
        },
        {
            "label": _("Account"),
            "fieldname": "party",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type.party",
            "width": 180
        },
        {
            "label": _("Debit"),
            "fieldname": "debit",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Credit"),
            "fieldname": "credit",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Grand Total"),
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Against"),
            "fieldname": "against",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Remarks"),
            "fieldname": "remarks",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Sale Challan No"),
            "fieldname": "sale_challan_no",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Hub Challan No"),
            "fieldname": "hub_challan_no",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Item"),
            "fieldname": "items",
            "fieldtype": "Data",
            "width": 250
        }

    ]
    return columns


def get_conditions(filters, doctype):
    conditions = []

    if filters.get("from_date"):
        conditions.append(f"`tab{doctype}`.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append(f"`tab{doctype}`.posting_date <= %(to_date)s")

    if doctype == "Journal Entry":
        conditions.append("`tabJournal Entry`.is_opening = 0")

    return " AND ".join(conditions)


def get_account_type_from_name(account_name):
    try:
        account_doc = frappe.get_doc("Account", account_name)
        account_type = account_doc.account_type
        return account_type
    except frappe.DoesNotExistError:
        return None


def get_data(filters):
    data = []

    sale = """
            SELECT
                 `tabSales Invoice`.posting_date,
                `tabSales Invoice`.name as voucher_no,
                `tabSales Invoice`.customer as party,
                `tabSales Invoice`.total as debit,
                `tabSales Invoice`.total_taxes_and_charges,
                `tabSales Invoice`.grand_total,
                `tabSales Invoice`.sale_challan_no,
                `tabSales Invoice`.hub_challan_no,
                `tabSales Invoice`.against_income_account as against,
                GROUP_CONCAT(
                    CONCAT(
                        `tabSales Invoice Item`.item_code,
                        " : ",
                        ROUND(`tabSales Invoice Item`.qty,0),
                        " X ",
                        ROUND(`tabSales Invoice Item`.rate,2),
                        " = ",
                        ROUND(`tabSales Invoice Item`.amount,2)
                    ) SEPARATOR '<br>'
                ) AS items
            FROM
                `tabSales Invoice`
            LEFT JOIN
                `tabSales Invoice Item` ON `tabSales Invoice`.name = `tabSales Invoice Item`.parent
            WHERE
                {conditions} AND `tabSales Invoice`.docstatus = 1
            GROUP BY
                `tabSales Invoice`.name, `tabSales Invoice`.customer, `tabSales Invoice`.grand_total
            ORDER BY
                `tabSales Invoice`.posting_date ASC, `tabSales Invoice`.name ASC
        """.format(conditions=get_conditions(filters, "Sales Invoice"))

    purchase = """
                SELECT
                     `tabPurchase Invoice`.posting_date,
                    `tabPurchase Invoice`.name as voucher_no,
                    `tabPurchase Invoice`.supplier as party,
                    `tabPurchase Invoice`.total as credit,
                    `tabPurchase Invoice`.total_taxes_and_charges,
                    `tabPurchase Invoice`.grand_total,
                    `tabPurchase Invoice`.against_expense_account as against,
                    GROUP_CONCAT(
                        CONCAT(
                            `tabPurchase Invoice Item`.item_code,
                            " : ",
                            ROUND(`tabPurchase Invoice Item`.qty,0),
                            " X ",
                            ROUND(`tabPurchase Invoice Item`.rate,2),
                            " = ",
                            ROUND(`tabPurchase Invoice Item`.amount,2)
                        ) SEPARATOR '<br>'
                    ) AS items
                FROM
                    `tabPurchase Invoice`
                LEFT JOIN
                    `tabPurchase Invoice Item` ON `tabPurchase Invoice`.name = `tabPurchase Invoice Item`.parent
                WHERE
                    {conditions} AND `tabPurchase Invoice`.docstatus = 1
                GROUP BY
                    `tabPurchase Invoice`.name, `tabPurchase Invoice`.supplier, `tabPurchase Invoice`.grand_total
                ORDER BY
                    `tabPurchase Invoice`.posting_date ASC, `tabPurchase Invoice`.name ASC
            """.format(conditions=get_conditions(filters, "Purchase Invoice"))

    cash_receipt = """SELECT
                                            `tabGL Entry`.posting_date,
                                            `tabGL Entry`.account as party,
                                            `tabGL Entry`.party_type,
                                            `tabGL Entry`.voucher_no,
                                            `tabGL Entry`.debit,
                                            `tabGL Entry`.credit,
                                            `tabGL Entry`.against,
                                            `tabGL Entry`.remarks
                                        FROM
                                            `tabGL Entry`
                                        WHERE
                                            {conditions} AND `tabGL Entry`.is_cancelled = 0
                                            AND `tabGL Entry`.debit >0
                                            AND (SELECT `account_type` FROM `tabAccount` WHERE `name` = `tabGL Entry`.account) ='Cash'
                                    """.format(conditions=get_conditions(filters, "GL Entry"))

    cash_payment = """SELECT
                                    `tabGL Entry`.posting_date,
                                    `tabGL Entry`.account as party,
                                    `tabGL Entry`.party_type,
                                    `tabGL Entry`.voucher_no,
                                    `tabGL Entry`.debit,
                                    `tabGL Entry`.credit,
                                    `tabGL Entry`.against,
                                    `tabGL Entry`.remarks
                                FROM
                                    `tabGL Entry`
                                WHERE
                                    {conditions} AND `tabGL Entry`.is_cancelled = 0
                                    AND `tabGL Entry`.credit >0
                                    AND (SELECT `account_type` FROM `tabAccount` WHERE `name` = `tabGL Entry`.account) ='Cash'
                            """.format(conditions=get_conditions(filters, "GL Entry"))

    bank_receipt = """SELECT
                        `tabGL Entry`.posting_date,
                        `tabGL Entry`.account as party,
                        `tabGL Entry`.party_type,
                        `tabGL Entry`.voucher_no,
                        `tabGL Entry`.debit,
                        `tabGL Entry`.credit,
                        `tabGL Entry`.against,
                        `tabGL Entry`.remarks
                    FROM
                        `tabGL Entry`
                    WHERE
                        {conditions} AND `tabGL Entry`.is_cancelled = 0
                        AND `tabGL Entry`.debit >0
                        AND (SELECT `account_type` FROM `tabAccount` WHERE `name` = `tabGL Entry`.account) ='Bank'
                """.format(conditions=get_conditions(filters, "GL Entry"))

    bank_payment = """SELECT
                            `tabGL Entry`.posting_date,
                            `tabGL Entry`.account as party,
                            `tabGL Entry`.party_type,
                            `tabGL Entry`.voucher_no,
                            `tabGL Entry`.debit,
                            `tabGL Entry`.credit,
                            `tabGL Entry`.against,
                            `tabGL Entry`.remarks
                        FROM
                            `tabGL Entry`
                        WHERE
                            {conditions} AND `tabGL Entry`.is_cancelled = 0
                            AND `tabGL Entry`.credit >0
                            AND (SELECT `account_type` FROM `tabAccount` WHERE `name` = `tabGL Entry`.account) ='Bank'
                    """.format(conditions=get_conditions(filters, "GL Entry"))

    sale_result = frappe.db.sql(sale, filters, as_dict=1)
    purchase_result = frappe.db.sql(purchase, filters, as_dict=1)
    cash_receipt_result = frappe.db.sql(cash_receipt, filters, as_dict=1)
    cash_payment_result = frappe.db.sql(cash_payment, filters, as_dict=1)
    bank_receipt_result = frappe.db.sql(bank_receipt, filters, as_dict=1)
    bank_payment_result = frappe.db.sql(bank_payment, filters, as_dict=1)

    # ==================CALCULATING TOTAL IN SALES====================

    sales_header_dict = [
        {'voucher_type': '<b><u>Sales Invoice</u></b>', 'posting_date': '', 'voucher_no': '',
         'party': '', 'debit': '', 'credit': '',
         'grand_total': '',
         'items': ''}]
    sale_total_dict = {'voucher_type': '<b>Sum</b>', 'posting_date': '-------', 'voucher_no': '-------',
                       'party': '-------', 'debit': None, 'credit': None, 'grand_total': None,
                       'remarks': '--------------', 'items': '--------------'}
    total = 0
    total_taxes_and_charges = 0
    grand_total = 0
    for sale in sale_result:
        total += sale.debit
        total_taxes_and_charges += sale.total_taxes_and_charges
        grand_total += sale.grand_total

    sale_total_dict['debit'] = total
    sale_total_dict['total_taxes_and_charges'] = total_taxes_and_charges
    sale_total_dict['grand_total'] = grand_total
    sale_result = sales_header_dict + sale_result
    sale_result.append(sale_total_dict)  # appending a row at end of list of dicts
    # ====================CALCULATING TOTAL IN SALES END====================
    # ====================CALCULATING TOTAL IN PURCHASE====================
    purchase_header_dict = [{'voucher_type': '<b><u>Purchase Invoice</b></u>', 'posting_date': '', 'voucher_no': '',
                             'party': '', 'debit': '', 'credit': '', 'grand_total': '',
                             'items': ''}]
    purchase_total_dict = {'voucher_type': '<b>Sum</b>', 'posting_date': '-------', 'voucher_no': '-------',
                           'party': '-------', 'debit': None, 'credit': None, 'grand_total': None,
                           'remarks': '--------------', 'items': '--------------'}
    total = 0
    total_taxes_and_charges = 0
    grand_total = 0
    for purchase in purchase_result:
        total += purchase.credit
        total_taxes_and_charges += purchase.total_taxes_and_charges
        grand_total += purchase.grand_total

    purchase_total_dict['credit'] = total
    purchase_total_dict['total_taxes_and_charges'] = total_taxes_and_charges
    purchase_total_dict['grand_total'] = grand_total
    purchase_result = purchase_header_dict + purchase_result
    purchase_result.append(purchase_total_dict)  # appending a row at end of list of dicts
    # ====================CALCULATING TOTAL IN PURCHASE END====================
    # ====================CALCULATING TOTAL IN CASH RECEIVED====================
    cash_receipt_header_dict = [{'voucher_type': '<b><u>Cash Receipt</b></u>', 'posting_date': '', 'voucher_no': '',
                                 'party': '', 'debit': '', 'credit': '', 'grand_total': '',
                                 'items': ''}]
    cash_receipt_total_dict = {'voucher_type': '<b>Sum</b>', 'posting_date': '-------', 'voucher_no': '-------',
                               'party': '-------', 'debit': None, 'credit': 0, 'grand_total': 0,
                               'remarks': '--------------', 'items': '--------------'}
    total = 0
    for index, cr in enumerate(cash_receipt_result):
        total += cr.debit
        cash_receipt_result[index][
            'party'] = f"{cash_receipt_result[index]['party']}  {' / ' + cash_receipt_result[index]['party_type'] if cash_receipt_result[index]['party_type'] else ''} {' / ' + cash_receipt_result[index]['party'] if cash_receipt_result[index]['party'] else ''}"

    cash_receipt_total_dict['debit'] = total
    cash_receipt_result = cash_receipt_header_dict + cash_receipt_result
    cash_receipt_result.append(cash_receipt_total_dict)
    # ====================CALCULATING TOTAL IN CASH RECEIVED END====================

    # ====================CALCULATING TOTAL IN CASH PAID====================
    cash_payment_header_dict = [{'voucher_type': '<b><u>Cash Payment</b></u>', 'posting_date': '', 'voucher_no': '',
                                 'party': '', 'debit': '', 'credit': '', 'grand_total': '',
                                 'items': ''}]
    cash_payment_total_dict = {'voucher_type': '<b>Sum</b>', 'posting_date': '-------', 'voucher_no': '-------',
                               'party': '-------', 'debit': None, 'credit': 0, 'grand_total': 0,
                               'remarks': '--------------', 'items': '--------------'}
    total = 0
    for index, cr in enumerate(cash_payment_result):
        total += cr.credit
        cash_payment_result[index][
            'party'] = f"{cash_payment_result[index]['party']}  {' / ' + cash_payment_result[index]['party_type'] if cash_payment_result[index]['party_type'] else ''} {' / ' + cash_payment_result[index]['party'] if cash_payment_result[index]['party'] else ''}"

    cash_payment_total_dict['credit'] = total
    cash_payment_result = cash_payment_header_dict + cash_payment_result
    cash_payment_result.append(cash_payment_total_dict)
    # ====================CALCULATING TOTAL IN CASH PAID END====================
    # ====================CALCULATING TOTAL IN BANK RECEIVED====================
    bank_receipt_header_dict = [{'voucher_type': '<b><u>Bank Received</b></u>', 'posting_date': '', 'voucher_no': '',
                                 'party': '', 'debit': '', 'credit': '', 'grand_total': '',
                                 'items': ''}]
    bank_receipt_total_dict = {'voucher_type': '<b>Sum</b>', 'posting_date': '-------', 'voucher_no': '-------',
                               'party': '-------', 'debit': None, 'credit': 0, 'grand_total': 0,
                               'remarks': '--------------', 'items': '--------------'}
    total = 0
    for index, cr in enumerate(bank_receipt_result):
        total += cr.debit
        bank_receipt_result[index][
            'party'] = f"{bank_receipt_result[index]['party']}  {' / ' + bank_receipt_result[index]['party_type'] if bank_receipt_result[index]['party_type'] else ''} {' / ' + bank_receipt_result[index]['party'] if bank_receipt_result[index]['party'] else ''}"

    bank_receipt_total_dict['debit'] = total
    bank_receipt_result = bank_receipt_header_dict + bank_receipt_result
    bank_receipt_result.append(bank_receipt_total_dict)
    # ====================CALCULATING TOTAL IN BANK RECEIVED END====================

    # ====================CALCULATING TOTAL IN BANK PAID====================
    bank_payment_header_dict = [{'voucher_type': '<b><u>Bank Payment</b></u>', 'posting_date': '', 'voucher_no': '',
                                 'party': '', 'debit': '', 'credit': '', 'grand_total': '',
                                 'items': ''}]
    bank_payment_total_dict = {'voucher_type': '<b>Sum</b>', 'posting_date': '-------', 'voucher_no': '-------',
                               'party': '-------', 'debit': None, 'credit': 0, 'grand_total': 0,
                               'remarks': '--------------', 'items': '--------------'}
    total = 0
    for index, cr in enumerate(bank_payment_result):
        total += cr.credit
        bank_payment_result[index][
            'party'] = f"{bank_payment_result[index]['party']}  {' / ' + bank_payment_result[index]['party_type'] if bank_payment_result[index]['party_type'] else ''} {' / ' + bank_payment_result[index]['party'] if bank_payment_result[index]['party'] else ''}"

    bank_payment_total_dict['credit'] = total
    bank_payment_result = bank_payment_header_dict + bank_payment_result
    bank_payment_result.append(bank_payment_total_dict)
    # ====================CALCULATING TOTAL IN BANK PAID END====================
    #
    # ====================TRANSACTION TYPE FILTER====================
    if filters.get('transaction_types') == "All":
        data.extend(sale_result)
        data.extend(purchase_result)
        data.extend(cash_receipt_result)
        data.extend(cash_payment_result)
        data.extend(bank_receipt_result)
        data.extend(bank_payment_result)
    if 'Sales' in filters.get('transaction_types'):
        data.extend(sale_result)
    if 'Purchases' in filters.get('transaction_types'):
        data.extend(purchase_result)
    if 'Cash Receipt' in filters.get('transaction_types'):
        data.extend(cash_receipt_result)
    if 'Cash Payment' in filters.get('transaction_types'):
        data.extend(cash_payment_result)
    if 'Bank Receipt' in filters.get('transaction_types'):
        data.extend(bank_receipt_result)
    if 'Bank Payment' in filters.get('transaction_types'):
        data.extend(bank_payment_result)
        # ====================FILTERS END====================

    return data
