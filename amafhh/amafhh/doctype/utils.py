import frappe
from erpnext.accounts.utils import get_balance_on


@frappe.whitelist()
def get_party_type(**args):
    if not frappe.has_permission("Account"):
        frappe.msgprint("No Permission", raise_exception=1)

    account_details = frappe.db.get_value(
        "Account", args.get('account'), ["account_type"], as_dict=1
    )

    if not account_details:
        return

    if account_details.account_type == "Receivable":
        party_type = "Customer"
    elif account_details.account_type == "Payable":
        party_type = "Supplier"
    else:
        party_type = ""

    grid_values = {
        "party_type": party_type,
    }
    if not party_type:
        grid_values["party"] = ""

    return grid_values


@frappe.whitelist()
def get_account_balance(**args):
    ac_balance = {}
    company = args.get("company")
    cost_center = frappe.get_cached_value(
        "Company", company, ["cost_center"]
    )
    ac_balance['balance'] = get_balance_on(args.get('account'), args.get('posting_date'), cost_center=cost_center)
    if ac_balance:
        return ac_balance
    else:
        ac_balance['balance'] = 0
        return ac_balance

@frappe.whitelist()
def get_account_type(account_name):
    account = frappe.get_doc("Account", account_name)
    if account.is_group == 0:
        return account.account_type
    else:
        return None


# @frappe.whitelist()
# def add_crv(**args):
#     source_name = frappe.get_doc("Cash Receipt Voucher", args.get('source_name'))
#     company = frappe.defaults.get_defaults().company
#     cash_account = source_name.account
#     posting_date = source_name.posting_date
#     voucher_type = "Cash Entry"
#     crv_no = source_name.name
#     total = source_name.total
#     if len(source_name.items) > 0 and source_name.crv_status < 1:
#         je = frappe.new_doc("Journal Entry")
#         je.posting_date = posting_date
#         je.voucher_type = voucher_type
#         je.company = company
#         je.bill_no = crv_no
#         je.append("accounts", {
#             'account': cash_account,
#             'debit_in_account_currency': total,
#             'credit_in_account_currency': 0,
#         })
#         for item in source_name.items:
#             je.append("accounts", {
#                 'account': item.account,
#                 'party_type': item.party_type,
#                 'party': item.party,
#                 'debit_in_account_currency': 0,
#                 'credit_in_account_currency': item.amount,
#             })
#         je.submit()
#     else:
#         if len(source_name.items) < 1:
#             frappe.throw("No detailed rows found")
#         if source_name.crv_status > 0:
#             frappe.throw("Journal entry already created")
