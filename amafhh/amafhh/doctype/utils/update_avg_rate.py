import frappe


@frappe.whitelist()
def update_avg_rate(**args):
    # -----------START-------
    import_file = args.get('import_file')
    pi = frappe.qb.DocType("Purchase Invoice")
    pii = frappe.qb.DocType("Purchase Invoice Item")
    pi_parent_query = (
        frappe.qb.from_(pi)
        .select(
            pi.posting_date,
            pi.supplier,
            pi.name.as_("voucher_no"),
            frappe.qb.functions("SUM", pii.qty).as_("qty"),
            frappe.qb.functions("AVG", pii.rate).as_("rate"),
            pi.grand_total.as_("amount")
        )
        .left_join(pii).on(pi.name == pii.parent)
        .where((pi.docstatus == 1) & (pi.import_file == import_file))
        .groupby(pi.name)
        .orderby(pi.posting_date)
    )
    pi_parent_query_result = pi_parent_query.run(as_dict=True)

    si = frappe.qb.DocType("Sales Invoice")
    sii = frappe.qb.DocType("Sales Invoice Item")
    si_parent_query = (
        frappe.qb.from_(si)
        .select(
            si.posting_date,
            si.customer,
            si.name.as_("voucher_no"),
            frappe.qb.functions("SUM", sii.qty).as_("qty")
        )
        .left_join(sii).on(si.name == sii.parent)
        .where((si.docstatus == 1) & (si.import_file == import_file))
        .groupby(si.name)
        .orderby(si.posting_date)
    )
    si_parent_query_result = si_parent_query.run(as_dict=True)

    lcv = frappe.qb.DocType("Landed Cost Voucher")
    lctc = frappe.qb.DocType("Landed Cost Taxes and Charges")
    lcv_parent_query = (
        frappe.qb.from_(lcv)
        .select(
            lcv.posting_date,
            lctc.description.as_("qty"),
            lcv.name.as_("voucher_no"),
            lctc.expense_account.as_("supplier"),
            lctc.amount
        )
        .left_join(lctc).on(lcv.name == lctc.parent)
        .where((lcv.docstatus == 1) & (lcv.import_file == import_file))
    )

    lcv_parent_query_result = lcv_parent_query.run(as_dict=True)

    # -------------Purchase Invoice----------------
    total_purchase_qty = 0
    total_rate = 0
    total_purchase_amount = 0
    for purchase in pi_parent_query_result:
        total_purchase_qty += purchase.qty
        total_rate += purchase.rate
        total_purchase_amount += purchase.amount

    avg_purchase_rate = total_rate / len(pi_parent_query_result) if pi_parent_query_result else 0
    # -------------Sales Invoice----------------
    total_sales_qty = 0
    for sale in si_parent_query_result:
        total_sales_qty += sale.qty

    # -------------Stock Balances----------------
    item_codes = frappe.get_all("Item", filters={"import_file": import_file}, pluck="name")

    balance_stock = frappe.get_all(
        "Stock Ledger Entry",
        filters={"item_code": ("in", item_codes)},
        fields=["qty_after_transaction"],
        order_by="name desc",
        limit=1
    )
    total_balance_qty = 0
    for stock in balance_stock:
        total_balance_qty += stock.qty_after_transaction
    # -------------Landed Cost Voucher----------------
    total_lc_amount = sum(lcr.amount for lcr in lcv_parent_query_result)

    total_cost = total_purchase_amount + total_lc_amount
    avg_rate_with_lc = total_cost / total_purchase_qty if total_purchase_qty != 0 else 0

    balance_stock_value = total_balance_qty * avg_rate_with_lc
    cogs = total_cost - balance_stock_value

    return {
        'total_purchase_qty': round(total_purchase_qty, 2),
        'total_sales_qty': round(total_sales_qty, 2),
        'total_balance_qty': round(total_balance_qty, 2),
        'avg_purchase_rate': round(avg_purchase_rate, 2),
        'total_purchase_amount': round(total_purchase_amount, 2),
        'total_lc_amount': round(total_lc_amount, 2),
        'total_cost': round(total_cost, 2),
        'avg_rate_with_lc': round(avg_rate_with_lc, 2),
        'balance_stock_value': round(balance_stock_value, 2),
        'cogs': round(cogs, 2)
    }

    # ----------END----------
