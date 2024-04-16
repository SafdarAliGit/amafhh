import frappe


@frappe.whitelist()
def update_avg_rate(**args):
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

    # Now you can return both results
    # -------------Purchase Invoice----------------
    total_qty = 0
    total_rate = 0
    total_amount = 0
    for purchase in pi_parent_query_result:
        total_qty += purchase.qty
        total_rate += purchase.rate
        total_amount += purchase.amount
    if len(pi_parent_query_result) != 0:
        avg_rate = total_rate / len(pi_parent_query_result)
    else:
        # Handle the case where len(purchase_result) is zero
        avg_rate = 0  # or any other appropriate value
    # -------------Landed Cost Voucher----------------
    total_lc_amount = 0
    for lcr in lcv_parent_query_result:
        total_lc_amount += lcr.amount

    total_cost = total_amount + total_lc_amount
    if total_qty != 0:
        avg_rate_with_lc = total_cost / total_qty
    else:
        avg_rate = 0
    return {
        'total_qty': round(total_qty, 2),
        'avg_rate': round(avg_rate, 2),
        'total_amount': round(total_amount, 2),
        'total_lc_amount': round(total_lc_amount, 2),
        'total_cost': round(total_cost, 2),
        'avg_rate_with_lc': round(avg_rate_with_lc, 2)

    }
